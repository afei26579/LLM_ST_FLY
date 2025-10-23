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
        model: str = 'wan2.5-t2v-preview',
        resolution: str = '1280*720',
        duration: int = 5,
        fps: int = 24,
        seed: int = None
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
            seed: 随机种子
            
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
                    fps=fps,
                    seed=seed
                )
            
            logger.info(f"开始文生视频任务: {task.task_id}")
            
            # 更新状态为处理中
            task.status = 'processing'
            task.submit_time = timezone.now()
            task.save()
            
            # 调用DashScope VideoSynthesis API（异步）
            result = self._call_text_to_video_api_async(task)
            
            # 异步调用立即返回，任务状态为 processing
            if result.get('status') == 'SUBMITTED':
                # 保存 API 任务 ID 和响应对象
                task.api_task_id = result.get('api_task_id', '')
                task.api_request_id = result.get('request_id', '')
                task.status = 'processing'
                task.save()
                
                # 将响应对象临时存储（用于 fetch 查询）
                # 注意：由于响应对象无法序列化，我们只保存 task_id
                if not hasattr(self, '_async_responses'):
                    self._async_responses = {}
                self._async_responses[task.task_id] = result.get('response')
                
                logger.info(f"异步任务已提交: task_id={task.task_id}, api_task_id={task.api_task_id}")
                
                # 立即返回给前端，前端会轮询状态
                return {
                    'task_id': task.task_id,
                    'api_task_id': task.api_task_id,
                    'status': 'processing',
                    'message': '视频生成任务已提交，正在处理中...'
                }
            else:
                # 提交失败
                raise VideoGenerationError(f"异步任务提交失败: {result.get('error', '未知错误')}")
                
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
        prompt: str = '',
        input_image=None,
        input_image_url: str = None,
        model: str = 'wan2.5-i2v-preview',
        resolution: str = '720P',
        duration: int = 5,
        fps: int = 24
    ) -> Dict[str, Any]:
        """
        图生视频（异步模式）
        
        Args:
            user_id: 用户ID
            prompt: 文本提示词（可选）
            input_image: 输入图片文件
            input_image_url: 输入图片URL
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
                    task_type='image_to_video',
                    status='pending',
                    prompt=prompt,
                    input_image_url=input_image_url,
                    model=model,
                    resolution=resolution,
                    duration=duration,
                    fps=fps
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
            
            # 调用DashScope VideoSynthesis API（异步）
            result = self._call_image_to_video_api_async(task, img_url)
            
            # 异步调用立即返回
            if result.get('status') == 'SUBMITTED':
                # 保存 API 任务 ID
                task.api_task_id = result.get('api_task_id', '')
                task.api_request_id = result.get('request_id', '')
                task.status = 'processing'
                task.save()
                
                # 保存响应对象供后续轮询使用
                if not hasattr(self, '_async_responses'):
                    self._async_responses = {}
                self._async_responses[task.task_id] = result.get('response')
                
                logger.info(f"图生视频异步任务已提交: task_id={task.task_id}, api_task_id={task.api_task_id}")
                
                # 立即返回给前端
                return {
                    'task_id': task.task_id,
                    'api_task_id': task.api_task_id,
                    'status': 'processing',
                    'message': '图生视频任务已提交，正在处理中...'
                }
            else:
                # 提交失败
                raise VideoGenerationError(f"异步任务提交失败: {result.get('error', '未知错误')}")
                
        except Exception as e:
            logger.error(f"图生视频失败: {str(e)}")
            logger.error(traceback.format_exc())
            
            # 更新任务状态为失败
            if 'task' in locals():
                task.status = 'failed'
                task.error_message = str(e)
                task.save()
            
            raise VideoGenerationError(f"图生视频失败: {str(e)}")
    
    def _call_text_to_video_api_async(self, task: VideoGenerationTask) -> Dict[str, Any]:
        """调用DashScope文生视频API（异步模式）"""
        try:
            logger.info(f"调用文生视频API（异步）: {task.task_id}, duration={task.duration}, seed={task.seed}")
            
            # 构建 API 参数
            api_params = {
                'api_key': self.api_key,
                'model': task.model,
                'prompt': task.prompt,
                'size': task.resolution,
                'duration': task.duration,  # 视频时长
                'audio': True,
                'prompt_extend': True,  # 启用提示词增强
                'watermark': False
            }
            
            # 如果提供了随机种子，添加到参数中
            if task.seed is not None:
                api_params['seed'] = int(task.seed)
                logger.info(f"使用随机种子: {task.seed}")
            
            # 异步调用VideoSynthesis API
            response = VideoSynthesis.async_call(**api_params)
            
            logger.info(f"异步API响应状态: {response.status_code}")
            
            if response.status_code == HTTPStatus.OK:
                # 异步调用成功，返回任务ID
                api_task_id = response.output.task_id
                logger.info(f"异步任务已提交: api_task_id={api_task_id}")
                
                # 提取 request_id
                request_id = ''
                if hasattr(response, 'request_id'):
                    try:
                        request_id = str(getattr(response, 'request_id', ''))
                    except Exception as e:
                        logger.warning(f"提取request_id失败: {str(e)}")
                
                # 保存响应对象到实例变量（用于后续 fetch）
                # 注意：这里我们只能保存 api_task_id，fetch 时需要重新构造
                
                return {
                    'status': 'SUBMITTED',
                    'api_task_id': api_task_id,
                    'request_id': request_id,
                    'submit_time': timezone.now().isoformat(),
                    'response': response  # 保存响应对象
                }
            else:
                error_msg = f"异步任务提交失败: status_code={response.status_code}, code={response.code}, message={response.message}"
                logger.error(error_msg)
                raise VideoGenerationError(error_msg)
                
        except Exception as e:
            logger.error(f"文生视频API调用失败（异步）: {str(e)}")
            logger.error(traceback.format_exc())
            raise VideoGenerationError(f"文生视频API调用失败: {str(e)}")
    
    def fetch_video_task_status(self, task_id: str, async_response=None) -> Dict[str, Any]:
        """查询视频生成任务状态"""
        try:
            logger.info(f"查询视频任务状态: task_id={task_id}")
            
            # 从数据库获取 api_task_id
            from .models import VideoGenerationTask
            db_task = VideoGenerationTask.objects.get(task_id=task_id)
            api_task_id = db_task.api_task_id
            
            if not api_task_id:
                raise VideoGenerationError("任务缺少 api_task_id")
            
            # 如果有保存的异步响应对象，使用它；否则尝试从缓存获取
            if async_response is None and hasattr(self, '_async_responses'):
                async_response = self._async_responses.get(task_id)
            
            # 如果仍然没有响应对象，构造一个简单的（参照 demo.py 的结构）
            if async_response is None:
                # 构造一个模拟的响应对象，包含 task_id
                class MockResponse:
                    def __init__(self, task_id):
                        # 创建 output 对象，包含 task_id 属性
                        self.output = type('Output', (), {'task_id': task_id})()
                        self.status_code = HTTPStatus.OK
                
                async_response = MockResponse(api_task_id)
                logger.info(f"构造模拟响应对象: api_task_id={api_task_id}")
            
            # 使用 fetch 查询任务状态（参照 demo.py: VideoSynthesis.fetch(rsp)）
            response = VideoSynthesis.fetch(async_response)
            
            if response.status_code == HTTPStatus.OK:
                output = response.output
                task_status = output.task_status
                
                logger.info(f"任务状态: {task_status}")
                
                result = {
                    'task_id': api_task_id,
                    'task_status': task_status,
                    'submit_time': output.get('submit_time'),
                    'scheduled_time': output.get('scheduled_time'),
                    'end_time': output.get('end_time')
                }
                
                # 如果任务完成，获取视频URL
                if task_status == 'SUCCEEDED':
                    result['video_url'] = output.video_url
                    result['actual_prompt'] = output.get('actual_prompt', '')
                    result['orig_prompt'] = output.get('orig_prompt', '')
                    
                    # 提取 usage 信息
                    if hasattr(response, 'usage') and response.usage:
                        try:
                            if hasattr(response.usage, '__dict__'):
                                result['usage'] = dict(response.usage.__dict__)
                            elif isinstance(response.usage, dict):
                                result['usage'] = dict(response.usage)
                        except Exception as e:
                            logger.warning(f"提取usage信息失败: {str(e)}")
                elif task_status == 'FAILED':
                    result['error'] = output.get('message', '视频生成失败')
                    result['code'] = output.get('code', '')
                
                return result
            else:
                error_msg = f"查询任务状态失败: {response.code}, {response.message}"
                logger.error(error_msg)
                raise VideoGenerationError(error_msg)
                
        except Exception as e:
            logger.error(f"查询视频任务状态失败: {str(e)}")
            logger.error(traceback.format_exc())
            raise VideoGenerationError(f"查询任务状态失败: {str(e)}")
    
    def _call_image_to_video_api_async(self, task: VideoGenerationTask, img_url: str) -> Dict[str, Any]:
        """调用DashScope图生视频API（异步模式）"""
        try:
            logger.info(f"调用图生视频API（异步）: {task.task_id}, resolution={task.resolution}, duration={task.duration}")
            logger.info(f"图片URL: {img_url[:100]}...")
            
            # 构建 API 参数（参照 demo2.py）
            # 注意：wan2.5-i2v-preview 模型的 resolution 使用 "480P", "720P", "1080P" 格式
            # 如果前端传来的是 "1280*720" 格式，需要转换
            resolution = task.resolution
            if '*' in resolution:
                # 转换 "1280*720" → "720P" 格式
                resolution_map = {
                    '854*480': '480P',
                    '1280*720': '720P',
                    '1920*1080': '1080P'
                }
                resolution = resolution_map.get(resolution, resolution)
                logger.info(f"分辨率格式转换: {task.resolution} → {resolution}")
            
            api_params = {
                'api_key': self.api_key,
                'model': task.model,
                'prompt': task.prompt if task.prompt else '让图片动起来',  # 提供默认提示词
                'resolution': resolution,  # 使用转换后的格式
                'duration': task.duration,
                'img_url': img_url
            }
            
            logger.info(f"API参数: model={task.model}, resolution={resolution}, duration={task.duration}")
            
            # 异步调用VideoSynthesis API（参照 demo2.py）
            response = VideoSynthesis.async_call(**api_params)
            
            logger.info(f"异步API响应状态: {response.status_code}")
            
            if response.status_code == HTTPStatus.OK:
                # 异步调用成功，返回任务ID
                api_task_id = response.output.task_id
                logger.info(f"图生视频异步任务已提交: api_task_id={api_task_id}")
                
                # 提取 request_id
                request_id = ''
                if hasattr(response, 'request_id'):
                    try:
                        request_id = str(getattr(response, 'request_id', ''))
                    except Exception as e:
                        logger.warning(f"提取request_id失败: {str(e)}")
                
                return {
                    'status': 'SUBMITTED',
                    'api_task_id': api_task_id,
                    'request_id': request_id,
                    'submit_time': timezone.now().isoformat(),
                    'response': response  # 保存响应对象
                }
            else:
                error_msg = f"异步任务提交失败: status_code={response.status_code}, code={response.code}, message={response.message}"
                logger.error(error_msg)
                raise VideoGenerationError(error_msg)
                
        except Exception as e:
            logger.error(f"图生视频API调用失败（异步）: {str(e)}")
            logger.error(traceback.format_exc())
            raise VideoGenerationError(f"图生视频API调用失败: {str(e)}")
    
    def _prepare_image_input(self, task: VideoGenerationTask) -> str:
        """准备图片输入（使用 file:// 格式）"""
        try:
            # 如果有URL直接返回
            if task.input_image_url:
                return task.input_image_url
            
            # 如果有上传的文件，使用 file:// 本地路径（参照 demo2.py）
            if task.input_image:
                file_path = task.input_image.path
                # 添加 file:// 前缀（Windows 路径使用正斜杠）
                img_url = f"file://{file_path}"
                logger.info(f"使用本地文件路径: {img_url}")
                return img_url
            
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
        """获取任务状态（支持异步任务轮询）"""
        try:
            task = VideoGenerationTask.objects.get(task_id=task_id)
            
            # 如果任务还在处理中，且有 API 任务ID，查询 DashScope 任务状态
            if task.status == 'processing' and task.api_task_id:
                try:
                    logger.info(f"轮询异步任务状态: task_id={task_id}, api_task_id={task.api_task_id}")
                    
                    # 查询 DashScope 任务状态（传递 task_id 用于获取响应对象）
                    api_result = self.fetch_video_task_status(task_id)
                    
                    # 根据 API 返回的状态更新本地任务
                    if api_result['task_status'] == 'SUCCEEDED':
                        # 任务完成，下载视频
                        logger.info(f"视频生成完成: {task_id}")
                        
                        # 下载并保存视频
                        video_url = api_result.get('video_url')
                        if video_url:
                            saved_info = self._download_and_save_video(
                                video_url,
                                task.task_id,
                                task.user_id
                            )
                            
                            # 更新任务状态
                            task.status = 'completed'
                            task.completed_at = timezone.now()
                            task.output_video_url = video_url
                            task.saved_video_path = saved_info.get('saved_path', '')
                            task.video_file_size = saved_info.get('file_size', 0)
                            task.enhanced_prompt = api_result.get('actual_prompt', task.prompt)
                            task.api_usage = api_result.get('usage', {})
                            
                            # 解析时间信息
                            if api_result.get('end_time'):
                                try:
                                    from datetime import datetime
                                    task.end_time = datetime.fromisoformat(api_result['end_time'].replace(' ', 'T'))
                                except:
                                    pass
                            
                            task.save()
                            
                            # 保存视频记录
                            self._save_generated_video(task, {
                                'video_url': video_url,
                                'saved_url': saved_info.get('saved_url', ''),
                                'saved_path': saved_info.get('saved_path', ''),
                                'filename': saved_info.get('filename', ''),
                                'file_size': saved_info.get('file_size', 0)
                            })
                            
                            # 更新用户统计
                            self._update_user_stats(task.user_id)
                    
                    elif api_result['task_status'] == 'FAILED':
                        # 任务失败
                        task.status = 'failed'
                        task.error_message = api_result.get('error', '视频生成失败')
                        task.save()
                        logger.error(f"视频生成失败: {task_id}, error={task.error_message}")
                    
                except Exception as e:
                    logger.error(f"轮询任务状态异常: {str(e)}")
                    # 不抛出异常，继续返回当前状态
            
            # 构建返回结果
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
                    'result_url': task.output_video_url,  # 前端使用 result_url
                    'output_video_url': task.output_video_url,
                    'enhanced_prompt': task.enhanced_prompt,
                    'api_usage': task.api_usage,
                    'file_size': task.video_file_size,
                    'duration': task.duration,
                    'resolution': task.resolution
                })
            elif task.status == 'failed':
                result['error_message'] = task.error_message
            
            return result
            
        except VideoGenerationTask.DoesNotExist:
            raise VideoGenerationError(f"任务不存在: {task_id}")
        except Exception as e:
            logger.error(f"获取任务状态失败: {str(e)}")
            logger.error(traceback.format_exc())
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
