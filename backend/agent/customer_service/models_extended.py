"""
扩展的客服系统数据模型 - 知识库和助手配置
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField

# pgvector 配置
# 注意：Windows环境下PostgreSQL需要额外安装pgvector扩展
# 暂时禁用pgvector，使用TextField替代
PGVECTOR_AVAILABLE = False  # 设为True需要PostgreSQL安装pgvector扩展

# 尝试导入 pgvector，如果失败则使用备用方案
if PGVECTOR_AVAILABLE:
    try:
        from pgvector.django import VectorField
    except ImportError:
        PGVECTOR_AVAILABLE = False
        VectorField = None
else:
    VectorField = None

User = get_user_model()


class KnowledgeBase(models.Model):
    """知识库"""
    STATUS_CHOICES = [
        ('creating', '创建中'),
        ('processing', '处理中'),
        ('ready', '就绪'),
        ('error', '错误'),
    ]
    
    FORMAT_CHOICES = [
        ('text', '文本格式'),
        ('structured', '结构化格式'),
        ('image', '图片格式'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='knowledge_bases')
    name = models.CharField(max_length=200, verbose_name='知识库名称')
    description = models.TextField(blank=True, verbose_name='描述')
    format = models.CharField(max_length=20, choices=FORMAT_CHOICES, default='text', verbose_name='知识库格式')
    
    # 状态
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='creating')
    error_message = models.TextField(blank=True, null=True)
    
    # 统计
    document_count = models.IntegerField(default=0, verbose_name='文档数量')
    chunk_count = models.IntegerField(default=0, verbose_name='切片数量')
    total_tokens = models.IntegerField(default=0, verbose_name='总token数')
    
    # 文档分析结果（使用 JSON 存储）
    domain = models.CharField(max_length=100, blank=True, null=True, verbose_name='文档领域')
    summary = models.TextField(blank=True, null=True, verbose_name='文档总结')
    key_points = models.JSONField(default=list, blank=True, verbose_name='核心要点')
    keywords = models.JSONField(default=list, blank=True, verbose_name='关键词')
    suggested_questions = models.JSONField(default=list, blank=True, verbose_name='推荐问题')
    intent_prompt = models.TextField(blank=True, null=True, verbose_name='意图识别提示词')
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'cs_knowledge_base'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
        ]

    def __str__(self):
        return f"{self.name} ({self.user.username})"


class KnowledgeDocument(models.Model):
    """知识库文档"""
    STATUS_CHOICES = [
        ('uploading', '上传中'),
        ('processing', '处理中'),
        ('completed', '已完成'),
        ('failed', '失败'),
    ]

    knowledge_base = models.ForeignKey(
        KnowledgeBase, 
        on_delete=models.CASCADE, 
        related_name='documents'
    )
    
    # 文档信息
    filename = models.CharField(max_length=500)
    file_type = models.CharField(max_length=50)  # pdf, txt, docx, md等
    file_size = models.BigIntegerField(verbose_name='文件大小（字节）')
    file_path = models.CharField(max_length=1000, verbose_name='文件路径')
    
    # 处理状态
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='uploading')
    error_message = models.TextField(blank=True, null=True)
    
    # 处理配置
    chunk_strategy = models.CharField(
        max_length=20, 
        choices=[
            ('auto', '智能切片'),
            ('fixed', '固定长度'),
            ('semantic', '语义切片'),
        ],
        default='auto'
    )
    chunk_size = models.IntegerField(default=500, verbose_name='切片大小')
    chunk_overlap = models.IntegerField(default=50, verbose_name='切片重叠')
    
    # 清洗配置
    clean_strategy = models.CharField(
        max_length=20,
        choices=[
            ('auto', '智能清洗'),
            ('basic', '基础清洗'),
            ('none', '不清洗'),
        ],
        default='auto'
    )
    
    # 统计
    chunk_count = models.IntegerField(default=0, verbose_name='切片数量')
    token_count = models.IntegerField(default=0, verbose_name='token数量')
    
    # 元数据
    metadata = models.JSONField(default=dict, blank=True)
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'cs_knowledge_document'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.filename} - {self.knowledge_base.name}"


class DocumentChunk(models.Model):
    """文档切片（向量存储）"""
    document = models.ForeignKey(
        KnowledgeDocument, 
        on_delete=models.CASCADE, 
        related_name='chunks'
    )
    knowledge_base = models.ForeignKey(
        KnowledgeBase,
        on_delete=models.CASCADE,
        related_name='chunks'
    )
    
    # 切片内容
    content = models.TextField(verbose_name='切片内容')
    chunk_index = models.IntegerField(verbose_name='切片索引')
    
    # 向量嵌入（根据pgvector是否可用选择字段类型）
    # 如果pgvector可用，使用VectorField；否则使用TextField存储JSON
    if PGVECTOR_AVAILABLE:
        embedding = VectorField(dimensions=1536, null=True, blank=True)
    else:
        # 备用方案：使用TextField存储JSON格式的向量
        embedding = models.TextField(null=True, blank=True, verbose_name='向量嵌入(JSON)')
    
    # 元数据
    metadata = models.JSONField(default=dict, blank=True)
    token_count = models.IntegerField(default=0)
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'cs_document_chunk'
        indexes = [
            models.Index(fields=['document', 'chunk_index']),
            models.Index(fields=['knowledge_base']),
        ]

    def __str__(self):
        return f"{self.document.filename} - Chunk {self.chunk_index}"


class CustomerServiceAssistant(models.Model):
    """客服助手配置"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cs_assistants')
    
    # 基本信息
    name = models.CharField(max_length=200, verbose_name='助手名称')
    description = models.TextField(blank=True, verbose_name='描述')
    avatar = models.CharField(max_length=10, default='🤖', verbose_name='头像emoji')
    
    # 配置
    greeting_message = models.TextField(
        default='您好！我是智能客服助手，有什么可以帮您的吗？',
        verbose_name='开场白'
    )
    system_prompt = models.TextField(
        blank=True,
        verbose_name='系统提示词',
        help_text='自定义AI行为和语气'
    )
    
    # 关联知识库
    knowledge_bases = models.ManyToManyField(
        KnowledgeBase,
        blank=True,
        related_name='assistants',
        verbose_name='关联知识库'
    )
    
    # 高级设置
    model = models.CharField(
        max_length=50,
        default='qwen-plus',
        choices=[
            ('qwen-turbo', 'Qwen Turbo - 快速'),
            ('qwen-plus', 'Qwen Plus - 平衡'),
            ('qwen-max', 'Qwen Max - 高质量'),
        ],
        verbose_name='AI模型'
    )
    temperature = models.FloatField(default=0.7, verbose_name='创造性参数')
    top_k = models.IntegerField(default=3, verbose_name='检索数量')
    
    # 启用功能
    enable_knowledge_base = models.BooleanField(default=True, verbose_name='启用知识库')
    enable_order_query = models.BooleanField(default=True, verbose_name='启用订单查询')
    enable_human_handoff = models.BooleanField(default=True, verbose_name='启用人工转接')
    
    # 状态
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    is_default = models.BooleanField(default=False, verbose_name='是否默认')
    
    # 统计
    total_conversations = models.IntegerField(default=0, verbose_name='总对话数')
    total_messages = models.IntegerField(default=0, verbose_name='总消息数')
    avg_satisfaction = models.FloatField(null=True, blank=True, verbose_name='平均满意度')
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'cs_assistant'
        ordering = ['-is_default', '-created_at']
        indexes = [
            models.Index(fields=['user', 'is_active']),
        ]

    def __str__(self):
        return f"{self.name} ({self.user.username})"

    def save(self, *args, **kwargs):
        # 如果设置为默认，取消其他助手的默认状态
        if self.is_default:
            CustomerServiceAssistant.objects.filter(
                user=self.user,
                is_default=True
            ).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)


class ChunkProcessingLog(models.Model):
    """切片处理日志"""
    document = models.ForeignKey(KnowledgeDocument, on_delete=models.CASCADE)
    
    step = models.CharField(max_length=50, verbose_name='处理步骤')
    status = models.CharField(
        max_length=20,
        choices=[
            ('started', '开始'),
            ('success', '成功'),
            ('failed', '失败'),
        ]
    )
    message = models.TextField(blank=True)
    details = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'cs_chunk_processing_log'
        ordering = ['-created_at']


# 更新原有的会话模型，添加助手关联
# 注意：需要在 models.py 中添加
"""
在 CustomerServiceSession 中添加：
assistant = models.ForeignKey(
    'CustomerServiceAssistant',
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name='sessions'
)
"""

