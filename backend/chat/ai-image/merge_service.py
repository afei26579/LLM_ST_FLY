"""
AI图像融合服务
使用 qwen-image-edit 模型实现多图融合
"""
import os
import logging
import base64
import uuid
from typing import Dict, Any, List
from http import HTTPStatus
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.utils import timezone
from django.db import transaction
import dashscope
from dashscope import MultiModalConversation
import requests
from .models import ImageGenerationTask, GeneratedImage

logger = logging.getLogger(__name__)


class ImageMergeService:
    """图像融合服务类"""
    
    def __init__(self):
        dashscope.api_key = settings.DASHSCOPE_API_KEY
        # 设置为中国（北京）地域
        dashscope.base_http_api_url = 'https://dashscope.aliyuncs.com/api/v1'
    
    @transaction.atomic
    def merge_images(self, images_base64: List[str], prompt: str, user_id: int = None) -> Dict[str, Any]:
        """
        多图融合
        
        Args:
            images_base64: base64编码的图片列表（1-3张）
            prompt: 融合描述
            user_id: 用户ID
            
        Returns:
            融合结果
        """
        task = None
        try:
            if not images_base64 or len(images_base64) < 2:
                raise ValueError("至少需要2张图片")
            
            if len(images_base64) > 3:
                raise ValueError("最多支持3张图片")
            
            logger.info(f"开始融合图片，用户ID: {user_id}, 图片数量: {len(images_base64)}")
            
            # 创建任务记录
            task_id = str(uuid.uuid4())
            if user_id:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                user = User.objects.get(id=user_id)
                
                task = ImageGenerationTask.objects.create(
                    user=user,
                    task_id=task_id,
                    prompt=prompt,
                    size='merged',  # 特殊标记表示融合图片
                    n=1,
                    status='processing',
                    prompt_extend=False,
                    watermark=False
                )
            
            # 构建 messages
            content = []
            
            # 添加图片
            for img_base64 in images_base64:
                content.append({"image": img_base64})
            
            # 添加文字描述
            content.append({"text": prompt})
            
            messages = [
                {
                    "role": "user",
                    "content": content
                }
            ]
            
            # 调用 qwen-image-edit 模型
            response = MultiModalConversation.call(
                model="qwen-image-edit",
                messages=messages,
                stream=False,
                watermark=False,
                negative_prompt=" "
            )
            
            if response.status_code == HTTPStatus.OK:
                # 提取生成的图片URL
                image_url = response.output.choices[0].message.content[0]['image']
                logger.info(f"图片融合成功，URL: {image_url}")
                
                # 下载并保存图片
                saved_info = self._download_and_save_image(image_url, user_id)
                
                # 更新任务状态并保存到数据库
                if task:
                    task.status = 'completed'
                    task.completed_at = timezone.now()
                    task.save()
                    
                    # 保存生成的图片记录
                    GeneratedImage.objects.create(
                        task=task,
                        image_source='image_edit',  # 标记为图像编辑生成
                        original_url=image_url,
                        saved_path=saved_info['saved_path'],
                        saved_url=saved_info['saved_url'],
                        filename=saved_info['filename'],
                        file_size=saved_info['size'],
                        orig_prompt=prompt,
                        download_time=timezone.now(),
                        is_downloaded=True
                    )
                    
                    logger.info(f"融合图片已保存到数据库，任务ID: {task_id}")
                
                return {
                    'merged_image_url': saved_info['saved_url'],
                    'original_url': image_url,
                    'filename': saved_info['filename'],
                    'size': saved_info['size'],
                    'task_id': task_id
                }
            else:
                if task:
                    task.status = 'failed'
                    task.error_message = f"{response.code} - {response.message}"
                    task.save()
                
                error_msg = f"融合失败: {response.code} - {response.message}"
                logger.error(error_msg)
                raise Exception(error_msg)
                
        except Exception as e:
            if task:
                task.status = 'failed'
                task.error_message = str(e)
                task.save()
            
            logger.error(f"多图融合失败: {str(e)}")
            raise
    
    def _download_and_save_image(self, image_url: str, user_id: int = None) -> Dict[str, Any]:
        """下载并保存图片"""
        try:
            # 下载图片
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            
            # 生成文件名
            filename = f"merged_{uuid.uuid4().hex[:12]}.png"
            
            # 构建保存路径
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d')
            if user_id:
                save_path = f"ai-images/{user_id}/{timestamp}/{filename}"
            else:
                save_path = f"ai-images/anonymous/{timestamp}/{filename}"
            
            # 保存图片
            saved_path = default_storage.save(
                save_path, 
                ContentFile(response.content)
            )
            
            # 生成访问URL
            if hasattr(default_storage, 'url'):
                saved_url = default_storage.url(saved_path)
            else:
                saved_url = f"/media/{saved_path}"
            
            # 确保返回完整URL
            if saved_url.startswith('/'):
                base_url = getattr(settings, 'BASE_URL', 'http://localhost:8000')
                saved_url = f"{base_url}{saved_url}"
            
            logger.info(f"融合图片保存成功: {saved_path}")
            
            return {
                'saved_path': saved_path,
                'saved_url': saved_url,
                'filename': filename,
                'size': len(response.content)
            }
            
        except Exception as e:
            logger.error(f"保存融合图片失败: {str(e)}")
            raise


# 创建服务实例
image_merge_service = ImageMergeService()

