"""
AI视频生成服务
提供文生视频、图生视频等功能
"""

import os
import uuid
import logging
import requests
import traceback
import base64
import mimetypes
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import PurePosixPath
from urllib.parse import urlparse, unquote
from http import HTTPStatus

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.utils import timezone
from django.db import transaction

from dashscope import VideoSynthesis
from .models import (
    VideoGenerationTask, GeneratedVideo, UserVideoStats, VideoStylePreset
)

logger = logging.getLogger(__name__)


class VideoGenerationError(Exception):
    """视频生成异常"""
    pass


class AIVideoService:
    """AI视频生成服务类"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'DASHSCOPE_API_KEY', os.getenv('DASHSCOPE_API_KEY'))
        if not self.api_key:
            raise VideoGenerationError("DASHSCOPE_API_KEY 未配置")
    
    def text_to_video(
        self,
        user_id: int,
        prompt: str,
        model: str = 'wanx2.1-t2v-turbo',
        resolution: str = '1280*720',
        duration: int = 5,
        fps: int = 25
    ) -> Dict[str, Any]:
        """
        文生视频
        
        Args:
            user_id: 用户ID
            prompt: 文本提示词
            model: 生成模型
            resolution: 分辨率
            duration: 视频时长(秒)
            fps: 帧率
            
        Returns:
            包含生成结果的字典
        """
        try:
            # 创建视频生成任务记录
            with transaction.atomic():
                task = VideoGenerationTask.objects.create(
                    user_id=user_id,
                    task_type='text_to_video',
                    status='pending',
                    prompt=prompt,
                    model=model,
                    resolution=resolution,
                    duration=duration,
                    fps=fps
                )
            
            logger.info(f"开始文生视频任务: {task.task_id}")
            
            # 更新状态为处理中
            task.status = 'processing'
            task.submit_time = timezone.now()
            task.save()
            
            # 调用DashScope VideoSynthesis API
            result = self._call_text_to_video_api(task)
            
            # 处理成功响应
            if result.get('status') == 'SUCCEEDED':
                # 下载并保存生成的视频
                if result.get('video_url'):
                    saved_info = self._download_and_save_video(
                        result['video_url'],
                        task.task_id,
                        user_id
                    )
                    result.update(saved_info)
                
                # 更新任务状态
                task.status = 'completed'
                task.completed_at = timezone.now()
                task.end_time = timezone.now()
                task.output_video_url = result.get('video_url', '')
                task.saved_video_path = result.get('saved_path', '')
                task.video_file_size = result.get('file_size', 0)
                task.enhanced_prompt = result.get('actual_prompt', prompt)
                task.api_request_id = result.get('request_id', '')
                task.api_task_id = result.get('task_id', '')
                task.api_usage = result.get('usage', {})
                
                # 安全地提取时间信息
                if result.get('submit_time'):
                    try:
                        submit_time_str = result['submit_time']
                        if isinstance(submit_time_str, str):
                            from datetime import datetime
                            task.submit_time = datetime.fromisoformat(submit_time_str.replace(' ', 'T'))
                    except Exception as e:
                        logger.warning(f"解析submit_time失败: {str(e)}")
                
                if result.get('end_time'):
                    try:
                        end_time_str = result['end_time']
                        if isinstance(end_time_str, str):
                            from datetime import datetime
                            task.end_time = datetime.fromisoformat(end_time_str.replace(' ', 'T'))
                    except Exception as e:
                        logger.warning(f"解析end_time失败: {str(e)}")
                
                task.save()
                
                # 保存生成的视频记录
                if result.get('video_url'):
                    self._save_generated_video(task, result)
                
                # 更新用户统计
                self._update_user_stats(user_id)
                
                logger.info(f"文生视频完成: {task.task_id}")
                
                return {
                    'task_id': task.task_id,
                    'status': 'completed',
                    'video_url': result.get('saved_url', result.get('video_url', '')),
                    'duration': duration,
                    'file_size': result.get('file_size', 0),
                    'enhanced_prompt': result.get('actual_prompt', prompt),
                    'usage': result.get('usage', {})
                }
            else:
                # 处理失败
                raise VideoGenerationError(f"视频生成失败: {result.get('error', '未知错误')}")
                
        except Exception as e:
            logger.error(f"文生视频失败: {str(e)}")
            logger.error(traceback.format_exc())
            
            # 更新任务状态为失败
            if 'task' in locals():
                task.status = 'failed'
                task.error_message = str(e)
                task.save()
            
            raise VideoGenerationError(f"文生视频失败: {str(e)}")
    
    def image_to_video(
        self,
        user_id: int,
        prompt: str,
        input_image=None,
        input_image_url: str = None,
        model: str = 'wan2.2-i2v-plus',
        resolution: str = '1080P',
        duration: int = 5
    ) -> Dict[str, Any]:
        """
        图生视频
        
        Args:
            user_id: 用户ID
            prompt: 文本提示词
            input_image: 输入图片文件
            input_image_url: 输入图片URL
            model: 生成模型
            resolution: 分辨率
            duration: 视频时长(秒)
            
        Returns:
            包含生成结果的字典
        """
        try:
            # 创建视频生成任务记录
            with transaction.atomic():
                task = VideoGenerationTask.objects.create(
                    user_id=user_id,
                    task_type='image_to_video',
                    status='pending',
                    prompt=prompt,
                    input_image_url=input_image_url,
                    model=model,
                    resolution=resolution,
                    duration=duration
                )
                
                # 如果有上传的图片，保存它
                if input_image:
                    task.input_image = input_image
                    task.save()
            
            logger.info(f"开始图生视频任务: {task.task_id}")
            
            # 更新状态为处理中
            task.status = 'processing'
            task.submit_time = timezone.now()
            task.save()
            
            # 准备图片输入
            img_url = self._prepare_image_input(task)
            
            # 调用DashScope VideoSynthesis API
            result = self._call_image_to_video_api(task, img_url)
            
            # 处理成功响应
            if result.get('status') == 'SUCCEEDED':
                # 下载并保存生成的视频
                if result.get('video_url'):
                    saved_info = self._download_and_save_video(
                        result['video_url'],
                        task.task_id,
                        user_id
                    )
                    result.update(saved_info)
                
                # 更新任务状态
                task.status = 'completed'
                task.completed_at = timezone.now()
                task.end_time = timezone.now()
                task.output_video_url = result.get('video_url', '')
                task.saved_video_path = result.get('saved_path', '')
                task.video_file_size = result.get('file_size', 0)
                task.enhanced_prompt = result.get('actual_prompt', prompt)
                task.api_request_id = result.get('request_id', '')
                task.api_task_id = result.get('task_id', '')
                task.api_usage = result.get('usage', {})
                
                # 安全地提取时间信息
                if result.get('submit_time'):
                    try:
                        submit_time_str = result['submit_time']
                        if isinstance(submit_time_str, str):
                            from datetime import datetime
                            task.submit_time = datetime.fromisoformat(submit_time_str.replace(' ', 'T'))
                    except Exception as e:
                        logger.warning(f"解析submit_time失败: {str(e)}")
                
                if result.get('end_time'):
                    try:
                        end_time_str = result['end_time']
                        if isinstance(end_time_str, str):
                            from datetime import datetime
                            task.end_time = datetime.fromisoformat(end_time_str.replace(' ', 'T'))
                    except Exception as e:
                        logger.warning(f"解析end_time失败: {str(e)}")
                
                task.save()
                
                # 保存生成的视频记录
                if result.get('video_url'):
                    self._save_generated_video(task, result)
                
                # 更新用户统计
                self._update_user_stats(user_id)
                
                logger.info(f"图生视频完成: {task.task_id}")
                
                return {
                    'task_id': task.task_id,
                    'status': 'completed',
                    'video_url': result.get('saved_url', result.get('video_url', '')),
                    'duration': duration,
                    'file_size': result.get('file_size', 0),
                    'enhanced_prompt': result.get('actual_prompt', prompt),
                    'usage': result.get('usage', {})
                }
            else:
                # 处理失败
                raise VideoGenerationError(f"视频生成失败: {result.get('error', '未知错误')}")
                
        except Exception as e:
            logger.error(f"图生视频失败: {str(e)}")
            logger.error(traceback.format_exc())
            
            # 更新任务状态为失败
            if 'task' in locals():
                task.status = 'failed'
                task.error_message = str(e)
                task.save()
            
            raise VideoGenerationError(f"图生视频失败: {str(e)}")
    
    def _call_text_to_video_api(self, task: VideoGenerationTask) -> Dict[str, Any]:
        """调用DashScope文生视频API"""
        try:
            logger.info(f"调用文生视频API: {task.task_id}")
            
            # 同步调用VideoSynthesis API
            response = VideoSynthesis.call(
                api_key=self.api_key,
                model=task.model,
                prompt=task.prompt,
                size=task.resolution
            )
            
            logger.info(f"API响应状态: {response.status_code}")
            
            if response.status_code == HTTPStatus.OK:
                output = response.output
                
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
                    'task_id': output.get('task_id', ''),
                    'status': output.get('task_status', 'UNKNOWN'),
                    'video_url': output.get('video_url', ''),
                    'submit_time': output.get('submit_time'),
                    'end_time': output.get('end_time'),
                    'orig_prompt': output.get('orig_prompt', task.prompt),
                    'actual_prompt': output.get('actual_prompt', task.prompt),
                    'usage': usage_data,
                    'request_id': request_id
                }
            else:
                error_msg = f"视频生成失败: status_code={response.status_code}, code={response.code}, message={response.message}"
                logger.error(error_msg)
                raise VideoGenerationError(error_msg)
                
        except Exception as e:
            logger.error(f"文生视频API调用失败: {str(e)}")
            raise VideoGenerationError(f"文生视频API调用失败: {str(e)}")
    
    def _call_image_to_video_api(self, task: VideoGenerationTask, img_url: str) -> Dict[str, Any]:
        """调用DashScope图生视频API"""
        try:
            logger.info(f"调用图生视频API: {task.task_id}")
            
            # 同步调用VideoSynthesis API
            response = VideoSynthesis.call(
                api_key=self.api_key,
                model=task.model,
                prompt=task.prompt,
                resolution=task.resolution,
                img_url=img_url
            )
            
            logger.info(f"API响应状态: {response.status_code}")
            
            if response.status_code == HTTPStatus.OK:
                output = response.output
                
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
                    'task_id': output.get('task_id', ''),
                    'status': output.get('task_status', 'UNKNOWN'),
                    'video_url': output.get('video_url', ''),
                    'submit_time': output.get('submit_time'),
                    'end_time': output.get('end_time'),
                    'orig_prompt': output.get('orig_prompt', task.prompt),
                    'actual_prompt': output.get('actual_prompt', task.prompt),
                    'usage': usage_data,
                    'request_id': request_id
                }
            else:
                error_msg = f"视频生成失败: status_code={response.status_code}, code={response.code}, message={response.message}"
                logger.error(error_msg)
                raise VideoGenerationError(error_msg)
                
        except Exception as e:
            logger.error(f"图生视频API调用失败: {str(e)}")
            raise VideoGenerationError(f"图生视频API调用失败: {str(e)}")
    
    def _prepare_image_input(self, task: VideoGenerationTask) -> str:
        """准备图片输入"""
        try:
            # 如果有URL直接返回
            if task.input_image_url:
                return task.input_image_url
            
            # 如果有上传的文件，生成Base64编码
            if task.input_image:
                file_path = task.input_image.path
                return self._encode_file_to_base64(file_path)
            
            raise VideoGenerationError("没有提供输入图片")
            
        except Exception as e:
            logger.error(f"准备图片输入失败: {str(e)}")
            raise VideoGenerationError(f"准备图片输入失败: {str(e)}")
    
    def _encode_file_to_base64(self, file_path: str) -> str:
        """将文件编码为Base64格式"""
        try:
            mime_type, _ = mimetypes.guess_type(file_path)
            if not mime_type or not mime_type.startswith("image/"):
                raise ValueError("不支持或无法识别的图像格式")
            
            with open(file_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            
            return f"data:{mime_type};base64,{encoded_string}"
            
        except Exception as e:
            logger.error(f"文件Base64编码失败: {str(e)}")
            raise VideoGenerationError(f"文件Base64编码失败: {str(e)}")
    
    def _download_and_save_video(
        self,
        video_url: str,
        task_id: str,
        user_id: int
    ) -> Dict[str, Any]:
        """下载并保存视频文件"""
        try:
            # 生成保存路径
            date_str = timezone.now().strftime('%Y%m%d')
            original_filename = f"{task_id}.mp4"
            save_path = f"ai-videos/{user_id}/{date_str}/{original_filename}"
            
            logger.info(f"开始下载视频: {video_url}")
            
            # 下载视频
            response = requests.get(video_url, timeout=60)  # 视频文件可能较大，增加超时时间
            response.raise_for_status()
            
            # 保存文件
            saved_path = default_storage.save(
                save_path,
                ContentFile(response.content)
            )
            
            # 生成访问URL
            saved_url = default_storage.url(saved_path)
            
            logger.info(f"视频保存成功: {saved_path}")
            
            return {
                'saved_path': saved_path,
                'saved_url': saved_url,
                'filename': original_filename,
                'file_size': len(response.content),
                'download_time': timezone.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"下载视频失败: {str(e)}")
            raise VideoGenerationError(f"下载视频失败: {str(e)}")
    
    def _save_generated_video(self, task: VideoGenerationTask, result: Dict[str, Any]):
        """保存生成的视频记录"""
        try:
            GeneratedVideo.objects.create(
                task=task,
                original_url=result.get('video_url', ''),
                saved_url=result.get('saved_url', ''),
                saved_path=result.get('saved_path', ''),
                filename=result.get('filename', ''),
                file_size=result.get('file_size', 0),
                duration=float(task.duration),
                resolution=task.resolution,
                fps=task.fps,
                is_downloaded=True,
                download_time=timezone.now()
            )
            logger.info(f"视频记录保存成功: {task.task_id}")
            
        except Exception as e:
            logger.error(f"保存视频记录失败: {str(e)}")
            # 这里不抛出异常，避免影响主流程
    
    def _update_user_stats(self, user_id: int):
        """更新用户统计"""
        try:
            UserVideoStats.update_stats(user_id)
        except Exception as e:
            logger.error(f"更新用户视频统计失败: {str(e)}")
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """获取任务状态"""
        try:
            task = VideoGenerationTask.objects.get(task_id=task_id)
            
            result = {
                'task_id': task.task_id,
                'status': task.status,
                'task_type': task.task_type,
                'prompt': task.prompt,
                'created_at': task.created_at.isoformat(),
                'updated_at': task.updated_at.isoformat()
            }
            
            if task.status == 'completed':
                result.update({
                    'completed_at': task.completed_at.isoformat() if task.completed_at else None,
                    'output_video_url': task.output_video_url,
                    'enhanced_prompt': task.enhanced_prompt,
                    'api_usage': task.api_usage,
                    'file_size': task.video_file_size
                })
            elif task.status == 'failed':
                result['error_message'] = task.error_message
            
            return result
            
        except VideoGenerationTask.DoesNotExist:
            raise VideoGenerationError(f"任务不存在: {task_id}")
        except Exception as e:
            logger.error(f"获取任务状态失败: {str(e)}")
            raise VideoGenerationError(f"获取任务状态失败: {str(e)}")
    
    def get_user_video_history(self, user_id: int, task_type: str = None, limit: int = 20) -> List[Dict[str, Any]]:
        """获取用户视频生成历史"""
        try:
            query = VideoGenerationTask.objects.filter(user_id=user_id)
            
            if task_type:
                query = query.filter(task_type=task_type)
            
            tasks = query.order_by('-created_at')[:limit]
            
            history = []
            for task in tasks:
                item = {
                    'task_id': task.task_id,
                    'task_type': task.task_type,
                    'status': task.status,
                    'prompt': task.prompt,
                    'enhanced_prompt': task.enhanced_prompt,
                    'created_at': task.created_at.isoformat(),
                    'output_video_url': task.output_video_url,
                    'file_size': task.video_file_size,
                    'model': task.model,
                    'resolution': task.resolution,
                    'duration': task.duration
                }
                
                if task.completed_at:
                    item['completed_at'] = task.completed_at.isoformat()
                
                if task.error_message:
                    item['error_message'] = task.error_message
                
                history.append(item)
            
            return history
            
        except Exception as e:
            logger.error(f"获取用户视频历史失败: {str(e)}")
            raise VideoGenerationError(f"获取用户视频历史失败: {str(e)}")
    
    def get_video_style_presets(self) -> List[Dict[str, Any]]:
        """获取视频风格预设"""
        try:
            presets = VideoStylePreset.objects.filter(is_active=True).order_by('-usage_count', 'name')
            
            result = []
            for preset in presets:
                item = {
                    'id': preset.id,
                    'name': preset.name,
                    'description': preset.description,
                    'style_keywords': preset.style_keywords,
                    'recommended_model': preset.recommended_model,
                    'default_resolution': preset.default_resolution,
                    'default_duration': preset.default_duration,
                    'default_fps': preset.default_fps,
                    'usage_count': preset.usage_count
                }
                
                if preset.preview_image:
                    item['preview_image'] = preset.preview_image.url
                
                result.append(item)
            
            return result
            
        except Exception as e:
            logger.error(f"获取视频风格预设失败: {str(e)}")
            raise VideoGenerationError(f"获取视频风格预设失败: {str(e)}")
    
    def apply_style_preset(self, preset_id: int, prompt: str) -> str:
        """应用风格预设到提示词"""
        try:
            preset = VideoStylePreset.objects.get(id=preset_id, is_active=True)
            
            # 增加使用次数
            preset.increment_usage()
            
            # 将风格关键词融入提示词
            enhanced_prompt = f"{prompt}, {preset.style_keywords}"
            
            return enhanced_prompt
            
        except VideoStylePreset.DoesNotExist:
            logger.warning(f"风格预设不存在: {preset_id}")
            return prompt
        except Exception as e:
            logger.error(f"应用风格预设失败: {str(e)}")
            return prompt


# 创建服务实例
ai_video_service = AIVideoService()
