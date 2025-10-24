"""
扩展的序列化器 - 知识库和助手配置
"""
from rest_framework import serializers
from .models_extended import (
    KnowledgeBase,
    KnowledgeDocument,
    DocumentChunk,
    CustomerServiceAssistant,
    ChunkProcessingLog
)


class KnowledgeBaseSerializer(serializers.ModelSerializer):
    """知识库序列化器"""
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = KnowledgeBase
        fields = [
            'id', 'name', 'description', 'format', 'status', 'error_message',
            'document_count', 'chunk_count', 'total_tokens',
            'domain', 'summary', 'key_points', 'keywords', 'suggested_questions',
            'user', 'user_name', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'status', 'error_message', 'document_count',
            'chunk_count', 'total_tokens', 'domain', 'summary',
            'key_points', 'keywords', 'suggested_questions',
            'created_at', 'updated_at'
        ]


class KnowledgeDocumentSerializer(serializers.ModelSerializer):
    """知识库文档序列化器"""
    kb_name = serializers.CharField(source='knowledge_base.name', read_only=True)
    
    class Meta:
        model = KnowledgeDocument
        fields = [
            'id', 'knowledge_base', 'kb_name', 'filename', 'file_type',
            'file_size', 'file_path', 'status', 'error_message',
            'chunk_strategy', 'chunk_size', 'chunk_overlap',
            'clean_strategy', 'chunk_count', 'token_count',
            'metadata', 'created_at', 'updated_at', 'processed_at'
        ]
        read_only_fields = [
            'id', 'status', 'error_message', 'chunk_count',
            'token_count', 'created_at', 'updated_at', 'processed_at'
        ]


class DocumentUploadSerializer(serializers.Serializer):
    """文档上传序列化器"""
    knowledge_base_id = serializers.IntegerField(required=True)
    file = serializers.FileField(required=True)
    chunk_strategy = serializers.ChoiceField(
        choices=['auto', 'fixed', 'semantic'],
        default='auto'
    )
    chunk_size = serializers.IntegerField(default=500, min_value=100, max_value=2000)
    chunk_overlap = serializers.IntegerField(default=50, min_value=0, max_value=500)
    clean_strategy = serializers.ChoiceField(
        choices=['auto', 'basic', 'none'],
        default='auto'
    )
    custom_clean_rules = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        allow_empty=True
    )


class DocumentChunkSerializer(serializers.ModelSerializer):
    """文档切片序列化器"""
    document_name = serializers.CharField(source='document.filename', read_only=True)
    kb_name = serializers.CharField(source='knowledge_base.name', read_only=True)
    
    class Meta:
        model = DocumentChunk
        fields = [
            'id', 'document', 'document_name', 'knowledge_base', 'kb_name',
            'content', 'chunk_index', 'metadata', 'token_count', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class CustomerServiceAssistantSerializer(serializers.ModelSerializer):
    """客服助手序列化器"""
    user_name = serializers.CharField(source='user.username', read_only=True)
    knowledge_bases_info = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomerServiceAssistant
        fields = [
            'id', 'name', 'description', 'avatar', 'greeting_message',
            'system_prompt', 'knowledge_bases', 'knowledge_bases_info',
            'model', 'temperature', 'top_k',
            'enable_knowledge_base', 'enable_order_query', 'enable_human_handoff',
            'is_active', 'is_default',
            'total_conversations', 'total_messages', 'avg_satisfaction',
            'user', 'user_name', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'total_conversations', 'total_messages',
            'avg_satisfaction', 'created_at', 'updated_at'
        ]
    
    def get_knowledge_bases_info(self, obj):
        """获取知识库信息"""
        kbs = obj.knowledge_bases.all()
        return [
            {
                'id': kb.id,
                'name': kb.name,
                'chunk_count': kb.chunk_count,
                'status': kb.status
            }
            for kb in kbs
        ]


class AssistantCreateSerializer(serializers.ModelSerializer):
    """助手创建序列化器"""
    knowledge_base_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        allow_empty=True
    )
    
    class Meta:
        model = CustomerServiceAssistant
        fields = [
            'name', 'description', 'avatar', 'greeting_message',
            'system_prompt', 'knowledge_base_ids',
            'model', 'temperature', 'top_k',
            'enable_knowledge_base', 'enable_order_query', 'enable_human_handoff',
            'is_active', 'is_default', 'user'
        ]
    
    def validate_temperature(self, value):
        """验证温度参数"""
        if not 0 <= value <= 2:
            raise serializers.ValidationError("温度参数必须在0-2之间")
        return value
    
    def validate_top_k(self, value):
        """验证检索数量"""
        if not 1 <= value <= 20:
            raise serializers.ValidationError("检索数量必须在1-20之间")
        return value
    
    def create(self, validated_data):
        """创建助手并关联知识库"""
        knowledge_base_ids = validated_data.pop('knowledge_base_ids', [])
        
        # 创建助手
        assistant = CustomerServiceAssistant.objects.create(**validated_data)
        
        # 关联知识库
        if knowledge_base_ids:
            assistant.knowledge_bases.set(knowledge_base_ids)
        
        return assistant


class AssistantTestSerializer(serializers.Serializer):
    """助手测试序列化器"""
    assistant_id = serializers.IntegerField(required=True)
    message = serializers.CharField(required=True, max_length=2000)


class ChunkProcessingLogSerializer(serializers.ModelSerializer):
    """切片处理日志序列化器"""
    document_name = serializers.CharField(source='document.filename', read_only=True)
    
    class Meta:
        model = ChunkProcessingLog
        fields = [
            'id', 'document', 'document_name', 'step', 'status',
            'message', 'details', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class KnowledgeSearchSerializer(serializers.Serializer):
    """知识库搜索序列化器"""
    query = serializers.CharField(required=True, max_length=500)
    knowledge_base_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=True,
        min_length=1
    )
    top_k = serializers.IntegerField(default=5, min_value=1, max_value=20)
    search_type = serializers.ChoiceField(
        choices=['vector', 'keyword', 'hybrid'],
        default='hybrid'
    )


class KnowledgeSearchResultSerializer(serializers.Serializer):
    """知识库搜索结果序列化器"""
    id = serializers.IntegerField()
    content = serializers.CharField()
    filename = serializers.CharField()
    kb_name = serializers.CharField()
    chunk_index = serializers.IntegerField()
    similarity = serializers.FloatField(required=False)
    final_score = serializers.FloatField(required=False)
    metadata = serializers.DictField()

