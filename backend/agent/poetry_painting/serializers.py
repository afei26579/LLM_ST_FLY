"""
诗词绘画智能体序列化器
"""
from rest_framework import serializers
from .models import PoetryPaintingConversation, PoetryPaintingWork, PoetryPaintingMessage


class PoetryPaintingMessageSerializer(serializers.ModelSerializer):
    """诗词绘画消息序列化器"""
    
    class Meta:
        model = PoetryPaintingMessage
        fields = ['id', 'role', 'content', 'work', 'created_at']
        read_only_fields = ['id', 'created_at']


class PoetryPaintingWorkSerializer(serializers.ModelSerializer):
    """诗词绘画作品序列化器"""
    
    painting_url_full = serializers.SerializerMethodField()
    
    class Meta:
        model = PoetryPaintingWork
        fields = [
            'id', 'conversation', 
            'poetry_theme', 'poetry_format', 'poetry_style', 
            'poetry_content', 'poetry_title', 'poetry_analysis',
            'painting_prompt', 'painting_style', 
            'painting_url', 'painting_url_full', 'painting_local_path',
            'iteration_count', 'user_rating',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_painting_url_full(self, obj):
        """获取完整的图片URL"""
        if obj.painting_local_path:
            request = self.context.get('request')
            if request:
                from django.conf import settings
                return request.build_absolute_uri(settings.MEDIA_URL + obj.painting_local_path)
        return obj.painting_url


class PoetryPaintingConversationSerializer(serializers.ModelSerializer):
    """诗词绘画对话序列化器"""
    
    works_count = serializers.SerializerMethodField()
    latest_work = serializers.SerializerMethodField()
    
    class Meta:
        model = PoetryPaintingConversation
        fields = [
            'id', 'user', 'title', 
            'created_at', 'updated_at',
            'works_count', 'latest_work'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    def get_works_count(self, obj):
        """获取作品数量"""
        return obj.works.count()
    
    def get_latest_work(self, obj):
        """获取最新作品"""
        latest = obj.works.first()
        if latest:
            return PoetryPaintingWorkSerializer(latest, context=self.context).data
        return None


class CreateWorkRequestSerializer(serializers.Serializer):
    """创作作品请求序列化器"""
    
    input = serializers.CharField(required=True, help_text="用户输入/创作主题")
    poetry_style = serializers.CharField(required=False, help_text="诗词风格")
    poetry_format = serializers.CharField(required=False, help_text="诗词格式")
    painting_style = serializers.CharField(required=False, help_text="绘画风格")
    image_size = serializers.CharField(required=False, help_text="图像尺寸")
    conversation_id = serializers.IntegerField(required=False, help_text="对话ID")


class IterateWorkRequestSerializer(serializers.Serializer):
    """迭代优化作品请求序列化器"""
    
    feedback = serializers.CharField(required=True, help_text="用户反馈")
    type = serializers.ChoiceField(
        choices=['poetry', 'painting', 'both'],
        default='both',
        help_text="优化类型"
    )


class RateWorkRequestSerializer(serializers.Serializer):
    """评分作品请求序列化器"""
    
    rating = serializers.IntegerField(min_value=1, max_value=5, help_text="评分(1-5)")

