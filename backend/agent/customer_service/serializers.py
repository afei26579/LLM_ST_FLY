"""
客服系统序列化器
"""
from rest_framework import serializers
from .models import (
    CustomerServiceSession,
    CustomerServiceMessage,
    CustomerServiceKnowledgeBase,
    CustomerServiceStats
)


class CustomerServiceMessageSerializer(serializers.ModelSerializer):
    """客服消息序列化器"""
    
    class Meta:
        model = CustomerServiceMessage
        fields = [
            'id', 'role', 'content', 'intent', 'entities', 
            'confidence', 'tools_result', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class CustomerServiceSessionSerializer(serializers.ModelSerializer):
    """客服会话序列化器"""
    messages = CustomerServiceMessageSerializer(many=True, read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = CustomerServiceSession
        fields = [
            'id', 'session_id', 'user', 'user_name', 'status', 'title',
            'message_count', 'satisfaction_score', 'messages',
            'created_at', 'updated_at', 'ended_at'
        ]
        read_only_fields = ['id', 'session_id', 'created_at', 'updated_at']


class CustomerServiceSessionListSerializer(serializers.ModelSerializer):
    """客服会话列表序列化器（简化版）"""
    user_name = serializers.CharField(source='user.username', read_only=True)
    last_message = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomerServiceSession
        fields = [
            'id', 'session_id', 'user_name', 'status', 'title',
            'message_count', 'last_message', 'created_at', 'updated_at'
        ]
    
    def get_last_message(self, obj):
        """获取最后一条消息"""
        last_msg = obj.messages.last()
        if last_msg:
            return {
                'role': last_msg.role,
                'content': last_msg.content[:100],  # 只返回前100字符
                'created_at': last_msg.created_at
            }
        return None


class ChatRequestSerializer(serializers.Serializer):
    """聊天请求序列化器"""
    message = serializers.CharField(required=True, max_length=2000)
    session_id = serializers.CharField(required=False, allow_blank=True)
    
    def validate_message(self, value):
        """验证消息内容"""
        if not value.strip():
            raise serializers.ValidationError("消息不能为空")
        return value.strip()


class ChatResponseSerializer(serializers.Serializer):
    """聊天响应序列化器"""
    response = serializers.CharField()
    session_id = serializers.CharField()
    intent = serializers.CharField()
    entities = serializers.JSONField()
    need_human = serializers.BooleanField()
    confidence = serializers.FloatField()
    message_id = serializers.IntegerField()


class CustomerServiceKnowledgeBaseSerializer(serializers.ModelSerializer):
    """知识库序列化器"""
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    
    class Meta:
        model = CustomerServiceKnowledgeBase
        fields = [
            'id', 'category', 'category_display', 'question', 'answer',
            'keywords', 'use_count', 'helpful_count', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'use_count', 'helpful_count', 'created_at', 'updated_at']


class CustomerServiceStatsSerializer(serializers.ModelSerializer):
    """客服统计序列化器"""
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = CustomerServiceStats
        fields = [
            'user_name', 'total_sessions', 'resolved_sessions', 
            'transferred_sessions', 'total_messages', 'avg_session_messages',
            'avg_satisfaction_score', 'last_session_at', 'updated_at'
        ]
        read_only_fields = '__all__'


class SatisfactionFeedbackSerializer(serializers.Serializer):
    """满意度反馈序列化器"""
    session_id = serializers.CharField(required=True)
    score = serializers.FloatField(required=True, min_value=1.0, max_value=5.0)
    comment = serializers.CharField(required=False, allow_blank=True, max_length=500)

