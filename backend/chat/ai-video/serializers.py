"""
AI视频生成序列化器
"""

from rest_framework import serializers
from django.core.files.uploadedfile import UploadedFile
from .models import (
    VideoGenerationTask, GeneratedVideo, UserVideoStats, VideoStylePreset
)


class TextToVideoSerializer(serializers.Serializer):
    """文生视频请求序列化器"""
    prompt = serializers.CharField(max_length=5000, help_text="文本提示词")
    model = serializers.CharField(max_length=50, default='wan2.5-t2v-preview', help_text="生成模型")
    resolution = serializers.ChoiceField(
        choices=['480P', '720P', '1080P', '854*480', '1280*720', '1920*1080'],
        default='1280*720',
        help_text="分辨率"
    )
    duration = serializers.IntegerField(default=5, min_value=5, max_value=10, help_text="视频时长(秒)")
    fps = serializers.IntegerField(default=24, help_text="帧率")
    seed = serializers.IntegerField(required=False, min_value=0, max_value=2147483647, help_text="随机种子")
    style_preset_id = serializers.IntegerField(required=False, help_text="风格预设ID")
    
    def validate_prompt(self, value):
        """验证提示词"""
        if not value.strip():
            raise serializers.ValidationError("提示词不能为空")
        if len(value.strip()) > 5000:
            raise serializers.ValidationError("提示词不能超过5000个字符")
        return value.strip()
    
    def validate_seed(self, value):
        """验证随机种子"""
        if value is not None:
            if value < 0:
                return 0
            if value > 2147483647:
                return 2147483647
        return value


class ImageToVideoSerializer(serializers.Serializer):
    """图生视频请求序列化器"""
    prompt = serializers.CharField(max_length=5000, required=False, allow_blank=True, help_text="文本提示词（可选）")
    image_file = serializers.ImageField(required=False, help_text="输入图片文件")
    input_image = serializers.ImageField(required=False, help_text="输入图片文件（兼容字段）")
    image_url = serializers.URLField(required=False, help_text="输入图片URL")
    input_image_url = serializers.URLField(required=False, help_text="输入图片URL（兼容字段）")
    model = serializers.CharField(max_length=50, default='wan2.5-i2v-preview', help_text="生成模型")
    resolution = serializers.ChoiceField(
        choices=['480P', '720P', '1080P', '854*480', '1280*720', '1920*1080'],
        default='1280*720',
        help_text="分辨率"
    )
    duration = serializers.IntegerField(default=5, min_value=5, max_value=10, help_text="视频时长(秒)")
    fps = serializers.IntegerField(default=24, help_text="帧率")
    
    def validate(self, data):
        """验证数据（兼容两种字段名）"""
        # 兼容处理：image_file 和 input_image
        if data.get('image_file') and not data.get('input_image'):
            data['input_image'] = data['image_file']
        
        # 兼容处理：image_url 和 input_image_url
        if data.get('image_url') and not data.get('input_image_url'):
            data['input_image_url'] = data['image_url']
        
        if not data.get('input_image') and not data.get('input_image_url'):
            raise serializers.ValidationError("必须提供输入图片或图片URL")
        
        return data
    
    def validate_prompt(self, value):
        """验证提示词"""
        if value and len(value.strip()) > 5000:
            raise serializers.ValidationError("提示词不能超过5000个字符")
        return value.strip() if value else ''


class VideoGenerationTaskSerializer(serializers.ModelSerializer):
    """视频生成任务序列化器"""
    class Meta:
        model = VideoGenerationTask
        fields = [
            'task_id', 'task_type', 'status', 'prompt', 'enhanced_prompt',
            'model', 'resolution', 'duration', 'fps', 'output_video_url',
            'video_file_size', 'error_message', 'created_at', 'updated_at', 'completed_at'
        ]
        read_only_fields = ['task_id', 'created_at', 'updated_at']


class GeneratedVideoSerializer(serializers.ModelSerializer):
    """生成的视频序列化器"""
    task = VideoGenerationTaskSerializer(read_only=True)
    
    class Meta:
        model = GeneratedVideo
        fields = [
            'task', 'original_url', 'saved_url', 'filename', 'file_size',
            'duration', 'resolution', 'fps', 'is_downloaded', 'download_time',
            'created_at'
        ]


class UserVideoStatsSerializer(serializers.ModelSerializer):
    """用户视频统计序列化器"""
    class Meta:
        model = UserVideoStats
        fields = [
            'total_text_to_video', 'total_image_to_video', 'total_videos_generated',
            'total_video_duration', 'total_storage_used', 'total_generation_time',
            'average_generation_time', 'last_generation_at', 'created_at', 'updated_at'
        ]


class VideoStylePresetSerializer(serializers.ModelSerializer):
    """视频风格预设序列化器"""
    class Meta:
        model = VideoStylePreset
        fields = [
            'id', 'name', 'description', 'style_keywords', 'recommended_model',
            'default_resolution', 'default_duration', 'default_fps', 'preview_image',
            'usage_count', 'is_active'
        ]
        read_only_fields = ['usage_count']


class VideoResponseSerializer(serializers.Serializer):
    """视频生成响应序列化器"""
    task_id = serializers.CharField(help_text="任务ID")
    status = serializers.CharField(help_text="任务状态")
    message = serializers.CharField(required=False, help_text="响应消息")
    video_url = serializers.URLField(required=False, help_text="视频文件URL")
    duration = serializers.IntegerField(required=False, help_text="视频时长")
    file_size = serializers.IntegerField(required=False, help_text="文件大小")
    enhanced_prompt = serializers.CharField(required=False, help_text="增强后的提示词")
    usage = serializers.DictField(required=False, help_text="API使用统计")


class VideoTaskStatusSerializer(serializers.Serializer):
    """视频任务状态查询序列化器"""
    task_id = serializers.CharField(help_text="任务ID")
    status = serializers.CharField(help_text="任务状态")
    task_type = serializers.CharField(help_text="任务类型")
    prompt = serializers.CharField(help_text="提示词")
    created_at = serializers.DateTimeField(help_text="创建时间")
    updated_at = serializers.DateTimeField(help_text="更新时间")
    completed_at = serializers.DateTimeField(required=False, help_text="完成时间")
    output_video_url = serializers.URLField(required=False, help_text="输出视频URL")
    enhanced_prompt = serializers.CharField(required=False, help_text="增强后的提示词")
    file_size = serializers.IntegerField(required=False, help_text="文件大小")
    error_message = serializers.CharField(required=False, help_text="错误信息")
    api_usage = serializers.DictField(required=False, help_text="API使用统计")


class VideoHistorySerializer(serializers.Serializer):
    """视频历史记录序列化器"""
    task_id = serializers.CharField(help_text="任务ID")
    task_type = serializers.CharField(help_text="任务类型")
    status = serializers.CharField(help_text="任务状态")
    prompt = serializers.CharField(help_text="提示词")
    enhanced_prompt = serializers.CharField(required=False, help_text="增强后的提示词")
    created_at = serializers.DateTimeField(help_text="创建时间")
    completed_at = serializers.DateTimeField(required=False, help_text="完成时间")
    output_video_url = serializers.URLField(required=False, help_text="输出视频URL")
    file_size = serializers.IntegerField(required=False, help_text="文件大小")
    model = serializers.CharField(help_text="生成模型")
    resolution = serializers.CharField(help_text="分辨率")
    duration = serializers.IntegerField(help_text="视频时长")
    error_message = serializers.CharField(required=False, help_text="错误信息")
