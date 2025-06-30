from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class Conversation(models.Model):
    """对话模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversations', verbose_name=_('用户'))
    title = models.CharField(max_length=255, verbose_name=_('标题'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('创建时间'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('更新时间'))
    
    class Meta:
        verbose_name = _('对话')
        verbose_name_plural = _('对话')
        ordering = ['-updated_at']
    
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