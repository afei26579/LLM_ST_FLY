"""
AI音频处理序列化器
"""

from rest_framework import serializers
from django.core.files.uploadedfile import UploadedFile
from .models import (
    AudioTask, SpeechToTextTask, TextToSpeechTask, VoiceCloneTask, UserAudioStats
)


class SpeechToTextSerializer(serializers.Serializer):
    """语音转文字请求序列化器"""
    audio_file = serializers.FileField(required=False, help_text="音频文件")
    audio_url = serializers.URLField(required=False, help_text="音频文件URL")
    language = serializers.CharField(max_length=10, default='zh-cn', help_text="语言代码")
    model = serializers.CharField(max_length=50, default='paraformer-realtime-v1', help_text="识别模型")
    
    def validate(self, data):
        """验证数据"""
        if not data.get('audio_file') and not data.get('audio_url'):
            raise serializers.ValidationError("必须提供音频文件或音频URL")
        return data


class TextToSpeechSerializer(serializers.Serializer):
    """文字转语音请求序列化器"""
    text = serializers.CharField(max_length=5000, help_text="要转换的文本")
    voice = serializers.CharField(max_length=50, default='zhifeng_emo', help_text="音色")
    speed = serializers.FloatField(default=1.0, min_value=0.5, max_value=2.0, help_text="语速")
    volume = serializers.IntegerField(default=50, min_value=0, max_value=100, help_text="音量")
    pitch = serializers.FloatField(default=1.0, min_value=0.5, max_value=2.0, help_text="音调")
    format = serializers.ChoiceField(
        choices=['mp3', 'wav', 'pcm'], 
        default='mp3', 
        help_text="输出格式"
    )
    
    def validate_text(self, value):
        """验证文本内容"""
        if not value.strip():
            raise serializers.ValidationError("文本内容不能为空")
        if len(value.strip()) > 5000:
            raise serializers.ValidationError("文本内容不能超过5000个字符")
        return value.strip()


class VoiceCloneSerializer(serializers.Serializer):
    """语音克隆请求序列化器"""
    reference_audio = serializers.FileField(help_text="参考音频文件")
    reference_text = serializers.CharField(max_length=1000, help_text="参考文本")
    target_text = serializers.CharField(max_length=1000, help_text="目标文本")
    model = serializers.CharField(max_length=50, default='sambert-v1', help_text="克隆模型")
    
    def validate_reference_text(self, value):
        """验证参考文本"""
        if not value.strip():
            raise serializers.ValidationError("参考文本不能为空")
        return value.strip()
    
    def validate_target_text(self, value):
        """验证目标文本"""
        if not value.strip():
            raise serializers.ValidationError("目标文本不能为空")
        return value.strip()


class AudioTaskSerializer(serializers.ModelSerializer):
    """音频任务序列化器"""
    class Meta:
        model = AudioTask
        fields = [
            'task_id', 'task_type', 'status', 'input_text', 
            'output_text', 'output_audio_url', 'error_message',
            'created_at', 'updated_at', 'completed_at'
        ]
        read_only_fields = ['task_id', 'created_at', 'updated_at']


class SpeechToTextTaskSerializer(serializers.ModelSerializer):
    """语音转文字任务序列化器"""
    audio_task = AudioTaskSerializer(read_only=True)
    
    class Meta:
        model = SpeechToTextTask
        fields = [
            'audio_task', 'language', 'model', 'format', 
            'sample_rate', 'confidence', 'duration'
        ]


class TextToSpeechTaskSerializer(serializers.ModelSerializer):
    """文字转语音任务序列化器"""
    audio_task = AudioTaskSerializer(read_only=True)
    
    class Meta:
        model = TextToSpeechTask
        fields = [
            'audio_task', 'voice', 'speed', 'volume', 'pitch', 
            'format', 'sample_rate', 'audio_duration', 'file_size'
        ]


class VoiceCloneTaskSerializer(serializers.ModelSerializer):
    """语音克隆任务序列化器"""
    audio_task = AudioTaskSerializer(read_only=True)
    
    class Meta:
        model = VoiceCloneTask
        fields = [
            'audio_task', 'reference_text', 'target_text', 
            'model', 'similarity_score'
        ]


class UserAudioStatsSerializer(serializers.ModelSerializer):
    """用户音频统计序列化器"""
    class Meta:
        model = UserAudioStats
        fields = [
            'total_speech_to_text', 'total_text_to_speech', 'total_voice_clone',
            'total_audio_duration', 'total_storage_used', 'last_audio_at',
            'created_at', 'updated_at'
        ]


class AudioResponseSerializer(serializers.Serializer):
    """音频处理响应序列化器"""
    task_id = serializers.CharField(help_text="任务ID")
    status = serializers.CharField(help_text="任务状态")
    message = serializers.CharField(required=False, help_text="响应消息")
    
    # 语音转文字响应字段
    text = serializers.CharField(required=False, help_text="识别的文本")
    confidence = serializers.FloatField(required=False, help_text="置信度")
    duration = serializers.FloatField(required=False, help_text="音频时长")
    
    # 文字转语音响应字段
    audio_url = serializers.URLField(required=False, help_text="音频文件URL")
    file_size = serializers.IntegerField(required=False, help_text="文件大小")
    
    # 语音克隆响应字段
    similarity_score = serializers.FloatField(required=False, help_text="相似度评分")
    
    # 通用字段
    usage = serializers.DictField(required=False, help_text="API使用统计")


class TaskStatusSerializer(serializers.Serializer):
    """任务状态查询序列化器"""
    task_id = serializers.CharField(help_text="任务ID")
    status = serializers.CharField(help_text="任务状态")
    task_type = serializers.CharField(help_text="任务类型")
    created_at = serializers.DateTimeField(help_text="创建时间")
    updated_at = serializers.DateTimeField(help_text="更新时间")
    completed_at = serializers.DateTimeField(required=False, help_text="完成时间")
    output_text = serializers.CharField(required=False, help_text="输出文本")
    output_audio_url = serializers.URLField(required=False, help_text="输出音频URL")
    error_message = serializers.CharField(required=False, help_text="错误信息")
    api_usage = serializers.DictField(required=False, help_text="API使用统计")


class AudioHistorySerializer(serializers.Serializer):
    """音频历史记录序列化器"""
    task_id = serializers.CharField(help_text="任务ID")
    task_type = serializers.CharField(help_text="任务类型")
    status = serializers.CharField(help_text="任务状态")
    created_at = serializers.DateTimeField(help_text="创建时间")
    completed_at = serializers.DateTimeField(required=False, help_text="完成时间")
    input_text = serializers.CharField(required=False, help_text="输入文本")
    output_text = serializers.CharField(required=False, help_text="输出文本")
    output_audio_url = serializers.URLField(required=False, help_text="输出音频URL")
    error_message = serializers.CharField(required=False, help_text="错误信息")
