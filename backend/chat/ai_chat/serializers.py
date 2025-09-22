from rest_framework import serializers
from chat.models import Conversation, Message


class AIChatMessageSerializer(serializers.ModelSerializer):
    """AI Chat 消息序列化器，用于序列化消息数据"""
    # 格式化时间戳
    timestamp = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    
    class Meta:
        model = Message
        fields = ('id', 'conversation', 'role', 'content', 'timestamp', 'tokens_used', 'thinking_process', 'is_thinking')
        read_only_fields = ('id', 'conversation', 'timestamp', 'tokens_used', 'thinking_process', 'is_thinking')


class AIChatMessageCreateSerializer(serializers.Serializer):
    """AI Chat 消息创建序列化器，用于验证创建消息的请求数据"""
    content = serializers.CharField(required=True, max_length=4000, allow_blank=False)
    deep_thinking = serializers.BooleanField(required=False, default=False)
    web_search = serializers.BooleanField(required=False, default=False)
    files = serializers.ListField(required=False, child=serializers.FileField())
    
    def validate_content(self, value):
        """验证消息内容"""
        if not value or not value.strip():
            raise serializers.ValidationError("消息内容不能为空")
        if len(value.strip()) > 4000:
            raise serializers.ValidationError("消息内容长度不能超过4000字符")
        return value.strip()


class AIChatConversationSerializer(serializers.ModelSerializer):
    """AI Chat 对话序列化器，用于序列化对话数据"""
    # 获取对话中的消息数量
    message_count = serializers.SerializerMethodField()
    
    # 获取最后一条消息的内容作为预览
    last_message_preview = serializers.SerializerMethodField()
    
    # 格式化创建时间和更新时间
    created_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    updated_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    
    class Meta:
        model = Conversation
        fields = ('id', 'user', 'title', 'created_at', 'updated_at', 'message_count', 'last_message_preview')
        read_only_fields = ('id', 'user', 'created_at', 'updated_at', 'message_count', 'last_message_preview')
    
    def get_message_count(self, obj):
        """获取对话中的消息数量"""
        return Message.objects.filter(conversation=obj).count()
    
    def get_last_message_preview(self, obj):
        """获取最后一条消息的内容预览"""
        last_message = Message.objects.filter(conversation=obj).order_by('-created_at').first()
        if last_message:
            # 截取前100个字符作为预览
            preview = last_message.content[:100]
            if len(last_message.content) > 100:
                preview += '...'
            return preview
        return ''


class AIChatConversationDetailSerializer(serializers.ModelSerializer):
    """AI Chat 对话详情序列化器，包含完整的消息列表"""
    # 获取对话中的所有消息
    messages = AIChatMessageSerializer(many=True, read_only=True)
    
    # 格式化时间戳
    created_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    updated_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    
    class Meta:
        model = Conversation
        fields = ('id', 'user', 'title', 'created_at', 'updated_at', 'messages')
        read_only_fields = ('id', 'user', 'created_at', 'updated_at', 'messages')


class AIChatConversationSummarySerializer(serializers.ModelSerializer):
    """AI Chat 对话摘要序列化器，用于列表展示"""
    # 获取最后一条消息的时间
    last_message_time = serializers.SerializerMethodField()
    
    # 判断是否有未读消息（在实际应用中可能需要额外字段来跟踪）
    has_unread = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = ('id', 'title', 'last_message_time', 'has_unread')
        read_only_fields = ('id', 'title', 'last_message_time', 'has_unread')
    
    def get_last_message_time(self, obj):
        """获取最后一条消息的时间"""
        last_message = Message.objects.filter(conversation=obj).order_by('-created_at').first()
        if last_message:
            return last_message.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        return obj.updated_at.strftime('%Y-%m-%d %H:%M:%S')
    
    def get_has_unread(self, obj):
        """判断是否有未读消息"""
        # 这里简化处理，实际应用中可能需要一个字段来跟踪未读状态
        return False


class AIChatHistorySerializer(serializers.Serializer):
    """AI Chat 历史记录序列化器，用于导出和展示历史对话"""
    conversation_id = serializers.IntegerField()
    conversation_title = serializers.CharField()
    export_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    message_count = serializers.IntegerField()
    messages = AIChatMessageSerializer(many=True)


class AIChatUserQuestionSerializer(serializers.ModelSerializer):
    """AI Chat 用户问题序列化器，用于获取用户的提问列表"""
    # 格式化时间戳
    timestamp = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    
    class Meta:
        model = Message
        fields = ('id', 'content', 'timestamp')
        read_only_fields = ('id', 'content', 'timestamp')
    
    def validate(self, data):
        """确保只返回用户角色的消息"""
        if data.get('role') != 'user':
            raise serializers.ValidationError("只能获取用户角色的消息")
        return data