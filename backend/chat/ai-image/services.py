"""
AI图像生成服务
处理图像生成的业务逻辑
"""

import os
import uuid
import logging
import requests
from typing import Dict, List, Any, Optional
from urllib.parse import urlparse, unquote
from pathlib import PurePosixPath
from http import HTTPStatus
from datetime import datetime, timedelta

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.utils import timezone

import dashscope
from dashscope import ImageSynthesis
from django.db import transaction

from .models import ImageGenerationTask, GeneratedImage, UserImageStats

logger = logging.getLogger(__name__)


class ImageGenerationError(Exception):
    """图像生成异常"""
    pass


class ImageDownloadError(Exception):
    """图像下载异常"""
    pass


class AIImageService:
    """AI图像生成服务类"""
    
    def __init__(self):
        # 设置API密钥
        dashscope.api_key = settings.DASHSCOPE_API_KEY
        
        # 检查API密钥是否配置
        if not settings.DASHSCOPE_API_KEY:
            raise ImageGenerationError("DashScope API密钥未配置")
    
    def generate_image(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        size: str = "1328*1328",
        prompt_extend: bool = True,
        watermark: bool = True,
        style: Optional[str] = None,
        shot_type: Optional[str] = None,
        angle: Optional[str] = None,
        shooting_technique: Optional[str] = None,
        lighting: Optional[str] = None,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        生成图像
        
        Args:
            prompt: 正向提示词
            negative_prompt: 反向提示词
            size: 图像尺寸
            prompt_extend: 是否启用智能改写
            watermark: 是否添加水印
            user_id: 用户ID
            
        Returns:
            生成结果字典（固定生成1张图片）
        """
        task = None
        try:
            logger.info(f"开始生成图像，用户ID: {user_id}, 提示词: {prompt[:100]}...")
            
            # 生成任务ID
            task_id = str(uuid.uuid4())
            
            # 创建数据库记录
            if user_id:
                task = self._create_task_record(
                    user_id=user_id,
                    task_id=task_id,
                    prompt=prompt,
                    negative_prompt=negative_prompt,
                    size=size,
                    n=1,  # 固定生成1张图片
                    prompt_extend=prompt_extend,
                    watermark=watermark,
                    style=style,
                    shot_type=shot_type,
                    angle=angle,
                    shooting_technique=shooting_technique,
                    lighting=lighting
                )
            
            # 构建请求参数
            params = {
                'model': 'qwen-image',
                'prompt': prompt,
                'n': 1,  # 固定生成1张图片
                'size': size,
                'prompt_extend': prompt_extend,
                'watermark': watermark
            }
            
            # 添加反向提示词
            if negative_prompt and negative_prompt.strip():
                params['negative_prompt'] = negative_prompt.strip()
            
            # 更新任务状态为处理中
            if task:
                task.status = 'processing'
                task.save(update_fields=['status'])
            
            # 调用DashScope API
            logger.info(f"调用DashScope API，参数: {params}")
            response = ImageSynthesis.call(
                api_key=settings.DASHSCOPE_API_KEY,
                **params
            )
            
            logger.info(f"API响应状态: {response.status_code}")
            
            if response.status_code == HTTPStatus.OK:
                # 处理成功响应
                result = self._process_success_response(response, task, user_id)
                logger.info(f"图像生成成功，任务ID: {result.get('task_id')}")
                
                # 更新任务状态为完成
                if task:
                    try:
                        task.status = 'completed'
                        task.completed_at = timezone.now()
                        task.api_request_id = result.get('request_id', '')
                        
                        # 安全地提取usage数据，确保是纯字典类型
                        usage_data = result.get('usage', {})
                        if usage_data and not isinstance(usage_data, dict):
                            try:
                                # 如果不是字典，尝试转换
                                if hasattr(usage_data, '__dict__'):
                                    usage_data = dict(usage_data.__dict__)
                                else:
                                    usage_data = {'raw_data': str(usage_data)}
                            except Exception:
                                usage_data = {}
                        task.api_usage = usage_data
                        
                        task.enhanced_prompt = result.get('enhanced_prompt', prompt)
                        task.save()
                        logger.info(f"任务状态更新为完成: {task.task_id}")
                    except Exception as e:
                        logger.error(f"更新任务状态为完成失败: {str(e)}")
                        logger.error(f"错误详情: {repr(e)}")
                        import traceback
                        logger.error(f"错误堆栈: {traceback.format_exc()}")
                        
                    # 更新用户统计
                    self._update_user_stats(user_id)
                
                return result
            else:
                # 处理失败响应
                error_msg = f"图像生成失败: status_code={response.status_code}, code={response.code}, message={response.message}"
                logger.error(error_msg)
                
                # 更新任务状态为失败
                if task:
                    task.status = 'failed'
                    task.error_message = error_msg
                    task.completed_at = timezone.now()
                    task.save()
                    
                    # 更新用户统计
                    self._update_user_stats(user_id)
                
                raise ImageGenerationError(error_msg)
                
        except Exception as e:
            logger.error(f"图像生成异常: {str(e)}")
            
            # 更新任务状态为失败
            if task:
                task.status = 'failed'
                task.error_message = str(e)
                task.completed_at = timezone.now()
                task.save()
                
                # 更新用户统计
                if user_id:
                    self._update_user_stats(user_id)
            
            if isinstance(e, ImageGenerationError):
                raise
            else:
                raise ImageGenerationError(f"图像生成过程中发生错误: {str(e)}")
    
    def _process_success_response(self, response, task: Optional['ImageGenerationTask'] = None, user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        处理成功响应
        
        Args:
            response: API响应
            user_id: 用户ID
            
        Returns:
            处理后的结果
        """
        output = response.output
        task_id = task.task_id if task else output.get('task_id', str(uuid.uuid4()))
        
        # 处理生成的图像
        images = []
        if output.get('results'):
            for result in output['results']:
                try:
                    # 下载并保存图像
                    image_info = self._download_and_save_image(
                        result['url'], 
                        task_id, 
                        user_id
                    )
                    
                    # 添加额外信息
                    image_info.update({
                        'orig_prompt': result.get('orig_prompt', ''),
                        'actual_prompt': result.get('actual_prompt', ''),
                    })
                    
                    images.append(image_info)
                    
                except Exception as e:
                    logger.error(f"处理图像失败: {str(e)}")
                    # 继续处理其他图像，不要因为一张图像失败就整体失败
                    continue
            
            # 如果有任务对象，保存图像记录到数据库
            if task and images:
                try:
                    self._save_generated_images(task, images)
                except Exception as e:
                    logger.error(f"保存图像记录到数据库失败: {str(e)}")
        
        # 安全地提取DashScope响应数据，避免对象类型冲突
        usage_data = {}
        if hasattr(response, 'usage') and response.usage:
            try:
                # 将DashScope usage对象转换为字典
                if hasattr(response.usage, '__dict__'):
                    usage_data = dict(response.usage.__dict__)
                elif isinstance(response.usage, dict):
                    usage_data = dict(response.usage)
                else:
                    usage_data = {'raw_usage': str(response.usage)}
            except Exception as e:
                logger.warning(f"提取usage信息失败: {str(e)}")
                usage_data = {}
        
        request_id = ''
        if hasattr(response, 'request_id'):
            try:
                request_id = str(getattr(response, 'request_id', ''))
            except Exception as e:
                logger.warning(f"提取request_id失败: {str(e)}")
                request_id = ''
        
        return {
            'task_id': task_id,
            'status': output.get('task_status', 'SUCCEEDED'),
            'images': images,
            'usage': usage_data,
            'request_id': request_id,
            'submit_time': output.get('submit_time'),
            'end_time': output.get('end_time'),
        }
    
    def _download_and_save_image(
        self, 
        image_url: str, 
        task_id: str, 
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        下载并保存图像
        
        Args:
            image_url: 图像URL
            task_id: 任务ID
            user_id: 用户ID
            
        Returns:
            图像信息字典
        """
        try:
            logger.info(f"开始下载图像: {image_url}")
            
            # 下载图像
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            
            # 获取文件名
            original_filename = PurePosixPath(unquote(urlparse(image_url).path)).parts[-1]
            if not original_filename:
                original_filename = f"{task_id}_{uuid.uuid4().hex[:8]}.png"
            
            # 构建保存路径 - 保存到MEDIA_ROOT/ai-images目录下
            timestamp = datetime.now().strftime('%Y%m%d')
            if user_id:
                save_path = f"ai-images/{user_id}/{timestamp}/{original_filename}"
            else:
                save_path = f"ai-images/anonymous/{timestamp}/{original_filename}"
            
            # 保存图像到存储
            saved_path = default_storage.save(
                save_path, 
                ContentFile(response.content)
            )
            
            # 生成访问URL
            if hasattr(default_storage, 'url'):
                saved_url = default_storage.url(saved_path)
            else:
                saved_url = f"/media/{saved_path}"
            
            logger.info(f"图像保存成功: {saved_path}")
            
            return {
                'original_url': image_url,
                'saved_path': saved_path,
                'saved_url': saved_url,
                'filename': original_filename,
                'size': len(response.content),
                'download_time': timezone.now().isoformat(),
            }
            
        except requests.RequestException as e:
            error_msg = f"下载图像失败: {str(e)}"
            logger.error(error_msg)
            raise ImageDownloadError(error_msg)
        except Exception as e:
            error_msg = f"保存图像失败: {str(e)}"
            logger.error(error_msg)
            raise ImageDownloadError(error_msg)
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        查询任务状态（异步任务）
        
        Args:
            task_id: 任务ID
            
        Returns:
            任务状态信息
        """
        try:
            # 注意：这里假设DashScope支持任务状态查询
            # 实际使用时需要根据API文档调整
            response = ImageSynthesis.fetch(task_id)
            
            if response.status_code == HTTPStatus.OK:
                return {
                    'task_id': task_id,
                    'status': response.output.get('task_status', 'UNKNOWN'),
                    'results': response.output.get('results', []),
                    'submit_time': response.output.get('submit_time'),
                    'end_time': response.output.get('end_time'),
                }
            else:
                raise ImageGenerationError(f"查询任务状态失败: {response.message}")
                
        except Exception as e:
            logger.error(f"查询任务状态异常: {str(e)}")
            raise ImageGenerationError(f"查询任务状态失败: {str(e)}")
    
    def validate_image_params(self, params: Dict[str, Any]) -> None:
        """
        验证图像生成参数
        
        Args:
            params: 参数字典
        """
        # 验证尺寸
        valid_sizes = [
            '1328*1328', '1664*928', '928*1664', 
            '1472*1140', '1140*1472'
        ]
        if params.get('size') not in valid_sizes:
            raise ImageGenerationError(f"不支持的图像尺寸: {params.get('size')}")
        
        # 验证数量
        n = params.get('n', 1)
        if not isinstance(n, int) or n < 1 or n > 4:
            raise ImageGenerationError("图像生成数量必须在1-4之间")
        
        # 验证提示词长度
        prompt = params.get('prompt', '')
        if len(prompt) > 2000:
            raise ImageGenerationError("正向提示词长度不能超过2000字符")
        
        negative_prompt = params.get('negative_prompt', '')
        if negative_prompt and len(negative_prompt) > 1000:
            raise ImageGenerationError("反向提示词长度不能超过1000字符")
    
    def cleanup_expired_images(self, days: int = 30) -> int:
        """
        清理过期图像
        
        Args:
            days: 保留天数
            
        Returns:
            清理的文件数量
        """
        try:
            # 这里可以实现清理逻辑
            # 例如删除超过指定天数的图像文件
            logger.info(f"开始清理{days}天前的图像文件")
            
            # 实际实现时需要遍历存储目录并删除过期文件
            # 这里只是示例
            cleanup_count = 0
            
            logger.info(f"清理完成，共清理{cleanup_count}个文件")
            return cleanup_count
            
        except Exception as e:
            logger.error(f"清理过期图像失败: {str(e)}")
            return 0
    
    def get_user_image_stats(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """
        获取用户图像生成统计
        
        Args:
            user_id: 用户ID
            days: 统计天数
            
        Returns:
            统计信息
        """
        try:
            # 这里可以实现统计逻辑
            # 例如查询数据库获取用户的生成记录
            
            return {
                'user_id': user_id,
                'total_images': 0,
                'success_count': 0,
                'failed_count': 0,
                'total_size': 0,
                'period_days': days,
            }
            
        except Exception as e:
            logger.error(f"获取用户统计失败: {str(e)}")
            return {}
    
    def _create_task_record(self, user_id: int, task_id: str, **kwargs) -> 'ImageGenerationTask':
        """创建任务记录"""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        try:
            user = User.objects.get(id=user_id)
            task = ImageGenerationTask.objects.create(
                user=user,
                task_id=task_id,
                **kwargs
            )
            logger.info(f"创建任务记录成功: {task_id}")
            return task
        except Exception as e:
            logger.error(f"创建任务记录失败: {str(e)}")
            raise
    
    def _save_generated_images(self, task: 'ImageGenerationTask', images_data: List[Dict]) -> List['GeneratedImage']:
        """保存生成的图像记录"""
        saved_images = []
        
        for image_data in images_data:
            try:
                image_record = GeneratedImage.objects.create(
                    task=task,
                    original_url=image_data.get('original_url', ''),
                    saved_path=image_data.get('saved_path', ''),
                    saved_url=image_data.get('saved_url', ''),
                    filename=image_data.get('filename', ''),
                    file_size=image_data.get('size', 0),
                    orig_prompt=image_data.get('orig_prompt', ''),
                    actual_prompt=image_data.get('actual_prompt', ''),
                    download_time=timezone.now(),
                    is_downloaded=True
                )
                saved_images.append(image_record)
                logger.info(f"保存图像记录成功: {image_record.filename}")
                
            except Exception as e:
                logger.error(f"保存图像记录失败: {str(e)}")
                continue
        
        return saved_images
    
    def _update_user_stats(self, user_id: int):
        """更新用户统计数据"""
        if not user_id:
            return
        
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            user = User.objects.get(id=user_id)
            stats, created = UserImageStats.objects.get_or_create(user=user)
            stats.update_stats()
            logger.info(f"更新用户统计成功: {user.username}")
            
        except Exception as e:
            logger.error(f"更新用户统计失败: {str(e)}")


# 创建服务实例
ai_image_service = AIImageService()
