"""
背景编辑服务
使用 qwen-image-edit 模型实现背景更换
"""
import os
import logging
import uuid
from typing import Dict, Any
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


class BackgroundEditService:
    """背景编辑服务类"""
    
    def __init__(self):
        dashscope.api_key = settings.DASHSCOPE_API_KEY
        # 设置为中国（北京）地域
        dashscope.base_http_api_url = 'https://dashscope.aliyuncs.com/api/v1'
    
    @transaction.atomic
    def change_background(self, image_base64: str, prompt: str, user_id: int = None) -> Dict[str, Any]:
        """
        更换背景
        
        Args:
            image_base64: base64编码的图片
            prompt: 背景描述
            user_id: 用户ID
            
        Returns:
            编辑结果
        """
        task = None
        try:
            logger.info(f"开始更换背景，用户ID: {user_id}, 描述: {prompt[:50]}...")
            
            # 创建任务记录
            task_id = str(uuid.uuid4())
            if user_id:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                user = User.objects.get(id=user_id)
                
                task = ImageGenerationTask.objects.create(
                    user=user,
                    task_id=task_id,
                    prompt=f'背景更换：{prompt}',
                    size='background_edit',
                    n=1,
                    status='processing',
                    prompt_extend=False,
                    watermark=False
                )
            
            # 构建 messages - 单图+文字描述
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"image": image_base64},
                        {"text": prompt}
                    ]
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
                logger.info(f"背景更换成功，URL: {image_url}")
                
                # 下载并保存图片
                saved_info = self._download_and_save_image(image_url, user_id, 'background')
                
                # 更新任务状态并保存到数据库
                if task:
                    task.status = 'completed'
                    task.completed_at = timezone.now()
                    task.save()
                    
                    # 保存生成的图片记录
                    GeneratedImage.objects.create(
                        task=task,
                        image_source='image_edit',  # 标记为图像编辑
                        original_url=image_url,
                        saved_path=saved_info['saved_path'],
                        saved_url=saved_info['saved_url'],
                        filename=saved_info['filename'],
                        file_size=saved_info['size'],
                        orig_prompt=f'背景更换：{prompt}',
                        download_time=timezone.now(),
                        is_downloaded=True
                    )
                    
                    logger.info(f"背景更换图片已保存到数据库，任务ID: {task_id}")
                
                return {
                    'edited_image_url': saved_info['saved_url'],
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
                
                error_msg = f"背景更换失败: {response.code} - {response.message}"
                logger.error(error_msg)
                raise Exception(error_msg)
                
        except Exception as e:
            if task:
                task.status = 'failed'
                task.error_message = str(e)
                task.save()
            
            logger.error(f"背景更换失败: {str(e)}")
            raise
    
    def _download_and_save_image(
        self, 
        image_url: str, 
        user_id: int = None,
        edit_type: str = ''
    ) -> Dict[str, Any]:
        """下载并保存图片"""
        try:
            # 下载图片
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            
            # 生成文件名
            filename = f"{edit_type}_{uuid.uuid4().hex[:12]}.png"
            
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
            
            logger.info(f"背景编辑图片保存成功: {saved_path}")
            
            return {
                'saved_path': saved_path,
                'saved_url': saved_url,
                'filename': filename,
                'size': len(response.content)
            }
            
        except Exception as e:
            logger.error(f"保存图片失败: {str(e)}")
            raise


# 创建服务实例
background_edit_service = BackgroundEditService()

