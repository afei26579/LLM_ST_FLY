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
    
    class Meta:
        model = Conversation
        fields = ['id', 'title', 'created_at', 'updated_at', 'messages', 'message_count']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_message_count(self, obj):
        return obj.messages.count()

class ConversationListSerializer(serializers.ModelSerializer):
    """对话列表序列化器（不包含完整消息）"""
    last_message = serializers.SerializerMethodField()
    message_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = ['id', 'title', 'created_at', 'updated_at', 'last_message', 'message_count']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_last_message(self, obj):
        last_message = obj.messages.last()
        if last_message:
            return MessageSerializer(last_message).data
        return None
    
    def get_message_count(self, obj):
        return obj.messages.count()

class MessageCreateSerializer(serializers.ModelSerializer):
    """创建消息的序列化器"""
    class Meta:
        model = Message
        fields = ['role', 'content', 'conversation']
        read_only_fields = ['id', 'created_at', 'tokens_used'] 