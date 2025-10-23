"""
诗词绘画智能体数据模型
"""
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class PoetryPaintingConversation(models.Model):
    """诗词绘画对话"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='poetry_painting_conversations')
    title = models.CharField(max_length=255, verbose_name='对话标题')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'agent_poetry_painting_conversation'
        ordering = ['-updated_at']
        verbose_name = '诗词绘画对话'
        verbose_name_plural = verbose_name
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"


class PoetryPaintingWork(models.Model):
    """诗词绘画作品"""
    POETRY_FORMAT_CHOICES = [
        ('five_jueju', '五言绝句'),
        ('seven_jueju', '七言绝句'),
        ('five_lvshi', '五言律诗'),
        ('seven_lvshi', '七言律诗'),
        ('ci', '词'),
    ]
    
    PAINTING_STYLE_CHOICES = [
        ('chinese_ink', '水墨画'),
        ('gongbi', '工笔画'),
        ('oil_painting', '油画风格'),
        ('watercolor', '水彩风格'),
        ('modern', '现代艺术'),
    ]
    
    conversation = models.ForeignKey(
        PoetryPaintingConversation, 
        on_delete=models.CASCADE,
        related_name='works',
        verbose_name='所属对话'
    )
    
    # 诗词信息
    poetry_theme = models.CharField(max_length=100, verbose_name='诗词主题')
    poetry_format = models.CharField(max_length=20, choices=POETRY_FORMAT_CHOICES, verbose_name='诗词格式')
    poetry_style = models.CharField(max_length=50, verbose_name='诗词风格')
    poetry_content = models.TextField(verbose_name='诗词内容')
    poetry_title = models.CharField(max_length=100, blank=True, verbose_name='诗词标题')
    poetry_analysis = models.JSONField(blank=True, null=True, verbose_name='诗词分析')
    
    # 绘画信息
    painting_prompt = models.TextField(verbose_name='绘画提示词')
    painting_style = models.CharField(max_length=20, choices=PAINTING_STYLE_CHOICES, verbose_name='绘画风格')
    painting_url = models.URLField(max_length=1000, blank=True, null=True, verbose_name='画作URL')
    painting_local_path = models.CharField(max_length=500, blank=True, verbose_name='本地路径')
    
    # 元数据
    langgraph_state = models.JSONField(blank=True, null=True, verbose_name='LangGraph状态')
    iteration_count = models.IntegerField(default=1, verbose_name='迭代次数')
    user_rating = models.IntegerField(blank=True, null=True, verbose_name='用户评分')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        db_table = 'agent_poetry_painting_work'
        ordering = ['-created_at']
        verbose_name = '诗词绘画作品'
        verbose_name_plural = verbose_name
        indexes = [
            models.Index(fields=['conversation', '-created_at']),
            models.Index(fields=['poetry_theme']),
        ]
    
    def __str__(self):
        return f"{self.poetry_title or self.poetry_theme} - {self.created_at.strftime('%Y-%m-%d')}"


class PoetryPaintingMessage(models.Model):
    """对话消息"""
    ROLE_CHOICES = [
        ('user', '用户'),
        ('assistant', '助手'),
        ('system', '系统'),
    ]
    
    conversation = models.ForeignKey(
        PoetryPaintingConversation,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name='所属对话'
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, verbose_name='角色')
    content = models.TextField(verbose_name='消息内容')
    work = models.ForeignKey(
        PoetryPaintingWork,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='关联作品'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        db_table = 'agent_poetry_painting_message'
        ordering = ['created_at']
        verbose_name = '诗词绘画消息'
        verbose_name_plural = verbose_name
    
    def __str__(self):
        return f"{self.role} - {self.content[:30]}"

