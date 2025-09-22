from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings
import json

User = get_user_model()


class Document(models.Model):
    """文档信息表"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="用户")
    name = models.CharField(max_length=255, verbose_name="文档名称")
    size = models.BigIntegerField(verbose_name="文件大小(字节)")
    file_type = models.CharField(max_length=50, verbose_name="文件类型")
    file_object_id = models.CharField(max_length=255, verbose_name="AI服务文件ID")
    file_hash = models.CharField(max_length=64, blank=True, null=True, verbose_name="文件哈希")
    last_modified = models.BigIntegerField(verbose_name="文件最后修改时间")
    upload_time = models.DateTimeField(auto_now_add=True, verbose_name="上传时间")
    updated_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    class Meta:
        db_table = 'ai_reading_document'
        verbose_name = '文档'
        verbose_name_plural = '文档'
        # 同一用户的相同文档（基于名称、大小、修改时间）应该是唯一的
        unique_together = ['user', 'name', 'size', 'last_modified']
    
    def __str__(self):
        return f"{self.user.username} - {self.name}"


class DocumentAnalysis(models.Model):
    """文档分析结果表"""
    document = models.OneToOneField(Document, on_delete=models.CASCADE, verbose_name="文档")
    summary = models.TextField(verbose_name="总结")
    key_points = models.JSONField(default=list, verbose_name="核心要点")
    keywords = models.JSONField(default=list, verbose_name="关键词")
    entities = models.JSONField(default=list, verbose_name="实体识别结果")
    suggested_questions = models.JSONField(default=list, verbose_name="推荐问题")
    analysis_time = models.DateTimeField(auto_now_add=True, verbose_name="分析时间")
    updated_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    class Meta:
        db_table = 'ai_reading_analysis'
        verbose_name = '文档分析'
        verbose_name_plural = '文档分析'
    
    def __str__(self):
        return f"{self.document.name} - 分析结果"


class QAHistory(models.Model):
    """问答历史表"""
    document = models.ForeignKey(Document, on_delete=models.CASCADE, verbose_name="文档")
    question = models.TextField(verbose_name="问题")
    answer = models.TextField(verbose_name="回答")
    created_time = models.DateTimeField(auto_now_add=True, verbose_name="提问时间")
    
    class Meta:
        db_table = 'ai_reading_qa_history'
        verbose_name = '问答历史'
        verbose_name_plural = '问答历史'
        ordering = ['-created_time']  # 按时间倒序
    
    def __str__(self):
        return f"{self.document.name} - Q: {self.question[:50]}..."


class DocumentAccess(models.Model):
    """文档访问记录表"""
    document = models.ForeignKey(Document, on_delete=models.CASCADE, verbose_name="文档")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="用户")
    access_time = models.DateTimeField(auto_now_add=True, verbose_name="访问时间")
    access_type = models.CharField(
        max_length=20, 
        choices=[
            ('upload', '上传'),
            ('analyze', '分析'),
            ('question', '提问'),
            ('view', '查看')
        ],
        verbose_name="访问类型"
    )
    
    class Meta:
        db_table = 'ai_reading_access'
        verbose_name = '文档访问记录'
        verbose_name_plural = '文档访问记录'
        ordering = ['-access_time']
    
    def __str__(self):
        return f"{self.user.username} - {self.document.name} - {self.access_type}"