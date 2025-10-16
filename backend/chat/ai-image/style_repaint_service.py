"""
图像风格重绘服务
使用 wanx-style-repaint-v1 模型实现风格转换
"""
import os
import logging
import uuid
import time
import requests
from typing import Dict, Any, Optional
from http import HTTPStatus
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.utils import timezone
from django.db import transaction
from .models import ImageGenerationTask, GeneratedImage

logger = logging.getLogger(__name__)


class StyleRepaintService:
    """图像风格重绘服务类"""
    
    # 预置风格列表（根据图片中的40种风格）
    PRESET_STYLES = {
        0: '复古漫画',
        1: '3D童话',
        2: '二次元',
        3: '小清新',
        4: '未来科技',
        5: '国画古风',
        6: '将军百战',
        7: '炫彩卡通',
        8: '清雅国风',
        9: '喜迎新年',
        14: '国风工笔',
        15: '恭贺新禧',
        30: '童话世界',
        31: '黏土世界',
        32: '像素世界',
        33: '冒险世界',
        34: '日漫世界',
        35: '3D世界',
        36: '二次元世界',
        37: '手绘世界',
        38: '蜡笔世界',
        39: '冰箱贴世界',
        40: '吧嗒世界'
    }
    
    def __init__(self):
        self.api_key = settings.DASHSCOPE_API_KEY
        self.base_url = "https://dashscope.aliyuncs.com/api/v1"
    
    @transaction.atomic
    def repaint_style(
        self, 
        image_url: str, 
        style_index: int, 
        user_id: int = None
    ) -> Dict[str, Any]:
        """
        风格重绘
        
        Args:
            image_url: 图片URL（HTTP/HTTPS或base64）
            style_index: 风格索引（0-40）
            user_id: 用户ID
            
        Returns:
            重绘结果
        """
        task_model = None
        try:
            style_name = self.PRESET_STYLES.get(style_index, f'风格{style_index}')
            logger.info(f"开始风格重绘，用户ID: {user_id}, 风格: {style_name}")
            
            # 创建任务记录
            task_id = str(uuid.uuid4())
            if user_id:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                user = User.objects.get(id=user_id)
                
                task_model = ImageGenerationTask.objects.create(
                    user=user,
                    task_id=task_id,
                    prompt=f'风格重绘：{style_name}',
                    size='style_repaint',
                    n=1,
                    status='processing',
                    style=style_name,
                    prompt_extend=False,
                    watermark=False
                )
            
            # 提交异步任务
            api_task_id = self._submit_task(image_url, style_index)
            
            if not api_task_id:
                raise Exception("提交任务失败")
            
            # 轮询查询结果
            result_url = self._query_task_result(api_task_id)
            
            if not result_url:
                raise Exception("获取结果失败")
            
            # 下载并保存图片
            saved_info = self._download_and_save_image(result_url, user_id, style_name)
            
            # 更新任务状态并保存到数据库
            if task_model:
                task_model.status = 'completed'
                task_model.completed_at = timezone.now()
                task_model.save()
                
                # 保存生成的图片记录
                GeneratedImage.objects.create(
                    task=task_model,
                    image_source='image_edit',  # 标记为图像编辑
                    original_url=result_url,
                    saved_path=saved_info['saved_path'],
                    saved_url=saved_info['saved_url'],
                    filename=saved_info['filename'],
                    file_size=saved_info['size'],
                    orig_prompt=f'风格重绘：{style_name}',
                    download_time=timezone.now(),
                    is_downloaded=True
                )
                
                logger.info(f"风格重绘图片已保存到数据库，任务ID: {task_id}")
            
            return {
                'edited_image_url': saved_info['saved_url'],
                'original_url': result_url,
                'filename': saved_info['filename'],
                'size': saved_info['size'],
                'task_id': task_id,
                'style': style_name
            }
            
        except Exception as e:
            if task_model:
                task_model.status = 'failed'
                task_model.error_message = str(e)
                task_model.save()
            
            logger.error(f"风格重绘失败: {str(e)}")
            raise
    
    def _submit_task(self, image_url: str, style_index: int) -> Optional[str]:
        """提交风格重绘任务"""
        try:
            url = f"{self.base_url}/services/aigc/image-generation/generation"
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "X-DashScope-Async": "enable"  # 异步调用
            }
            
            body = {
                "model": "wanx-style-repaint-v1",
                "input": {
                    "image_url": image_url,
                    "style_index": style_index
                }
            }
            
            response = requests.post(url, headers=headers, json=body, timeout=30)
            
            if response.status_code == HTTPStatus.OK:
                task_id = response.json().get('output', {}).get('task_id')
                logger.info(f"任务提交成功，API任务ID: {task_id}")
                return task_id
            else:
                logger.error(f"提交任务失败: {response.status_code}, {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"提交任务异常: {str(e)}")
            return None
    
    def _query_task_result(self, task_id: str, max_attempts: int = 24) -> Optional[str]:
        """轮询查询任务结果"""
        try:
            url = f"{self.base_url}/tasks/{task_id}"
            headers = {"Authorization": f"Bearer {self.api_key}"}
            
            logger.info("开始查询任务状态...")
            
            for attempt in range(max_attempts):
                response = requests.get(url, headers=headers, timeout=10)
                
                if response.status_code != HTTPStatus.OK:
                    logger.error(f"查询失败: {response.status_code}, {response.text}")
                    return None
                
                response_data = response.json()
                task_status = response_data.get('output', {}).get('task_status')
                
                if task_status == 'SUCCEEDED':
                    logger.info("任务成功完成！")
                    results = response_data.get('output', {}).get('results', [])
                    if results:
                        result_url = results[0].get('url')
                        logger.info(f"生成图片URL: {result_url}")
                        return result_url
                    else:
                        logger.error("任务成功但没有返回结果")
                        return None
                        
                elif task_status == 'FAILED':
                    error_msg = response_data.get('output', {}).get('message', '未知错误')
                    logger.error(f"任务失败: {error_msg}")
                    return None
                else:
                    logger.info(f"任务处理中... 状态: {task_status} (尝试 {attempt + 1}/{max_attempts})")
                    time.sleep(5)  # 等待5秒后再次查询
            
            logger.error(f"任务超时，已尝试 {max_attempts} 次")
            return None
            
        except Exception as e:
            logger.error(f"查询任务异常: {str(e)}")
            return None
    
    def _download_and_save_image(
        self, 
        image_url: str, 
        user_id: int = None,
        style_name: str = ''
    ) -> Dict[str, Any]:
        """下载并保存图片"""
        try:
            # 下载图片
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            
            # 生成文件名
            filename = f"style_{style_name}_{uuid.uuid4().hex[:8]}.png"
            
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
            
            logger.info(f"风格重绘图片保存成功: {saved_path}")
            
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
style_repaint_service = StyleRepaintService()

