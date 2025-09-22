"""
AI音频相关模型
包括语音转文字、文字转语音、语音克隆等功能的数据模型
"""

import os
import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.files.storage import default_storage
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


class AudioTask(models.Model):
    """音频处理任务基础模型"""
    TASK_TYPE_CHOICES = [
        ('speech_to_text', _('语音转文字')),
        ('text_to_speech', _('文字转语音')),
        ('voice_clone', _('语音克隆')),
    ]
    
    STATUS_CHOICES = [
        ('pending', _('待处理')),
        ('processing', _('处理中')),
        ('completed', _('已完成')),
        ('failed', _('失败')),
    ]
    
    task_id = models.CharField(max_length=100, unique=True, verbose_name=_('任务ID'))
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('用户'))
    task_type = models.CharField(max_length=20, choices=TASK_TYPE_CHOICES, verbose_name=_('任务类型'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name=_('状态'))
    
    # 输入相关
    input_text = models.TextField(blank=True, null=True, verbose_name=_('输入文本'))
    input_audio_file = models.FileField(upload_to='audio-inputs/', blank=True, null=True, verbose_name=_('输入音频文件'))
    input_audio_url = models.URLField(max_length=1000, blank=True, null=True, verbose_name=_('输入音频URL'))
    
    # 输出相关
    output_text = models.TextField(blank=True, null=True, verbose_name=_('输出文本'))
    output_audio_file = models.FileField(upload_to='audio-outputs/', blank=True, null=True, verbose_name=_('输出音频文件'))
    output_audio_url = models.URLField(max_length=1000, blank=True, null=True, verbose_name=_('输出音频URL'))
    
    # API相关
    api_request_id = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('API请求ID'))
    api_usage = models.JSONField(default=dict, blank=True, verbose_name=_('API使用统计'))
    error_message = models.TextField(blank=True, null=True, verbose_name=_('错误信息'))
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('创建时间'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('更新时间'))
    completed_at = models.DateTimeField(blank=True, null=True, verbose_name=_('完成时间'))
    
    class Meta:
        verbose_name = _('音频任务')
        verbose_name_plural = _('音频任务')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'task_type']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.get_task_type_display()} - {self.task_id}"
    
    def save(self, *args, **kwargs):
        if not self.task_id:
            self.task_id = str(uuid.uuid4())
        super().save(*args, **kwargs)


class SpeechToTextTask(models.Model):
    """语音转文字任务详细配置"""
    audio_task = models.OneToOneField(AudioTask, on_delete=models.CASCADE, primary_key=True, verbose_name=_('音频任务'))
    
    # 语音识别配置
    language = models.CharField(max_length=10, default='zh-cn', verbose_name=_('语言'))
    model = models.CharField(max_length=50, default='paraformer-realtime-v1', verbose_name=_('识别模型'))
    format = models.CharField(max_length=10, default='pcm', verbose_name=_('音频格式'))
    sample_rate = models.IntegerField(default=16000, verbose_name=_('采样率'))
    
    # 识别结果
    confidence = models.FloatField(blank=True, null=True, verbose_name=_('置信度'))
    duration = models.FloatField(blank=True, null=True, verbose_name=_('音频时长(秒)'))
    
    class Meta:
        verbose_name = _('语音转文字任务')
        verbose_name_plural = _('语音转文字任务')


class TextToSpeechTask(models.Model):
    """文字转语音任务详细配置"""
    audio_task = models.OneToOneField(AudioTask, on_delete=models.CASCADE, primary_key=True, verbose_name=_('音频任务'))
    
    # 语音合成配置
    voice = models.CharField(max_length=50, default='zhifeng_emo', verbose_name=_('音色'))
    speed = models.FloatField(default=1.0, verbose_name=_('语速'))
    volume = models.IntegerField(default=50, verbose_name=_('音量'))
    pitch = models.FloatField(default=1.0, verbose_name=_('音调'))
    format = models.CharField(max_length=10, default='mp3', verbose_name=_('输出格式'))
    sample_rate = models.IntegerField(default=22050, verbose_name=_('采样率'))
    
    # 合成结果
    audio_duration = models.FloatField(blank=True, null=True, verbose_name=_('音频时长(秒)'))
    file_size = models.IntegerField(blank=True, null=True, verbose_name=_('文件大小(字节)'))
    
    class Meta:
        verbose_name = _('文字转语音任务')
        verbose_name_plural = _('文字转语音任务')


class VoiceCloneTask(models.Model):
    """语音克隆任务详细配置"""
    audio_task = models.OneToOneField(AudioTask, on_delete=models.CASCADE, primary_key=True, verbose_name=_('音频任务'))
    
    # 语音克隆配置
    reference_audio = models.FileField(upload_to='voice-references/', verbose_name=_('参考音频'))
    reference_text = models.TextField(verbose_name=_('参考文本'))
    target_text = models.TextField(verbose_name=_('目标文本'))
    model = models.CharField(max_length=50, default='sambert-v1', verbose_name=_('克隆模型'))
    
    # 克隆结果
    similarity_score = models.FloatField(blank=True, null=True, verbose_name=_('相似度评分'))
    
    class Meta:
        verbose_name = _('语音克隆任务')
        verbose_name_plural = _('语音克隆任务')


class UserAudioStats(models.Model):
    """用户音频使用统计"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, verbose_name=_('用户'))
    
    # 使用统计
    total_speech_to_text = models.IntegerField(default=0, verbose_name=_('语音转文字次数'))
    total_text_to_speech = models.IntegerField(default=0, verbose_name=_('文字转语音次数'))
    total_voice_clone = models.IntegerField(default=0, verbose_name=_('语音克隆次数'))
    
    # 存储统计
    total_audio_duration = models.FloatField(default=0, verbose_name=_('总音频时长(秒)'))
    total_storage_used = models.BigIntegerField(default=0, verbose_name=_('总存储使用(字节)'))
    
    # 时间统计
    last_audio_at = models.DateTimeField(blank=True, null=True, verbose_name=_('最后音频处理时间'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('创建时间'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('更新时间'))
    
    class Meta:
        verbose_name = _('用户音频统计')
        verbose_name_plural = _('用户音频统计')
    
    def __str__(self):
        return f"{self.user.username} - 音频统计"
    
    @classmethod
    def update_stats(cls, user_id: int):
        """更新用户音频使用统计"""
        try:
            from django.db.models import Sum, Count, Q
            from django.db.models.functions import Coalesce
            from django.db.models import Value
            
            # 获取或创建统计记录
            stats, created = cls.objects.get_or_create(user_id=user_id)
            
            # 统计各类型任务数量
            task_counts = AudioTask.objects.filter(
                user_id=user_id,
                status='completed'
            ).values('task_type').annotate(count=Count('id'))
            
            # 重置计数
            stats.total_speech_to_text = 0
            stats.total_text_to_speech = 0
            stats.total_voice_clone = 0
            
            # 更新任务类型统计
            for item in task_counts:
                if item['task_type'] == 'speech_to_text':
                    stats.total_speech_to_text = item['count']
                elif item['task_type'] == 'text_to_speech':
                    stats.total_text_to_speech = item['count']
                elif item['task_type'] == 'voice_clone':
                    stats.total_voice_clone = item['count']
            
            # 计算总音频时长（从TextToSpeechTask和SpeechToTextTask）
            try:
                # TTS任务的音频时长
                tts_duration = TextToSpeechTask.objects.filter(
                    audio_task__user_id=user_id,
                    audio_task__status='completed',
                    audio_duration__isnull=False
                ).aggregate(
                    total=Coalesce(Sum('audio_duration'), Value(0))
                )['total'] or 0
                
                # STT任务的音频时长
                stt_duration = SpeechToTextTask.objects.filter(
                    audio_task__user_id=user_id,
                    audio_task__status='completed',
                    duration__isnull=False
                ).aggregate(
                    total=Coalesce(Sum('duration'), Value(0))
                )['total'] or 0
                
                stats.total_audio_duration = float(tts_duration) + float(stt_duration)
                
            except Exception as e:
                logger.warning(f"计算音频时长失败: {str(e)}")
                stats.total_audio_duration = 0
            
            # 计算存储使用量（TTS任务的文件大小）
            try:
                storage_used = TextToSpeechTask.objects.filter(
                    audio_task__user_id=user_id,
                    audio_task__status='completed',
                    file_size__isnull=False
                ).aggregate(
                    total=Coalesce(Sum('file_size'), Value(0))
                )['total'] or 0
                
                stats.total_storage_used = storage_used
                
            except Exception as e:
                logger.warning(f"计算存储使用量失败: {str(e)}")
                stats.total_storage_used = 0
            
            # 更新最后处理时间
            try:
                last_task = AudioTask.objects.filter(
                    user_id=user_id,
                    status='completed'
                ).order_by('-completed_at').first()
                
                if last_task and last_task.completed_at:
                    stats.last_audio_at = last_task.completed_at
            except Exception as e:
                logger.warning(f"更新最后处理时间失败: {str(e)}")
            
            stats.save()
            logger.info(f"用户音频统计更新成功: user_id={user_id}")
            
        except Exception as e:
            logger.error(f"更新用户音频统计失败: user_id={user_id}, error={str(e)}")
            import traceback
            logger.error(f"错误堆栈: {traceback.format_exc()}")
