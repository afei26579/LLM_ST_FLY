"""
智能体数据模型
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid

User = get_user_model()


class AgentType(models.TextChoices):
    """智能体类型"""
    TRAVEL_ASSISTANT = 'travel_assistant', '旅游助手'
    POETRY_PAINTING = 'poetry_painting', '诗词绘画'
    CUSTOMER_SERVICE = 'customer_service', '客服助手'


class Agent(models.Model):
    """智能体基础模型"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, verbose_name='智能体名称')
    type = models.CharField(
        max_length=50, 
        choices=AgentType.choices,
        verbose_name='智能体类型'
    )
    description = models.TextField(verbose_name='智能体描述')
    avatar = models.URLField(blank=True, null=True, verbose_name='头像URL')
    system_prompt = models.TextField(verbose_name='系统提示词')
    greeting_message = models.CharField(
        max_length=500, 
        verbose_name='欢迎语',
        default='您好！我是您的智能助手，有什么可以帮助您的吗？'
    )
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'agent_agent'
        verbose_name = '智能体'
        verbose_name_plural = '智能体'
        ordering = ['created_at']

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"


class Conversation(models.Model):
    """对话会话"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, verbose_name='智能体')
    title = models.CharField(max_length=200, verbose_name='对话标题')
    started_at = models.DateTimeField(auto_now_add=True, verbose_name='开始时间')
    last_message_at = models.DateTimeField(auto_now=True, verbose_name='最后消息时间')
    is_active = models.BooleanField(default=True, verbose_name='是否活跃')
    message_count = models.PositiveIntegerField(default=0, verbose_name='消息数量')

    class Meta:
        db_table = 'agent_conversation'
        verbose_name = '对话会话'
        verbose_name_plural = '对话会话'
        ordering = ['-last_message_at']
        indexes = [
            models.Index(fields=['user', 'agent']),
            models.Index(fields=['last_message_at']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.agent.name}: {self.title}"


class Message(models.Model):
    """消息记录"""
    class MessageType(models.TextChoices):
        USER = 'user', '用户消息'
        ASSISTANT = 'assistant', '助手回复'
        SYSTEM = 'system', '系统消息'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(
        Conversation, 
        on_delete=models.CASCADE, 
        related_name='messages',
        verbose_name='对话会话'
    )
    type = models.CharField(
        max_length=20,
        choices=MessageType.choices,
        verbose_name='消息类型'
    )
    content = models.TextField(verbose_name='消息内容')
    metadata = models.JSONField(blank=True, null=True, verbose_name='元数据')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    tokens_used = models.PositiveIntegerField(default=0, verbose_name='消耗Token数')

    class Meta:
        db_table = 'agent_message'
        verbose_name = '消息记录'
        verbose_name_plural = '消息记录'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['conversation', 'created_at']),
            models.Index(fields=['type']),
        ]

    def __str__(self):
        return f"{self.get_type_display()}: {self.content[:50]}..."


class UserAgentStats(models.Model):
    """用户智能体使用统计"""
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='agent_stats',
        verbose_name='用户'
    )
    total_conversations = models.PositiveIntegerField(default=0, verbose_name='总对话数')
    total_messages = models.PositiveIntegerField(default=0, verbose_name='总消息数')
    total_tokens_used = models.PositiveIntegerField(default=0, verbose_name='总Token消耗')
    travel_conversations = models.PositiveIntegerField(default=0, verbose_name='旅游助手对话数')
    poetry_conversations = models.PositiveIntegerField(default=0, verbose_name='诗词绘画对话数')
    service_conversations = models.PositiveIntegerField(default=0, verbose_name='客服助手对话数')
    last_used_at = models.DateTimeField(null=True, blank=True, verbose_name='最后使用时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'agent_user_stats'
        verbose_name = '用户智能体统计'
        verbose_name_plural = '用户智能体统计'

    def __str__(self):
        return f"{self.user.username} - 智能体使用统计"

    def update_stats(self, agent_type: str, new_conversation: bool = False, tokens: int = 0):
        """更新统计数据"""
        if new_conversation:
            self.total_conversations += 1
            if agent_type == AgentType.TRAVEL_ASSISTANT:
                self.travel_conversations += 1
            elif agent_type == AgentType.POETRY_PAINTING:
                self.poetry_conversations += 1
            elif agent_type == AgentType.CUSTOMER_SERVICE:
                self.service_conversations += 1
        
        self.total_messages += 1
        self.total_tokens_used += tokens
        self.last_used_at = timezone.now()
        self.save()
