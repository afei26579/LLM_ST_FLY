from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()

# 导入AI功能模块的模型，确保Django能发现这些模型
try:
    import importlib
    ai_image_models = importlib.import_module('chat.ai-image.models')
    # 导入AI图像生成模型
    ImageGenerationTask = ai_image_models.ImageGenerationTask
    GeneratedImage = ai_image_models.GeneratedImage
    UserImageStats = ai_image_models.UserImageStats
    
    # 导入AI文档阅读模型
    ai_reading_models = importlib.import_module('chat.ai-reading.models')
    Document = ai_reading_models.Document
    DocumentAnalysis = ai_reading_models.DocumentAnalysis
    QAHistory = ai_reading_models.QAHistory
    DocumentAccess = ai_reading_models.DocumentAccess
    
    # 导入AI音频处理模型
    ai_audio_models = importlib.import_module('chat.ai-audio.models')
    AudioTask = ai_audio_models.AudioTask
    SpeechToTextTask = ai_audio_models.SpeechToTextTask
    TextToSpeechTask = ai_audio_models.TextToSpeechTask
    VoiceCloneTask = ai_audio_models.VoiceCloneTask
    UserAudioStats = ai_audio_models.UserAudioStats
    
    # 导入AI视频生成模型
    ai_video_models = importlib.import_module('chat.ai-video.models')
    VideoGenerationTask = ai_video_models.VideoGenerationTask
    GeneratedVideo = ai_video_models.GeneratedVideo
    UserVideoStats = ai_video_models.UserVideoStats
    VideoStylePreset = ai_video_models.VideoStylePreset
    
except ImportError as e:
    # 如果导入失败，记录但不影响基础聊天功能
    import logging
    logger = logging.getLogger(__name__)
    logger.warning(f"AI模块模型导入失败: {e}")

class Conversation(models.Model):
    """对话模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversations', verbose_name=_('用户'))
    title = models.CharField(max_length=255, verbose_name=_('标题'))
    custom_title = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('自定义标题'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('创建时间'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('更新时间'))
    
    # 置顶功能字段
    is_pinned = models.BooleanField(default=False, verbose_name=_('是否置顶'))
    pinned_at = models.DateTimeField(null=True, blank=True, verbose_name=_('置顶时间'))
    
    class Meta:
        verbose_name = _('对话')
        verbose_name_plural = _('对话')
        ordering = ['-is_pinned', '-pinned_at', '-updated_at']  # 置顶优先
        indexes = [
            models.Index(fields=['user', '-is_pinned', '-pinned_at']),
            models.Index(fields=['user', '-updated_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"

class Message(models.Model):
    """消息模型"""
    ROLE_CHOICES = (
        ('user', _('用户')),
        ('assistant', _('助手')),
        ('system', _('系统')),
    )
    
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages', verbose_name=_('对话'))
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, verbose_name=_('角色'))
    content = models.TextField(verbose_name=_('内容'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('创建时间'))
    
    # 用于跟踪API使用情况的字段
    tokens_used = models.IntegerField(null=True, blank=True, verbose_name=_('使用的令牌数'))
    
    class Meta:
        verbose_name = _('消息')
        verbose_name_plural = _('消息')
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.role}: {self.content[:50]}..." 