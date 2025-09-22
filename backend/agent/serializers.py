"""
智能体序列化器
"""

from rest_framework import serializers
from .models import Agent, Conversation, Message, UserAgentStats, AgentType


class AgentSerializer(serializers.ModelSerializer):
    """智能体序列化器"""
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    
    class Meta:
        model = Agent
        fields = [
            'id', 'name', 'type', 'type_display', 'description', 
            'avatar', 'greeting_message', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ConversationSerializer(serializers.ModelSerializer):
    """对话会话序列化器"""
    agent_name = serializers.CharField(source='agent.name', read_only=True)
    agent_type = serializers.CharField(source='agent.type', read_only=True)
    agent_avatar = serializers.URLField(source='agent.avatar', read_only=True)
    
    class Meta:
        model = Conversation
        fields = [
            'id', 'title', 'agent_name', 'agent_type', 'agent_avatar',
            'started_at', 'last_message_at', 'is_active', 'message_count'
        ]
        read_only_fields = ['id', 'started_at', 'last_message_at']


class MessageSerializer(serializers.ModelSerializer):
    """消息序列化器"""
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    
    class Meta:
        model = Message
        fields = [
            'id', 'type', 'type_display', 'content', 'metadata', 
            'created_at', 'tokens_used'
        ]
        read_only_fields = ['id', 'created_at', 'tokens_used']


class ConversationDetailSerializer(ConversationSerializer):
    """对话会话详情序列化器（包含消息）"""
    messages = MessageSerializer(many=True, read_only=True)
    agent = AgentSerializer(read_only=True)
    
    class Meta(ConversationSerializer.Meta):
        fields = ConversationSerializer.Meta.fields + ['messages', 'agent']


class UserAgentStatsSerializer(serializers.ModelSerializer):
    """用户智能体统计序列化器"""
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = UserAgentStats
        fields = [
            'username', 'total_conversations', 'total_messages', 
            'total_tokens_used', 'travel_conversations', 
            'poetry_conversations', 'service_conversations',
            'last_used_at', 'created_at'
        ]
        read_only_fields = ['username', 'created_at']


class ChatRequest(serializers.Serializer):
    """聊天请求序列化器"""
    message = serializers.CharField(
        max_length=2000,
        help_text="用户消息内容"
    )
    conversation_id = serializers.UUIDField(
        required=False,
        allow_null=True,
        help_text="对话会话ID，新对话可不传"
    )
    agent_type = serializers.ChoiceField(
        choices=AgentType.choices,
        help_text="智能体类型"
    )
    
    def validate_message(self, value):
        """验证消息内容"""
        if not value.strip():
            raise serializers.ValidationError("消息内容不能为空")
        return value.strip()


class ChatResponse(serializers.Serializer):
    """聊天响应序列化器"""
    conversation_id = serializers.UUIDField(help_text="对话会话ID")
    message = serializers.CharField(help_text="智能体回复内容")
    message_id = serializers.UUIDField(help_text="消息ID")
    agent = AgentSerializer(help_text="智能体信息")
    tokens_used = serializers.IntegerField(help_text="本次对话消耗的Token数")
    is_new_conversation = serializers.BooleanField(help_text="是否为新对话")


class CreateConversationRequest(serializers.Serializer):
    """创建对话请求序列化器"""
    agent_type = serializers.ChoiceField(
        choices=AgentType.choices,
        help_text="智能体类型"
    )
    title = serializers.CharField(
        max_length=200,
        required=False,
        help_text="对话标题，不传则自动生成"
    )
    
    def validate_title(self, value):
        """验证标题"""
        if value and not value.strip():
            raise serializers.ValidationError("标题不能为空字符串")
        return value.strip() if value else None


class ConversationListRequest(serializers.Serializer):
    """对话列表请求序列化器"""
    agent_type = serializers.ChoiceField(
        choices=AgentType.choices,
        required=False,
        allow_null=True,
        help_text="按智能体类型筛选"
    )
    limit = serializers.IntegerField(
        default=20,
        min_value=1,
        max_value=100,
        help_text="返回数量限制"
    )
    offset = serializers.IntegerField(
        default=0,
        min_value=0,
        help_text="偏移量"
    )
