"""
客服系统数据模型
"""
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomerServiceSession(models.Model):
    """客服会话"""
    STATUS_CHOICES = [
        ('active', '进行中'),
        ('resolved', '已解决'),
        ('transferred', '已转人工'),
        ('closed', '已关闭'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cs_sessions')
    session_id = models.CharField(max_length=100, unique=True, db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    title = models.CharField(max_length=255, blank=True, default='客服咨询')
    
    # 统计信息
    message_count = models.IntegerField(default=0)
    satisfaction_score = models.FloatField(null=True, blank=True)
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'agent_customer_service_session'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.session_id} - {self.status}"


class CustomerServiceMessage(models.Model):
    """客服消息"""
    ROLE_CHOICES = [
        ('user', '用户'),
        ('assistant', 'AI助手'),
        ('system', '系统'),
        ('human', '人工客服'),
    ]

    session = models.ForeignKey(
        CustomerServiceSession, 
        on_delete=models.CASCADE, 
        related_name='messages'
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    
    # AI分析结果
    intent = models.CharField(max_length=50, blank=True)
    entities = models.JSONField(default=dict, blank=True)
    confidence = models.FloatField(null=True, blank=True)
    
    # 工具调用结果
    tools_result = models.JSONField(default=dict, blank=True)
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'agent_customer_service_message'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['session', 'created_at']),
            models.Index(fields=['intent']),
        ]

    def __str__(self):
        return f"{self.session.session_id} - {self.role}: {self.content[:50]}"


class CustomerServiceKnowledgeBase(models.Model):
    """客服知识库"""
    CATEGORY_CHOICES = [
        ('product', '产品咨询'),
        ('order', '订单问题'),
        ('technical', '技术支持'),
        ('policy', '政策条款'),
        ('faq', '常见问题'),
    ]

    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    question = models.TextField()
    answer = models.TextField()
    keywords = models.JSONField(default=list, blank=True)
    
    # 使用统计
    use_count = models.IntegerField(default=0)
    helpful_count = models.IntegerField(default=0)
    
    # 状态
    is_active = models.BooleanField(default=True)
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'agent_customer_service_knowledge'
        ordering = ['-use_count', '-created_at']
        indexes = [
            models.Index(fields=['category', 'is_active']),
        ]

    def __str__(self):
        return f"{self.category} - {self.question[:50]}"


class CustomerServiceStats(models.Model):
    """客服统计信息"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cs_stats')
    
    # 会话统计
    total_sessions = models.IntegerField(default=0)
    resolved_sessions = models.IntegerField(default=0)
    transferred_sessions = models.IntegerField(default=0)
    
    # 消息统计
    total_messages = models.IntegerField(default=0)
    avg_session_messages = models.FloatField(default=0.0)
    
    # 满意度
    avg_satisfaction_score = models.FloatField(null=True, blank=True)
    
    # 时间戳
    last_session_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'agent_customer_service_stats'

    def __str__(self):
        return f"{self.user.username} - Stats"

