"""
AI视频生成相关模型
包括文生视频、图生视频等功能的数据模型
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


class VideoGenerationTask(models.Model):
    """视频生成任务模型"""
    TASK_TYPE_CHOICES = [
        ('text_to_video', _('文生视频')),
        ('image_to_video', _('图生视频')),
    ]
    
    STATUS_CHOICES = [
        ('pending', _('待处理')),
        ('processing', _('处理中')),
        ('completed', _('已完成')),
        ('failed', _('失败')),
    ]
    
    RESOLUTION_CHOICES = [
        ('720P', '1280x720'),
        ('1080P', '1920x1080'),
        ('1280*720', '1280x720'),
        ('1920*1080', '1920x1080'),
    ]
    
    task_id = models.CharField(max_length=100, unique=True, verbose_name=_('任务ID'))
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('用户'))
    task_type = models.CharField(max_length=20, choices=TASK_TYPE_CHOICES, verbose_name=_('任务类型'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name=_('状态'))
    
    # 输入参数
    prompt = models.TextField(verbose_name=_('文本提示词'))
    input_image = models.ImageField(upload_to='video-inputs/', blank=True, null=True, verbose_name=_('输入图片'))
    input_image_url = models.URLField(max_length=1000, blank=True, null=True, verbose_name=_('输入图片URL'))
    
    # 生成参数
    model = models.CharField(max_length=50, default='wan2.5-t2v-preview', verbose_name=_('生成模型'))
    resolution = models.CharField(max_length=20, choices=RESOLUTION_CHOICES, default='1280*720', verbose_name=_('分辨率'))
    duration = models.IntegerField(default=5, verbose_name=_('视频时长(秒)'))
    fps = models.IntegerField(default=24, verbose_name=_('帧率'))
    seed = models.BigIntegerField(blank=True, null=True, verbose_name=_('随机种子'))
    
    # 输出结果
    output_video_url = models.URLField(max_length=1000, blank=True, null=True, verbose_name=_('输出视频URL'))
    saved_video_path = models.CharField(max_length=500, blank=True, null=True, verbose_name=_('保存的视频路径'))
    video_file_size = models.BigIntegerField(blank=True, null=True, verbose_name=_('视频文件大小'))
    
    # 增强提示词
    enhanced_prompt = models.TextField(blank=True, null=True, verbose_name=_('增强后的提示词'))
    original_prompt = models.TextField(blank=True, null=True, verbose_name=_('原始提示词'))
    
    # API相关
    api_request_id = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('API请求ID'))
    api_task_id = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('API任务ID'))
    api_usage = models.JSONField(default=dict, blank=True, verbose_name=_('API使用统计'))
    error_message = models.TextField(blank=True, null=True, verbose_name=_('错误信息'))
    
    # 时间统计
    submit_time = models.DateTimeField(blank=True, null=True, verbose_name=_('提交时间'))
    scheduled_time = models.DateTimeField(blank=True, null=True, verbose_name=_('调度时间'))
    end_time = models.DateTimeField(blank=True, null=True, verbose_name=_('结束时间'))
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('创建时间'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('更新时间'))
    completed_at = models.DateTimeField(blank=True, null=True, verbose_name=_('完成时间'))
    
    class Meta:
        verbose_name = _('视频生成任务')
        verbose_name_plural = _('视频生成任务')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'task_type']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
            models.Index(fields=['api_task_id']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.get_task_type_display()} - {self.task_id}"
    
    def save(self, *args, **kwargs):
        if not self.task_id:
            self.task_id = str(uuid.uuid4())
        if not self.original_prompt:
            self.original_prompt = self.prompt
        super().save(*args, **kwargs)


class GeneratedVideo(models.Model):
    """生成的视频记录"""
    task = models.ForeignKey(VideoGenerationTask, on_delete=models.CASCADE, related_name='generated_videos', verbose_name=_('生成任务'))
    
    # 视频信息
    original_url = models.URLField(max_length=1000, verbose_name=_('原始视频URL'))
    saved_url = models.URLField(max_length=1000, blank=True, null=True, verbose_name=_('保存后的视频URL'))
    saved_path = models.CharField(max_length=500, blank=True, null=True, verbose_name=_('本地保存路径'))
    filename = models.CharField(max_length=255, verbose_name=_('文件名'))
    
    # 视频属性
    file_size = models.BigIntegerField(blank=True, null=True, verbose_name=_('文件大小(字节)'))
    duration = models.FloatField(blank=True, null=True, verbose_name=_('视频时长(秒)'))
    resolution = models.CharField(max_length=20, blank=True, null=True, verbose_name=_('分辨率'))
    fps = models.IntegerField(blank=True, null=True, verbose_name=_('帧率'))
    bitrate = models.IntegerField(blank=True, null=True, verbose_name=_('比特率'))
    
    # 下载状态
    is_downloaded = models.BooleanField(default=False, verbose_name=_('是否已下载'))
    download_time = models.DateTimeField(blank=True, null=True, verbose_name=_('下载时间'))
    download_error = models.TextField(blank=True, null=True, verbose_name=_('下载错误信息'))
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('创建时间'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('更新时间'))
    
    class Meta:
        verbose_name = _('生成的视频')
        verbose_name_plural = _('生成的视频')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['task']),
            models.Index(fields=['is_downloaded']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.task.task_id} - {self.filename}"


class UserVideoStats(models.Model):
    """用户视频生成统计"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, verbose_name=_('用户'))
    
    # 生成统计
    total_text_to_video = models.IntegerField(default=0, verbose_name=_('文生视频次数'))
    total_image_to_video = models.IntegerField(default=0, verbose_name=_('图生视频次数'))
    total_videos_generated = models.IntegerField(default=0, verbose_name=_('总生成视频数'))
    
    # 存储统计
    total_video_duration = models.FloatField(default=0, verbose_name=_('总视频时长(秒)'))
    total_storage_used = models.BigIntegerField(default=0, verbose_name=_('总存储使用(字节)'))
    
    # 使用时间统计
    total_generation_time = models.FloatField(default=0, verbose_name=_('总生成耗时(秒)'))
    average_generation_time = models.FloatField(default=0, verbose_name=_('平均生成耗时(秒)'))
    
    # 时间统计
    last_generation_at = models.DateTimeField(blank=True, null=True, verbose_name=_('最后生成时间'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('创建时间'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('更新时间'))
    
    class Meta:
        verbose_name = _('用户视频统计')
        verbose_name_plural = _('用户视频统计')
    
    def __str__(self):
        return f"{self.user.username} - 视频统计"
    
    @classmethod
    def update_stats(cls, user_id: int):
        """更新用户视频生成统计"""
        try:
            from django.db.models import Sum, Count, Avg, Q
            from django.db.models.functions import Coalesce
            from django.db.models import Value
            
            # 获取或创建统计记录
            stats, created = cls.objects.get_or_create(user_id=user_id)
            
            # 统计各类型任务数量
            task_counts = VideoGenerationTask.objects.filter(
                user_id=user_id,
                status='completed'
            ).values('task_type').annotate(count=Count('id'))
            
            # 重置计数
            stats.total_text_to_video = 0
            stats.total_image_to_video = 0
            
            # 更新任务类型统计
            for item in task_counts:
                if item['task_type'] == 'text_to_video':
                    stats.total_text_to_video = item['count']
                elif item['task_type'] == 'image_to_video':
                    stats.total_image_to_video = item['count']
            
            # 总生成视频数
            stats.total_videos_generated = GeneratedVideo.objects.filter(
                task__user_id=user_id,
                task__status='completed'
            ).count()
            
            # 计算总视频时长
            try:
                video_duration = GeneratedVideo.objects.filter(
                    task__user_id=user_id,
                    task__status='completed',
                    duration__isnull=False
                ).aggregate(
                    total=Coalesce(Sum('duration'), Value(0))
                )['total'] or 0
                
                stats.total_video_duration = float(video_duration)
                
            except Exception as e:
                logger.warning(f"计算视频时长失败: {str(e)}")
                stats.total_video_duration = 0
            
            # 计算存储使用量
            try:
                storage_used = GeneratedVideo.objects.filter(
                    task__user_id=user_id,
                    task__status='completed',
                    file_size__isnull=False
                ).aggregate(
                    total=Coalesce(Sum('file_size'), Value(0))
                )['total'] or 0
                
                stats.total_storage_used = storage_used
                
            except Exception as e:
                logger.warning(f"计算存储使用量失败: {str(e)}")
                stats.total_storage_used = 0
            
            # 计算生成耗时统计
            try:
                completed_tasks = VideoGenerationTask.objects.filter(
                    user_id=user_id,
                    status='completed',
                    submit_time__isnull=False,
                    end_time__isnull=False
                )
                
                if completed_tasks.exists():
                    # 计算每个任务的耗时
                    total_time = 0
                    count = 0
                    for task in completed_tasks:
                        if task.submit_time and task.end_time:
                            duration = (task.end_time - task.submit_time).total_seconds()
                            if duration > 0:
                                total_time += duration
                                count += 1
                    
                    stats.total_generation_time = total_time
                    stats.average_generation_time = total_time / count if count > 0 else 0
                else:
                    stats.total_generation_time = 0
                    stats.average_generation_time = 0
                    
            except Exception as e:
                logger.warning(f"计算生成耗时失败: {str(e)}")
                stats.total_generation_time = 0
                stats.average_generation_time = 0
            
            # 更新最后生成时间
            try:
                last_task = VideoGenerationTask.objects.filter(
                    user_id=user_id,
                    status='completed'
                ).order_by('-completed_at').first()
                
                if last_task and last_task.completed_at:
                    stats.last_generation_at = last_task.completed_at
            except Exception as e:
                logger.warning(f"更新最后生成时间失败: {str(e)}")
            
            stats.save()
            logger.info(f"用户视频统计更新成功: user_id={user_id}")
            
        except Exception as e:
            logger.error(f"更新用户视频统计失败: user_id={user_id}, error={str(e)}")
            import traceback
            logger.error(f"错误堆栈: {traceback.format_exc()}")


class VideoStylePreset(models.Model):
    """视频风格预设"""
    name = models.CharField(max_length=100, unique=True, verbose_name=_('风格名称'))
    description = models.TextField(verbose_name=_('风格描述'))
    style_keywords = models.TextField(verbose_name=_('风格关键词'))
    recommended_model = models.CharField(max_length=50, default='wanx2.1-t2v-turbo', verbose_name=_('推荐模型'))
    
    # 默认参数
    default_resolution = models.CharField(max_length=20, default='1280*720', verbose_name=_('默认分辨率'))
    default_duration = models.IntegerField(default=5, verbose_name=_('默认时长'))
    default_fps = models.IntegerField(default=25, verbose_name=_('默认帧率'))
    
    # 预设图片
    preview_image = models.ImageField(upload_to='video-style-previews/', blank=True, null=True, verbose_name=_('预览图'))
    
    # 使用统计
    usage_count = models.IntegerField(default=0, verbose_name=_('使用次数'))
    
    # 状态
    is_active = models.BooleanField(default=True, verbose_name=_('是否激活'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('创建时间'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('更新时间'))
    
    class Meta:
        verbose_name = _('视频风格预设')
        verbose_name_plural = _('视频风格预设')
        ordering = ['-usage_count', 'name']
    
    def __str__(self):
        return self.name
    
    def increment_usage(self):
        """增加使用次数"""
        self.usage_count += 1
        self.save(update_fields=['usage_count'])
