"""
AI音频处理服务
提供语音转文字、文字转语音、语音克隆等功能
"""

import os
import uuid
import logging
import requests
import traceback
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

# 由于DashScope音频功能可能不完全支持，我们先设计接口，后续根据实际API调整
# 这里先模拟一些可能的导入
try:
    # 语音识别
    from dashscope import SpeechRecognition
    HAS_SPEECH_RECOGNITION = True
except ImportError:
    HAS_SPEECH_RECOGNITION = False
    SpeechRecognition = None

try:
    # 语音合成
    from dashscope import SpeechSynthesis
    HAS_SPEECH_SYNTHESIS = True
except ImportError:
    HAS_SPEECH_SYNTHESIS = False
    SpeechSynthesis = None

from .models import (
    AudioTask, SpeechToTextTask, TextToSpeechTask, 
    VoiceCloneTask, UserAudioStats
)

logger = logging.getLogger(__name__)


class AudioProcessingError(Exception):
    """音频处理异常"""
    pass


class AIAudioService:
    """AI音频处理服务类"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'DASHSCOPE_API_KEY', os.getenv('DASHSCOPE_API_KEY'))
        if not self.api_key:
            raise AudioProcessingError("DASHSCOPE_API_KEY 未配置")
    
    def speech_to_text(
        self, 
        user_id: int, 
        audio_file=None, 
        audio_url: str = None,
        language: str = 'zh-cn',
        model: str = 'paraformer-realtime-v1'
    ) -> Dict[str, Any]:
        """
        语音转文字
        
        Args:
            user_id: 用户ID
            audio_file: 音频文件对象
            audio_url: 音频文件URL
            language: 语言代码
            model: 识别模型
            
        Returns:
            包含转换结果的字典
        """
        try:
            # 创建音频任务记录
            with transaction.atomic():
                audio_task = AudioTask.objects.create(
                    user_id=user_id,
                    task_type='speech_to_text',
                    status='pending',
                    input_audio_url=audio_url
                )
                
                # 如果有上传的文件，保存它
                if audio_file:
                    audio_task.input_audio_file = audio_file
                    audio_task.save()
                
                # 创建详细配置
                stt_task = SpeechToTextTask.objects.create(
                    audio_task=audio_task,
                    language=language,
                    model=model
                )
            
            logger.info(f"开始语音转文字任务: {audio_task.task_id}")
            
            # 更新状态为处理中
            audio_task.status = 'processing'
            audio_task.save()
            
            # 调用DashScope API (如果可用)
            if HAS_SPEECH_RECOGNITION and SpeechRecognition:
                result = self._call_speech_recognition_api(audio_task, stt_task)
            else:
                # 模拟处理（用于开发测试）
                result = self._simulate_speech_to_text(audio_task, stt_task)
            
            # 更新任务状态
            audio_task.status = 'completed'
            audio_task.completed_at = timezone.now()
            audio_task.output_text = result.get('text', '')
            audio_task.api_request_id = result.get('request_id', '')
            audio_task.api_usage = result.get('usage', {})
            audio_task.save()
            
            # 更新详细配置
            stt_task.confidence = result.get('confidence', 0.0)
            stt_task.duration = result.get('duration', 0.0)
            stt_task.save()
            
            # 更新用户统计
            self._update_user_stats(user_id)
            
            logger.info(f"语音转文字完成: {audio_task.task_id}")
            
            return {
                'task_id': audio_task.task_id,
                'text': result.get('text', ''),
                'confidence': result.get('confidence', 0.0),
                'duration': result.get('duration', 0.0),
                'usage': result.get('usage', {}),
                'status': 'completed'
            }
            
        except Exception as e:
            logger.error(f"语音转文字失败: {str(e)}")
            logger.error(traceback.format_exc())
            
            # 更新任务状态为失败
            if 'audio_task' in locals():
                audio_task.status = 'failed'
                audio_task.error_message = str(e)
                audio_task.save()
            
            raise AudioProcessingError(f"语音转文字失败: {str(e)}")
    
    def text_to_speech(
        self,
        user_id: int,
        text: str,
        voice: str = 'zhifeng_emo',
        speed: float = 1.0,
        volume: int = 50,
        pitch: float = 1.0,
        format: str = 'mp3'
    ) -> Dict[str, Any]:
        """
        文字转语音
        
        Args:
            user_id: 用户ID
            text: 要转换的文本
            voice: 音色
            speed: 语速
            volume: 音量
            pitch: 音调
            format: 输出格式
            
        Returns:
            包含生成结果的字典
        """
        try:
            # 创建音频任务记录
            with transaction.atomic():
                audio_task = AudioTask.objects.create(
                    user_id=user_id,
                    task_type='text_to_speech',
                    status='pending',
                    input_text=text
                )
                
                # 创建详细配置
                tts_task = TextToSpeechTask.objects.create(
                    audio_task=audio_task,
                    voice=voice,
                    speed=speed,
                    volume=volume,
                    pitch=pitch,
                    format=format
                )
            
            logger.info(f"开始文字转语音任务: {audio_task.task_id}")
            
            # 更新状态为处理中
            audio_task.status = 'processing'
            audio_task.save()
            
            # 调用DashScope API (如果可用)
            if HAS_SPEECH_SYNTHESIS and SpeechSynthesis:
                result = self._call_speech_synthesis_api(audio_task, tts_task)
            else:
                # 模拟处理（用于开发测试）
                result = self._simulate_text_to_speech(audio_task, tts_task)
            
            # 下载并保存生成的音频
            if result.get('audio_url'):
                saved_info = self._download_and_save_audio(
                    result['audio_url'], 
                    audio_task.task_id,
                    user_id,
                    format
                )
                result.update(saved_info)
            
            # 更新任务状态
            audio_task.status = 'completed'
            audio_task.completed_at = timezone.now()
            audio_task.output_audio_url = result.get('audio_url', '')
            audio_task.output_audio_file = result.get('saved_path', '')
            audio_task.api_request_id = result.get('request_id', '')
            audio_task.api_usage = result.get('usage', {})
            audio_task.save()
            
            # 更新详细配置
            tts_task.audio_duration = result.get('duration', 0.0)
            tts_task.file_size = result.get('file_size', 0)
            tts_task.save()
            
            # 更新用户统计
            self._update_user_stats(user_id)
            
            logger.info(f"文字转语音完成: {audio_task.task_id}")
            
            return {
                'task_id': audio_task.task_id,
                'audio_url': result.get('saved_url', result.get('audio_url', '')),
                'duration': result.get('duration', 0.0),
                'file_size': result.get('file_size', 0),
                'usage': result.get('usage', {}),
                'status': 'completed'
            }
            
        except Exception as e:
            logger.error(f"文字转语音失败: {str(e)}")
            logger.error(traceback.format_exc())
            
            # 更新任务状态为失败
            if 'audio_task' in locals():
                audio_task.status = 'failed'
                audio_task.error_message = str(e)
                audio_task.save()
            
            raise AudioProcessingError(f"文字转语音失败: {str(e)}")
    
    def voice_clone(
        self,
        user_id: int,
        reference_audio,
        reference_text: str,
        target_text: str,
        model: str = 'sambert-v1'
    ) -> Dict[str, Any]:
        """
        语音克隆
        
        Args:
            user_id: 用户ID
            reference_audio: 参考音频文件
            reference_text: 参考文本
            target_text: 目标文本
            model: 克隆模型
            
        Returns:
            包含克隆结果的字典
        """
        try:
            # 创建音频任务记录
            with transaction.atomic():
                audio_task = AudioTask.objects.create(
                    user_id=user_id,
                    task_type='voice_clone',
                    status='pending',
                    input_text=target_text
                )
                
                # 创建详细配置
                clone_task = VoiceCloneTask.objects.create(
                    audio_task=audio_task,
                    reference_audio=reference_audio,
                    reference_text=reference_text,
                    target_text=target_text,
                    model=model
                )
            
            logger.info(f"开始语音克隆任务: {audio_task.task_id}")
            
            # 更新状态为处理中
            audio_task.status = 'processing'
            audio_task.save()
            
            # 语音克隆功能暂时使用模拟实现
            result = self._simulate_voice_clone(audio_task, clone_task)
            
            # 更新任务状态
            audio_task.status = 'completed'
            audio_task.completed_at = timezone.now()
            audio_task.output_audio_url = result.get('audio_url', '')
            audio_task.api_request_id = result.get('request_id', '')
            audio_task.api_usage = result.get('usage', {})
            audio_task.save()
            
            # 更新详细配置
            clone_task.similarity_score = result.get('similarity_score', 0.0)
            clone_task.save()
            
            # 更新用户统计
            self._update_user_stats(user_id)
            
            logger.info(f"语音克隆完成: {audio_task.task_id}")
            
            return {
                'task_id': audio_task.task_id,
                'audio_url': result.get('audio_url', ''),
                'similarity_score': result.get('similarity_score', 0.0),
                'usage': result.get('usage', {}),
                'status': 'completed'
            }
            
        except Exception as e:
            logger.error(f"语音克隆失败: {str(e)}")
            logger.error(traceback.format_exc())
            
            # 更新任务状态为失败
            if 'audio_task' in locals():
                audio_task.status = 'failed'
                audio_task.error_message = str(e)
                audio_task.save()
            
            raise AudioProcessingError(f"语音克隆失败: {str(e)}")
    
    def _call_speech_recognition_api(self, audio_task: AudioTask, stt_task: SpeechToTextTask) -> Dict[str, Any]:
        """调用DashScope语音识别API"""
        try:
            # 获取音频文件路径或URL
            audio_source = None
            if audio_task.input_audio_file:
                audio_source = audio_task.input_audio_file.path
            elif audio_task.input_audio_url:
                audio_source = audio_task.input_audio_url
            else:
                raise AudioProcessingError("没有提供音频源")
            
            # 调用API（示例代码，需要根据实际API调整）
            response = SpeechRecognition.call(
                api_key=self.api_key,
                model=stt_task.model,
                audio=audio_source,
                language=stt_task.language,
                format=stt_task.format,
                sample_rate=stt_task.sample_rate
            )
            
            if response.status_code == HTTPStatus.OK:
                return {
                    'text': response.output.get('text', ''),
                    'confidence': response.output.get('confidence', 0.0),
                    'duration': response.output.get('duration', 0.0),
                    'request_id': getattr(response, 'request_id', ''),
                    'usage': dict(response.usage.__dict__) if hasattr(response, 'usage') else {}
                }
            else:
                raise AudioProcessingError(f"API调用失败: {response.message}")
                
        except Exception as e:
            logger.error(f"语音识别API调用失败: {str(e)}")
            raise AudioProcessingError(f"语音识别API调用失败: {str(e)}")
    
    def _call_speech_synthesis_api(self, audio_task: AudioTask, tts_task: TextToSpeechTask) -> Dict[str, Any]:
        """调用DashScope语音合成API"""
        try:
            # 调用API（示例代码，需要根据实际API调整）
            response = SpeechSynthesis.call(
                api_key=self.api_key,
                text=audio_task.input_text,
                voice=tts_task.voice,
                speed=tts_task.speed,
                volume=tts_task.volume,
                pitch=tts_task.pitch,
                format=tts_task.format,
                sample_rate=tts_task.sample_rate
            )
            
            if response.status_code == HTTPStatus.OK:
                return {
                    'audio_url': response.output.get('audio_url', ''),
                    'duration': response.output.get('duration', 0.0),
                    'request_id': getattr(response, 'request_id', ''),
                    'usage': dict(response.usage.__dict__) if hasattr(response, 'usage') else {}
                }
            else:
                raise AudioProcessingError(f"API调用失败: {response.message}")
                
        except Exception as e:
            logger.error(f"语音合成API调用失败: {str(e)}")
            raise AudioProcessingError(f"语音合成API调用失败: {str(e)}")
    
    def _simulate_speech_to_text(self, audio_task: AudioTask, stt_task: SpeechToTextTask) -> Dict[str, Any]:
        """模拟语音转文字（用于开发测试）"""
        import time
        time.sleep(2)  # 模拟处理时间
        
        return {
            'text': '这是模拟的语音识别结果，用于开发测试。',
            'confidence': 0.95,
            'duration': 5.0,
            'request_id': f'sim-{uuid.uuid4()}',
            'usage': {
                'audio_duration': 5.0,
                'characters': 20
            }
        }
    
    def _simulate_text_to_speech(self, audio_task: AudioTask, tts_task: TextToSpeechTask) -> Dict[str, Any]:
        """模拟文字转语音（用于开发测试）"""
        import time
        time.sleep(2)  # 模拟处理时间
        
        # 模拟生成一个音频URL
        fake_url = f"https://example.com/audio/{audio_task.task_id}.{tts_task.format}"
        
        return {
            'audio_url': fake_url,
            'duration': len(audio_task.input_text) * 0.1,  # 模拟时长
            'request_id': f'sim-{uuid.uuid4()}',
            'usage': {
                'characters': len(audio_task.input_text),
                'audio_duration': len(audio_task.input_text) * 0.1
            }
        }
    
    def _simulate_voice_clone(self, audio_task: AudioTask, clone_task: VoiceCloneTask) -> Dict[str, Any]:
        """模拟语音克隆（用于开发测试）"""
        import time
        time.sleep(5)  # 模拟处理时间
        
        fake_url = f"https://example.com/cloned-audio/{audio_task.task_id}.mp3"
        
        return {
            'audio_url': fake_url,
            'similarity_score': 0.88,
            'request_id': f'sim-{uuid.uuid4()}',
            'usage': {
                'reference_duration': 10.0,
                'generated_duration': len(clone_task.target_text) * 0.1
            }
        }
    
    def _download_and_save_audio(
        self, 
        audio_url: str, 
        task_id: str, 
        user_id: int,
        format: str = 'mp3'
    ) -> Dict[str, Any]:
        """下载并保存音频文件"""
        try:
            # 生成保存路径
            date_str = timezone.now().strftime('%Y%m%d')
            filename = f"{task_id}.{format}"
            save_path = f"ai-audio/{user_id}/{date_str}/{filename}"
            
            # 下载音频文件（模拟）
            # 注意：这里是模拟实现，实际需要根据真实URL下载
            if audio_url.startswith('https://example.com'):
                # 模拟音频数据
                fake_audio_data = b'fake audio data for testing'
                file_size = len(fake_audio_data)
                
                # 保存文件
                saved_path = default_storage.save(
                    save_path,
                    ContentFile(fake_audio_data)
                )
            else:
                # 真实下载
                response = requests.get(audio_url, timeout=30)
                response.raise_for_status()
                
                file_size = len(response.content)
                saved_path = default_storage.save(
                    save_path,
                    ContentFile(response.content)
                )
            
            # 生成访问URL
            saved_url = default_storage.url(saved_path)
            
            return {
                'saved_path': saved_path,
                'saved_url': saved_url,
                'filename': filename,
                'file_size': file_size,
                'download_time': timezone.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"下载音频文件失败: {str(e)}")
            raise AudioProcessingError(f"下载音频文件失败: {str(e)}")
    
    def _update_user_stats(self, user_id: int):
        """更新用户统计"""
        try:
            UserAudioStats.update_stats(user_id)
        except Exception as e:
            logger.error(f"更新用户音频统计失败: {str(e)}")
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """获取任务状态"""
        try:
            task = AudioTask.objects.get(task_id=task_id)
            
            result = {
                'task_id': task.task_id,
                'status': task.status,
                'task_type': task.task_type,
                'created_at': task.created_at.isoformat(),
                'updated_at': task.updated_at.isoformat()
            }
            
            if task.status == 'completed':
                result.update({
                    'completed_at': task.completed_at.isoformat() if task.completed_at else None,
                    'output_text': task.output_text,
                    'output_audio_url': task.output_audio_url,
                    'api_usage': task.api_usage
                })
            elif task.status == 'failed':
                result['error_message'] = task.error_message
            
            return result
            
        except AudioTask.DoesNotExist:
            raise AudioProcessingError(f"任务不存在: {task_id}")
        except Exception as e:
            logger.error(f"获取任务状态失败: {str(e)}")
            raise AudioProcessingError(f"获取任务状态失败: {str(e)}")
    
    def get_user_audio_history(self, user_id: int, task_type: str = None, limit: int = 20) -> List[Dict[str, Any]]:
        """获取用户音频处理历史"""
        try:
            query = AudioTask.objects.filter(user_id=user_id)
            
            if task_type:
                query = query.filter(task_type=task_type)
            
            tasks = query.order_by('-created_at')[:limit]
            
            history = []
            for task in tasks:
                item = {
                    'task_id': task.task_id,
                    'task_type': task.task_type,
                    'status': task.status,
                    'created_at': task.created_at.isoformat(),
                    'input_text': task.input_text,
                    'output_text': task.output_text,
                    'output_audio_url': task.output_audio_url
                }
                
                if task.completed_at:
                    item['completed_at'] = task.completed_at.isoformat()
                
                if task.error_message:
                    item['error_message'] = task.error_message
                
                history.append(item)
            
            return history
            
        except Exception as e:
            logger.error(f"获取用户音频历史失败: {str(e)}")
            raise AudioProcessingError(f"获取用户音频历史失败: {str(e)}")


# 创建服务实例
ai_audio_service = AIAudioService()
