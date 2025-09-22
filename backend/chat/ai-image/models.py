"""
AI图像生成数据模型
用于存储用户的图像生成记录和相关参数
"""
from django.db import models
from django.db.models.functions import Coalesce
from django.db.models import Value, Q
from django.contrib.auth import get_user_model
from django.utils import timezone
import json
import logging

logger = logging.getLogger(__name__)

User = get_user_model()


class ImageGenerationTask(models.Model):
    """图像生成任务记录"""
    
    STATUS_CHOICES = [
        ('pending', '等待中'),
        ('processing', '生成中'),
        ('completed', '已完成'),
        ('failed', '失败'),
    ]
    
    # 基本信息
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户', related_name='image_tasks')
    task_id = models.CharField(max_length=100, unique=True, verbose_name='任务ID')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='状态')
    
    # 提示词信息
    prompt = models.TextField(verbose_name='正向提示词')
    negative_prompt = models.TextField(blank=True, null=True, verbose_name='反向提示词')
    enhanced_prompt = models.TextField(blank=True, null=True, verbose_name='增强后的提示词')
    
    # 基础参数
    size = models.CharField(max_length=20, verbose_name='图像尺寸')
    n = models.IntegerField(default=1, verbose_name='生成数量')
    prompt_extend = models.BooleanField(default=True, verbose_name='智能改写')
    watermark = models.BooleanField(default=True, verbose_name='添加水印')
    
    # 高级参数
    style = models.CharField(max_length=50, blank=True, null=True, verbose_name='风格')
    shot_type = models.CharField(max_length=50, blank=True, null=True, verbose_name='景别')
    angle = models.CharField(max_length=50, blank=True, null=True, verbose_name='视角')
    shooting_technique = models.CharField(max_length=50, blank=True, null=True, verbose_name='拍摄技法')
    lighting = models.CharField(max_length=50, blank=True, null=True, verbose_name='光线效果')
    
    # API响应信息
    api_request_id = models.CharField(max_length=100, blank=True, null=True, verbose_name='API请求ID')
    api_usage = models.JSONField(default=dict, verbose_name='API使用统计')
    error_message = models.TextField(blank=True, null=True, verbose_name='错误信息')
    
    # 时间信息
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    completed_at = models.DateTimeField(blank=True, null=True, verbose_name='完成时间')
    
    class Meta:
        db_table = 'ai_image_generation_task'
        verbose_name = '图像生成任务'
        verbose_name_plural = '图像生成任务'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['task_id']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.task_id} - {self.status}"
    
    def get_parameters_dict(self):
        """获取所有参数的字典形式"""
        return {
            'prompt': self.prompt,
            'negative_prompt': self.negative_prompt,
            'enhanced_prompt': self.enhanced_prompt,
            'size': self.size,
            'n': self.n,
            'prompt_extend': self.prompt_extend,
            'watermark': self.watermark,
            'style': self.style,
            'shot_type': self.shot_type,
            'angle': self.angle,
            'shooting_technique': self.shooting_technique,
            'lighting': self.lighting,
        }


class GeneratedImage(models.Model):
    """生成的图像记录"""
    
    task = models.ForeignKey(ImageGenerationTask, on_delete=models.CASCADE, verbose_name='生成任务', related_name='images')
    
    # 图像信息
    original_url = models.URLField(max_length=1000, verbose_name='原始图像URL')
    saved_path = models.CharField(max_length=500, verbose_name='保存路径')
    saved_url = models.URLField(max_length=1000, verbose_name='保存后的URL')
    filename = models.CharField(max_length=255, verbose_name='文件名')
    file_size = models.BigIntegerField(verbose_name='文件大小(字节)')
    
    # API返回的提示词信息
    orig_prompt = models.TextField(blank=True, null=True, verbose_name='原始提示词')
    actual_prompt = models.TextField(blank=True, null=True, verbose_name='实际使用的提示词')
    
    # 图像元数据
    width = models.IntegerField(blank=True, null=True, verbose_name='宽度')
    height = models.IntegerField(blank=True, null=True, verbose_name='高度')
    format = models.CharField(max_length=10, blank=True, null=True, verbose_name='格式')
    
    # 下载和存储信息
    download_time = models.DateTimeField(verbose_name='下载时间')
    download_duration = models.FloatField(blank=True, null=True, verbose_name='下载耗时(秒)')
    is_downloaded = models.BooleanField(default=False, verbose_name='是否已下载')
    
    # 用户操作记录
    view_count = models.IntegerField(default=0, verbose_name='查看次数')
    download_count = models.IntegerField(default=0, verbose_name='下载次数')
    last_viewed = models.DateTimeField(blank=True, null=True, verbose_name='最后查看时间')
    
    # 时间信息
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'ai_generated_image'
        verbose_name = '生成的图像'
        verbose_name_plural = '生成的图像'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['task', '-created_at']),
            models.Index(fields=['is_downloaded']),
        ]
    
    def __str__(self):
        return f"{self.task.user.username} - {self.filename}"
    
    def increment_view_count(self):
        """增加查看次数"""
        self.view_count += 1
        self.last_viewed = timezone.now()
        self.save(update_fields=['view_count', 'last_viewed'])
    
    def increment_download_count(self):
        """增加下载次数"""
        self.download_count += 1
        self.save(update_fields=['download_count'])
    
    def get_size_display(self):
        """获取文件大小的友好显示"""
        if not self.file_size:
            return '未知'
        
        for unit in ['B', 'KB', 'MB', 'GB']:
            if self.file_size < 1024.0:
                return f"{self.file_size:.1f} {unit}"
            self.file_size /= 1024.0
        return f"{self.file_size:.1f} TB"


class UserImageStats(models.Model):
    """用户图像生成统计"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='用户', related_name='image_stats')
    
    # 统计数据
    total_tasks = models.IntegerField(default=0, verbose_name='总任务数')
    total_images = models.IntegerField(default=0, verbose_name='总图像数')
    success_tasks = models.IntegerField(default=0, verbose_name='成功任务数')
    failed_tasks = models.IntegerField(default=0, verbose_name='失败任务数')
    
    # 使用统计
    total_storage_used = models.BigIntegerField(default=0, verbose_name='使用存储空间(字节)')
    total_api_calls = models.IntegerField(default=0, verbose_name='API调用次数')
    
    # 偏好分析
    favorite_style = models.CharField(max_length=50, blank=True, null=True, verbose_name='偏好风格')
    favorite_size = models.CharField(max_length=20, blank=True, null=True, verbose_name='偏好尺寸')
    avg_images_per_task = models.FloatField(default=1.0, verbose_name='平均每任务图像数')
    
    # 时间信息
    first_generation = models.DateTimeField(blank=True, null=True, verbose_name='首次生成时间')
    last_generation = models.DateTimeField(blank=True, null=True, verbose_name='最后生成时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'ai_user_image_stats'
        verbose_name = '用户图像统计'
        verbose_name_plural = '用户图像统计'
    
    def __str__(self):
        return f"{self.user.username} - 统计"
    
    def update_stats(self):
        """更新统计数据 - 添加全面的异常处理"""
        try:
            tasks = ImageGenerationTask.objects.filter(user=self.user)
            
            # 基础统计
            self.total_tasks = tasks.count()
            self.success_tasks = tasks.filter(status='completed').count()
            self.failed_tasks = tasks.filter(status='failed').count()
            
            images = GeneratedImage.objects.filter(task__user=self.user)
            self.total_images = images.count()
            
            # 修复聚合查询，使用Coalesce处理空值
            try:
                storage_result = images.aggregate(
                    total=Coalesce(models.Sum('file_size'), Value(0))
                )
                self.total_storage_used = storage_result.get('total', 0)
            except Exception as e:
                logger.warning(f"计算存储使用量失败: {str(e)}")
                self.total_storage_used = 0
            
            # 分析偏好
            if self.total_tasks > 0:
                try:
                    # 最常用的风格 - 添加异常处理
                    style_stats = tasks.exclude(
                        Q(style__isnull=True) | Q(style='')
                    ).values('style').annotate(
                        count=models.Count('style')
                    ).order_by('-count').first()
                    if style_stats:
                        self.favorite_style = style_stats['style']
                except Exception as e:
                    logger.warning(f"获取偏好风格失败: {str(e)}")
                    self.favorite_style = None
                
                try:
                    # 最常用的尺寸 - 添加异常处理
                    size_stats = tasks.values('size').annotate(
                        count=models.Count('size')
                    ).order_by('-count').first()
                    if size_stats:
                        self.favorite_size = size_stats['size']
                except Exception as e:
                    logger.warning(f"获取偏好尺寸失败: {str(e)}")
                    self.favorite_size = None
                
                # 平均每任务图像数
                try:
                    self.avg_images_per_task = self.total_images / self.total_tasks if self.total_tasks > 0 else 0.0
                except (ZeroDivisionError, TypeError):
                    self.avg_images_per_task = 0.0
            else:
                # 如果没有任务，重置偏好数据
                self.favorite_style = None
                self.favorite_size = None
                self.avg_images_per_task = 0.0
            
            # 更新时间
            try:
                first_task = tasks.order_by('created_at').first()
                if first_task:
                    self.first_generation = first_task.created_at
                
                last_task = tasks.order_by('-created_at').first()
                if last_task:
                    self.last_generation = last_task.created_at
            except Exception as e:
                logger.warning(f"更新时间信息失败: {str(e)}")
            
            # 保存更新
            self.save()
            logger.info(f"用户 {self.user.username} 统计信息更新成功")
            
        except Exception as e:
            logger.error(f"更新用户统计信息失败: {str(e)}")
            # 即使统计更新失败，也不应该影响主要的图像生成功能
            # 所以这里只记录错误，不抛出异常
