from rest_framework import serializers
from .models import Conversation, Message

class MessageSerializer(serializers.ModelSerializer):
    """消息序列化器"""
    class Meta:
        model = Message
        fields = ['id', 'role', 'content', 'created_at', 'tokens_used']
        read_only_fields = ['id', 'created_at', 'tokens_used']

class ConversationSerializer(serializers.ModelSerializer):
    """对话序列化器"""
    messages = MessageSerializer(many=True, read_only=True)
    message_count = serializers.SerializerMethodField()
    display_title = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = ['id', 'title', 'custom_title', 'display_title', 'created_at', 'updated_at', 'messages', 'message_count', 'is_pinned', 'pinned_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_pinned', 'pinned_at', 'display_title']
    
    def get_message_count(self, obj):
        return obj.messages.count()
    
    def get_display_title(self, obj):
        """优先返回自定义标题，如果没有则返回默认标题"""
        return obj.custom_title if obj.custom_title else obj.title

class ConversationListSerializer(serializers.ModelSerializer):
    """对话列表序列化器（不包含完整消息）"""
    last_message = serializers.SerializerMethodField()
    message_count = serializers.SerializerMethodField()
    user_question_count = serializers.SerializerMethodField()
    first_user_question = serializers.SerializerMethodField()
    display_title = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = ['id', 'title', 'custom_title', 'display_title', 'created_at', 'updated_at', 'last_message', 'message_count', 'user_question_count', 'first_user_question', 'is_pinned', 'pinned_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_pinned', 'pinned_at', 'display_title']
    
    def get_last_message(self, obj):
        last_message = obj.messages.last()
        if last_message:
            return MessageSerializer(last_message).data
        return None
    
    def get_message_count(self, obj):
        return obj.messages.count()
    
    def get_user_question_count(self, obj):
        """获取对话中用户问题的数量"""
        return obj.messages.filter(role='user').count()
    
    def get_first_user_question(self, obj):
        """获取第一个用户问题作为预览"""
        first_user_message = obj.messages.filter(role='user').order_by('created_at').first()
        if first_user_message:
            # 截取前50个字符作为预览
            preview = first_user_message.content[:50]
            if len(first_user_message.content) > 50:
                preview += '...'
            return preview
        return ''
    
    def get_display_title(self, obj):
        """优先返回自定义标题，如果没有则返回默认标题"""
        return obj.custom_title if obj.custom_title else obj.title

class MessageCreateSerializer(serializers.ModelSerializer):
    """创建消息的序列化器"""
    class Meta:
        model = Message
        fields = ['role', 'content', 'conversation']
        read_only_fields = ['id', 'created_at', 'tokens_used'] 