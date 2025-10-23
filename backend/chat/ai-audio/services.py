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
            
            # 调用真实的 DashScope API
            result = self._call_speech_recognition_api(audio_task, stt_task)
            
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
                'result_text': result.get('text', ''),  # 前端使用 result_text 字段
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
        voice: str = 'Cherry',
        language_type: str = 'Chinese',
        format: str = 'wav'
    ) -> Dict[str, Any]:
        """
        文字转语音
        
        Args:
            user_id: 用户ID
            text: 要转换的文本
            voice: 音色
            language_type: 语言类型
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
                    language_type=language_type,
                    format=format
                )
            
            logger.info(f"开始文字转语音任务: {audio_task.task_id}")
            
            # 更新状态为处理中
            audio_task.status = 'processing'
            audio_task.save()
            
            # 调用真实的 DashScope API
            result = self._call_speech_synthesis_api(audio_task, tts_task)
            
            # 下载并保存生成的音频到本地 media/ai-audio/ 目录
            if result.get('audio_url'):
                logger.info(f"开始下载音频文件: {result['audio_url']}")
                saved_info = self._download_and_save_audio(
                    result['audio_url'], 
                    audio_task.task_id,
                    user_id,
                    format
                )
                result.update(saved_info)
                logger.info(f"音频文件已保存到: {saved_info['saved_path']}")
            
            # 更新任务状态
            audio_task.status = 'completed'
            audio_task.completed_at = timezone.now()
            audio_task.output_audio_url = result.get('audio_url', '')  # DashScope 原始临时URL
            audio_task.output_audio_file = result.get('saved_path', '')  # 本地保存的文件路径
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
                'audio_url': result.get('saved_url', result.get('audio_url', '')),  # 优先返回本地URL
                'original_url': result.get('audio_url', ''),  # DashScope 原始URL
                'saved_path': result.get('saved_path', ''),  # 本地文件路径
                'audio_id': result.get('audio_id', ''),
                'expires_at': result.get('expires_at', ''),
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
    
    def _call_speech_recognition_api_stream(self, audio_task: AudioTask, stt_task: SpeechToTextTask):
        """调用DashScope语音识别API - 流式输出版本"""
        try:
            import dashscope
            from http import HTTPStatus
            import json
            
            # 获取音频文件的绝对路径
            if not audio_task.input_audio_file:
                raise AudioProcessingError("没有提供音频文件")
            
            # 获取文件的绝对路径
            audio_file_path = audio_task.input_audio_file.path
            
            # 添加 file:// 前缀（必须使用绝对路径）
            audio_file_url = f"file://{audio_file_path}"
            
            logger.info(f"准备调用语音识别 API（流式）: 文件路径={audio_file_path}")
            
            # 构建 messages
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"audio": audio_file_url}
                    ]
                }
            ]
            
            # 调用 MultiModalConversation API（流式）
            responses = dashscope.MultiModalConversation.call(
                model="qwen-audio-asr",#qwen-audio-turbo-latest
                messages=messages,
                stream=True,
                incremental_output=True,
                result_format="message"
            )
            
            full_content = ""
            
            # 流式输出
            for response in responses:
                if response.status_code == HTTPStatus.OK:
                    # 提取当前块的文本
                    if response.output.choices[0].message.content:
                        chunk_text = response.output.choices[0].message.content[0]["text"]
                        full_content += chunk_text
                        
                        # 生成流式数据
                        yield {
                            'type': 'chunk',
                            'text': chunk_text,
                            'full_text': full_content
                        }
                else:
                    error_msg = f"API调用失败: {response.message}"
                    logger.error(error_msg)
                    yield {
                        'type': 'error',
                        'message': error_msg
                    }
                    raise AudioProcessingError(error_msg)
            
            # 发送完成信号
            logger.info(f"语音识别完成（流式）: text_length={len(full_content)}")
            yield {
                'type': 'done',
                'text': full_content,
                'confidence': 0.95,
                'request_id': response.request_id if hasattr(response, 'request_id') else ''
            }
                
        except Exception as e:
            logger.error(f"语音识别API调用失败（流式）: {str(e)}")
            logger.error(traceback.format_exc())
            yield {
                'type': 'error',
                'message': str(e)
            }
    
    def _call_speech_synthesis_api(self, audio_task: AudioTask, tts_task: TextToSpeechTask) -> Dict[str, Any]:
        """调用DashScope语音合成API - 使用 qwen3-tts-flash 模型"""
        try:
            import dashscope
            from http import HTTPStatus
            
            # 调用 MultiModalConversation API（参考 demo.py）
            response = dashscope.audio.qwen_tts.SpeechSynthesizer.call(
                model="qwen3-tts-flash-2025-09-18",
                api_key=self.api_key,
                text=audio_task.input_text,
                voice=tts_task.voice,
                language_type=tts_task.language_type,
              
            )

            if response.status_code == HTTPStatus.OK:
                # 获取音频URL
                audio_url = response.output.audio['url']
                audio_id = response.output.audio['id']
                expires_at = response.output.audio['expires_at']
                
                # 获取使用情况
                usage = {
                    'characters': response.usage.characters if hasattr(response.usage, 'characters') else len(audio_task.input_text)
                }
                
                logger.info(f"TTS API调用成功: audio_id={audio_id}, url={audio_url}")
                
                return {
                    'audio_url': audio_url,
                    'audio_id': audio_id,
                    'expires_at': expires_at,
                    'duration': 0.0,  # API不直接返回时长
                    'request_id': response.request_id,
                    'usage': usage
                }
            else:
                raise AudioProcessingError(f"API调用失败: {response.message}")
                
        except Exception as e:
            logger.error(f"语音合成API调用失败: {str(e)}")
            logger.error(traceback.format_exc())
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
        format: str = 'wav'
    ) -> Dict[str, Any]:
        """
        下载并保存音频文件到 backend/media/ai-audio/ 目录
        
        Args:
            audio_url: DashScope 返回的音频URL
            task_id: 任务ID
            user_id: 用户ID
            format: 音频格式（wav/mp3/pcm）
            
        Returns:
            包含保存信息的字典
        """
        try:
            # 生成保存路径：ai-audio/{user_id}/{YYYYMMDD}/{task_id}.{format}
            date_str = timezone.now().strftime('%Y%m%d')
            filename = f"{task_id}.{format}"
            save_path = f"ai-audio/{user_id}/{date_str}/{filename}"
            
            logger.info(f"准备下载音频 - URL: {audio_url[:100]}...")
            logger.info(f"保存路径: media/{save_path}")
            
            # 下载音频文件
            response = requests.get(audio_url, timeout=60)
            response.raise_for_status()
            
            audio_content = response.content
            file_size = len(audio_content)
            
            logger.info(f"音频下载成功 - 大小: {file_size} bytes ({file_size/1024:.2f} KB)")
            
            # 保存文件到 media/ai-audio/ 目录
            saved_path = default_storage.save(
                save_path,
                ContentFile(audio_content)
            )
            
            # 生成访问URL（Django media URL）
            saved_url = default_storage.url(saved_path)
            
            logger.info(f"音频保存成功 - 文件路径: {saved_path}")
            logger.info(f"访问URL: {saved_url}")
            
            return {
                'saved_path': saved_path,
                'saved_url': saved_url,
                'filename': filename,
                'file_size': file_size,
                'download_time': timezone.now().isoformat()
            }
            
        except requests.Timeout:
            logger.error(f"下载音频超时: URL={audio_url}")
            raise AudioProcessingError("下载音频文件超时，请重试")
        except requests.RequestException as e:
            logger.error(f"下载音频失败（网络错误）: {str(e)}")
            raise AudioProcessingError(f"下载音频文件失败: {str(e)}")
        except Exception as e:
            logger.error(f"保存音频文件失败: {str(e)}")
            logger.error(traceback.format_exc())
            raise AudioProcessingError(f"保存音频文件失败: {str(e)}")
    
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
