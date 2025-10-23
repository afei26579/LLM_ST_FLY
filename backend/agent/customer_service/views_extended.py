"""
扩展的客服系统视图 - 知识库和助手管理API
"""
import os
import uuid
import logging
from datetime import datetime

from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes, parser_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.utils import timezone
from django.conf import settings
from django.db import transaction
from django.shortcuts import get_object_or_404

from core.response import StandardResponse
from .models_extended import (
    KnowledgeBase,
    KnowledgeDocument,
    DocumentChunk,
    CustomerServiceAssistant,
    ChunkProcessingLog
)
from .serializers_extended import (
    KnowledgeBaseSerializer,
    KnowledgeDocumentSerializer,
    DocumentUploadSerializer,
    DocumentChunkSerializer,
    CustomerServiceAssistantSerializer,
    AssistantCreateSerializer,
    ChunkProcessingLogSerializer
)

logger = logging.getLogger(__name__)


class KnowledgeBaseViewSet(viewsets.ModelViewSet):
    """知识库管理视图集"""
    permission_classes = [IsAuthenticated]
    serializer_class = KnowledgeBaseSerializer
    
    def get_queryset(self):
        """只返回当前用户的知识库"""
        return KnowledgeBase.objects.filter(user=self.request.user)
    
    def list(self, request, *args, **kwargs):
        """获取知识库列表"""
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            
            return StandardResponse.success(
                data=serializer.data,
                message='获取知识库列表成功'
            )
        except Exception as e:
            logger.error(f"获取知识库列表失败: {str(e)}", exc_info=True)
            return StandardResponse.error(message=f'获取知识库列表失败: {str(e)}')
    
    def retrieve(self, request, *args, **kwargs):
        """获取单个知识库详情"""
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            
            return StandardResponse.success(
                data=serializer.data,
                message='获取知识库详情成功'
            )
        except Exception as e:
            logger.error(f"获取知识库详情失败: {str(e)}", exc_info=True)
            return StandardResponse.error(message=f'获取知识库详情失败: {str(e)}')
    
    def create(self, request, *args, **kwargs):
        """创建知识库"""
        try:
            data = request.data.copy()
            data['user'] = request.user.id
            
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            
            # 创建知识库
            kb = serializer.save(status='ready')
            
            logger.info(f"用户 {request.user.username} 创建知识库: {kb.name}")
            
            return StandardResponse.success(
                data=KnowledgeBaseSerializer(kb).data,
                message='知识库创建成功',
                code=201
            )
        except Exception as e:
            logger.error(f"创建知识库失败: {str(e)}", exc_info=True)
            return StandardResponse.error(message=f'创建知识库失败: {str(e)}')
    
    def update(self, request, *args, **kwargs):
        """更新知识库"""
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            
            logger.info(f"用户 {request.user.username} 更新知识库: {instance.name}")
            
            return StandardResponse.success(
                data=serializer.data,
                message='知识库更新成功'
            )
        except Exception as e:
            logger.error(f"更新知识库失败: {str(e)}", exc_info=True)
            return StandardResponse.error(message=f'更新知识库失败: {str(e)}')
    
    def destroy(self, request, *args, **kwargs):
        """删除知识库"""
        try:
            instance = self.get_object()
            kb_name = instance.name
            
            # 删除关联的文档文件
            for doc in instance.documents.all():
                if doc.file_path and os.path.exists(doc.file_path):
                    try:
                        os.remove(doc.file_path)
                    except Exception as e:
                        logger.warning(f"删除文件失败 {doc.file_path}: {str(e)}")
            
            instance.delete()
            
            logger.info(f"用户 {request.user.username} 删除知识库: {kb_name}")
            
            return StandardResponse.success(
                message='知识库删除成功'
            )
        except Exception as e:
            logger.error(f"删除知识库失败: {str(e)}", exc_info=True)
            return StandardResponse.error(message=f'删除知识库失败: {str(e)}')
    
    @action(detail=True, methods=['get'])
    def documents(self, request, pk=None):
        """获取知识库的所有文档"""
        try:
            kb = self.get_object()
            documents = kb.documents.all()
            serializer = KnowledgeDocumentSerializer(documents, many=True)
            
            return StandardResponse.success(
                data=serializer.data,
                message='获取文档列表成功'
            )
        except Exception as e:
            logger.error(f"获取文档列表失败: {str(e)}", exc_info=True)
            return StandardResponse.error(message=f'获取文档列表失败: {str(e)}')
    
    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def upload_document(self, request, pk=None):
        """上传文档到知识库"""
        try:
            kb = self.get_object()
            
            # 验证上传数据
            upload_serializer = DocumentUploadSerializer(data=request.data)
            upload_serializer.is_valid(raise_exception=True)
            
            uploaded_file = upload_serializer.validated_data['file']
            chunk_strategy = upload_serializer.validated_data.get('chunk_strategy', 'auto')
            chunk_size = upload_serializer.validated_data.get('chunk_size', 500)
            chunk_overlap = upload_serializer.validated_data.get('chunk_overlap', 50)
            clean_strategy = upload_serializer.validated_data.get('clean_strategy', 'auto')
            
            # 保存文件
            media_root = settings.MEDIA_ROOT
            upload_dir = os.path.join(media_root, 'knowledge-base', str(kb.id))
            os.makedirs(upload_dir, exist_ok=True)
            
            file_ext = os.path.splitext(uploaded_file.name)[1]
            filename = f"{uuid.uuid4()}{file_ext}"
            file_path = os.path.join(upload_dir, filename)
            
            with open(file_path, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)
            
            # 创建文档记录
            document = KnowledgeDocument.objects.create(
                knowledge_base=kb,
                filename=uploaded_file.name,
                file_type=file_ext.lower().replace('.', ''),
                file_size=uploaded_file.size,
                file_path=file_path,
                chunk_strategy=chunk_strategy,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                clean_strategy=clean_strategy,
                status='processing'
            )
            
            # TODO: 异步处理文档（切片、向量化）
            # 这里可以使用 Celery 或 Django-Q 等任务队列
            # 暂时标记为已完成
            document.status = 'completed'
            document.processed_at = timezone.now()
            document.save()
            
            # 更新知识库统计
            kb.document_count = kb.documents.count()
            kb.save()
            
            logger.info(f"文档上传成功: {uploaded_file.name} -> KB: {kb.name}")
            
            return StandardResponse.success(
                data=KnowledgeDocumentSerializer(document).data,
                message='文档上传成功',
                code=201
            )
            
        except Exception as e:
            logger.error(f"文档上传失败: {str(e)}", exc_info=True)
            return StandardResponse.error(message=f'文档上传失败: {str(e)}')
    
    @action(detail=True, methods=['get'])
    def chunks(self, request, pk=None):
        """获取知识库的所有切片"""
        try:
            kb = self.get_object()
            chunks = DocumentChunk.objects.filter(knowledge_base=kb)
            
            # 分页
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 20))
            
            start = (page - 1) * page_size
            end = start + page_size
            
            total = chunks.count()
            chunk_list = chunks[start:end]
            
            serializer = DocumentChunkSerializer(chunk_list, many=True)
            
            return StandardResponse.success(
                data={
                    'list': serializer.data,
                    'total': total,
                    'page': page,
                    'page_size': page_size
                },
                message='获取切片列表成功'
            )
        except Exception as e:
            logger.error(f"获取切片列表失败: {str(e)}", exc_info=True)
            return StandardResponse.error(message=f'获取切片列表失败: {str(e)}')


class KnowledgeDocumentViewSet(viewsets.ModelViewSet):
    """知识库文档管理视图集"""
    permission_classes = [IsAuthenticated]
    serializer_class = KnowledgeDocumentSerializer
    
    def get_queryset(self):
        """只返回当前用户的文档"""
        return KnowledgeDocument.objects.filter(
            knowledge_base__user=self.request.user
        )
    
    def destroy(self, request, *args, **kwargs):
        """删除文档"""
        try:
            instance = self.get_object()
            kb = instance.knowledge_base
            
            # 删除文件
            if instance.file_path and os.path.exists(instance.file_path):
                try:
                    os.remove(instance.file_path)
                except Exception as e:
                    logger.warning(f"删除文件失败 {instance.file_path}: {str(e)}")
            
            # 删除相关切片
            DocumentChunk.objects.filter(document=instance).delete()
            
            instance.delete()
            
            # 更新知识库统计
            kb.document_count = kb.documents.count()
            kb.chunk_count = DocumentChunk.objects.filter(knowledge_base=kb).count()
            kb.save()
            
            logger.info(f"删除文档成功: {instance.filename}")
            
            return StandardResponse.success(message='文档删除成功')
            
        except Exception as e:
            logger.error(f"删除文档失败: {str(e)}", exc_info=True)
            return StandardResponse.error(message=f'删除文档失败: {str(e)}')


class CustomerServiceAssistantViewSet(viewsets.ModelViewSet):
    """客服助手管理视图集"""
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """只返回当前用户的助手"""
        return CustomerServiceAssistant.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        """根据动作选择序列化器"""
        if self.action == 'create':
            return AssistantCreateSerializer
        return CustomerServiceAssistantSerializer
    
    def list(self, request, *args, **kwargs):
        """获取助手列表"""
        try:
            queryset = self.get_queryset()
            serializer = CustomerServiceAssistantSerializer(queryset, many=True)
            
            return StandardResponse.success(
                data=serializer.data,
                message='获取助手列表成功'
            )
        except Exception as e:
            logger.error(f"获取助手列表失败: {str(e)}", exc_info=True)
            return StandardResponse.error(message=f'获取助手列表失败: {str(e)}')
    
    def retrieve(self, request, *args, **kwargs):
        """获取单个助手详情"""
        try:
            instance = self.get_object()
            serializer = CustomerServiceAssistantSerializer(instance)
            
            return StandardResponse.success(
                data=serializer.data,
                message='获取助手详情成功'
            )
        except Exception as e:
            logger.error(f"获取助手详情失败: {str(e)}", exc_info=True)
            return StandardResponse.error(message=f'获取助手详情失败: {str(e)}')
    
    def create(self, request, *args, **kwargs):
        """创建助手"""
        try:
            data = request.data.copy()
            data['user'] = request.user.id
            
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            
            # 如果设置为默认助手，取消其他助手的默认状态
            is_default = serializer.validated_data.get('is_default', False)
            if is_default:
                CustomerServiceAssistant.objects.filter(
                    user=request.user,
                    is_default=True
                ).update(is_default=False)
            
            assistant = serializer.save()
            
            logger.info(f"用户 {request.user.username} 创建助手: {assistant.name}")
            
            return StandardResponse.success(
                data=CustomerServiceAssistantSerializer(assistant).data,
                message='助手创建成功',
                code=201
            )
        except Exception as e:
            logger.error(f"创建助手失败: {str(e)}", exc_info=True)
            return StandardResponse.error(message=f'创建助手失败: {str(e)}')
    
    def update(self, request, *args, **kwargs):
        """更新助手"""
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            
            # 如果设置为默认助手，取消其他助手的默认状态
            if request.data.get('is_default') == True:
                CustomerServiceAssistant.objects.filter(
                    user=request.user,
                    is_default=True
                ).exclude(id=instance.id).update(is_default=False)
            
            serializer = CustomerServiceAssistantSerializer(
                instance, 
                data=request.data, 
                partial=partial
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            
            logger.info(f"用户 {request.user.username} 更新助手: {instance.name}")
            
            return StandardResponse.success(
                data=serializer.data,
                message='助手更新成功'
            )
        except Exception as e:
            logger.error(f"更新助手失败: {str(e)}", exc_info=True)
            return StandardResponse.error(message=f'更新助手失败: {str(e)}')
    
    def destroy(self, request, *args, **kwargs):
        """删除助手"""
        try:
            instance = self.get_object()
            assistant_name = instance.name
            
            # 如果是默认助手，不允许删除（或设置其他助手为默认）
            if instance.is_default:
                # 尝试设置另一个助手为默认
                other_assistant = CustomerServiceAssistant.objects.filter(
                    user=request.user
                ).exclude(id=instance.id).first()
                
                if other_assistant:
                    other_assistant.is_default = True
                    other_assistant.save()
            
            instance.delete()
            
            logger.info(f"用户 {request.user.username} 删除助手: {assistant_name}")
            
            return StandardResponse.success(message='助手删除成功')
            
        except Exception as e:
            logger.error(f"删除助手失败: {str(e)}", exc_info=True)
            return StandardResponse.error(message=f'删除助手失败: {str(e)}')
    
    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        """设置为默认助手"""
        try:
            instance = self.get_object()
            
            # 取消其他助手的默认状态
            CustomerServiceAssistant.objects.filter(
                user=request.user,
                is_default=True
            ).update(is_default=False)
            
            # 设置当前助手为默认
            instance.is_default = True
            instance.save()
            
            logger.info(f"设置默认助手: {instance.name}")
            
            return StandardResponse.success(
                data=CustomerServiceAssistantSerializer(instance).data,
                message='设置默认助手成功'
            )
        except Exception as e:
            logger.error(f"设置默认助手失败: {str(e)}", exc_info=True)
            return StandardResponse.error(message=f'设置默认助手失败: {str(e)}')
    
    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """获取助手统计信息"""
        try:
            instance = self.get_object()
            
            stats = {
                'total_conversations': instance.total_conversations,
                'total_messages': instance.total_messages,
                'avg_satisfaction': instance.avg_satisfaction,
                'knowledge_bases_count': instance.knowledge_bases.count(),
                'created_at': instance.created_at,
                'last_updated': instance.updated_at
            }
            
            return StandardResponse.success(
                data=stats,
                message='获取统计信息成功'
            )
        except Exception as e:
            logger.error(f"获取统计信息失败: {str(e)}", exc_info=True)
            return StandardResponse.error(message=f'获取统计信息失败: {str(e)}')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_default_assistant(request):
    """获取用户的默认助手"""
    try:
        assistant = CustomerServiceAssistant.objects.filter(
            user=request.user,
            is_default=True,
            is_active=True
        ).first()
        
        if not assistant:
            # 如果没有默认助手，返回第一个激活的助手
            assistant = CustomerServiceAssistant.objects.filter(
                user=request.user,
                is_active=True
            ).first()
        
        if assistant:
            return StandardResponse.success(
                data=CustomerServiceAssistantSerializer(assistant).data,
                message='获取默认助手成功'
            )
        else:
            return StandardResponse.error(
                message='未找到可用的助手',
                code=404
            )
            
    except Exception as e:
        logger.error(f"获取默认助手失败: {str(e)}", exc_info=True)
        return StandardResponse.error(message=f'获取默认助手失败: {str(e)}')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_knowledge(request):
    """搜索知识库"""
    try:
        query = request.query_params.get('q', '')
        kb_ids = request.query_params.getlist('kb_ids[]')
        limit = int(request.query_params.get('limit', 5))
        
        if not query:
            return StandardResponse.error(message='搜索关键词不能为空')
        
        # 简单的文本搜索（后续可以替换为向量搜索）
        chunks_query = DocumentChunk.objects.filter(
            knowledge_base__user=request.user,
            content__icontains=query
        )
        
        if kb_ids:
            chunks_query = chunks_query.filter(knowledge_base_id__in=kb_ids)
        
        chunks = chunks_query.order_by('-created_at')[:limit]
        
        results = []
        for chunk in chunks:
            results.append({
                'content': chunk.content,
                'source': chunk.document.filename,
                'kb_name': chunk.knowledge_base.name,
                'score': 1.0  # 占位符，实际应该是相似度分数
            })
        
        return StandardResponse.success(
            data=results,
            message='搜索成功'
        )
        
    except Exception as e:
        logger.error(f"搜索知识库失败: {str(e)}", exc_info=True)
        return StandardResponse.error(message=f'搜索失败: {str(e)}')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def chunk_documents(request):
    """文档切片处理"""
    try:
        from .document_processor import DocumentProcessor, DocumentCleaner
        
        kb_id = request.data.get('knowledge_base_id')
        files = request.FILES.getlist('files')
        
        # 切片配置
        chunk_strategy = request.data.get('chunk_strategy', 'auto')
        chunk_separator = request.data.get('chunk_separator', '\n')
        chunk_max_length = int(request.data.get('chunk_max_length', 800))
        chunk_overlap = int(request.data.get('chunk_overlap', 10))
        remove_spaces = request.data.get('remove_spaces', 'true').lower() == 'true'
        remove_urls = request.data.get('remove_urls', 'false').lower() == 'true'
        
        if not kb_id:
            return StandardResponse.error(message='缺少knowledge_base_id参数')
        
        if not files:
            return StandardResponse.error(message='请上传至少一个文件')
        
        # 获取知识库
        kb = get_object_or_404(KnowledgeBase, id=kb_id, user=request.user)
        kb.status = 'processing'
        kb.save()
        
        processor = DocumentProcessor()
        all_chunks = []
        documents_created = []
        
        for uploaded_file in files:
            try:
                # 保存文件
                media_root = settings.MEDIA_ROOT
                upload_dir = os.path.join(media_root, 'knowledge-base', str(kb.id))
                os.makedirs(upload_dir, exist_ok=True)
                
                file_ext = os.path.splitext(uploaded_file.name)[1].lower()
                filename = f"{uuid.uuid4()}{file_ext}"
                file_path = os.path.join(upload_dir, filename)
                
                with open(file_path, 'wb+') as destination:
                    for chunk in uploaded_file.chunks():
                        destination.write(chunk)
                
                # 创建文档记录
                document = KnowledgeDocument.objects.create(
                    knowledge_base=kb,
                    filename=uploaded_file.name,
                    file_type=file_ext.replace('.', ''),
                    file_size=uploaded_file.size,
                    file_path=file_path,
                    chunk_strategy=chunk_strategy,
                    chunk_size=chunk_max_length,
                    chunk_overlap=chunk_overlap,
                    status='processing'
                )
                documents_created.append(document)
                
                # 处理文档 - 根据格式选择处理方式
                chunks_data = processor.process_document(
                    file_path=file_path,
                    file_type=file_ext.replace('.', ''),
                    kb_format=kb.format,
                    chunk_strategy=chunk_strategy,
                    chunk_size=chunk_max_length,
                    chunk_overlap=chunk_overlap,
                    remove_spaces=remove_spaces,
                    remove_urls=remove_urls,
                    separator=chunk_separator
                )
                
                # 准备返回的切片数据
                for idx, chunk_data in enumerate(chunks_data):
                    all_chunks.append({
                        'content': chunk_data['content'],
                        'index': idx,
                        'metadata': {
                            'source': uploaded_file.name,
                            'document_id': document.id,
                            **chunk_data.get('metadata', {})
                        }
                    })
                
                # 更新文档状态
                document.chunk_count = len(chunks_data)
                document.status = 'completed'
                document.processed_at = timezone.now()
                document.save()
                
                logger.info(f"文档切片成功: {uploaded_file.name}, 生成 {len(chunks_data)} 个切片")
                
            except Exception as e:
                logger.error(f"处理文档 {uploaded_file.name} 失败: {str(e)}", exc_info=True)
                if 'document' in locals():
                    document.status = 'failed'
                    document.error_message = str(e)
                    document.save()
        
        # 更新知识库统计
        kb.document_count = kb.documents.count()
        kb.chunk_count = sum(doc.chunk_count for doc in documents_created)
        kb.status = 'ready'
        kb.save()
        
        return StandardResponse.success(
            data={
                'chunks': all_chunks,
                'total_chunks': len(all_chunks),
                'documents_processed': len(documents_created)
            },
            message=f'文档切片完成，共生成 {len(all_chunks)} 个切片'
        )
        
    except Exception as e:
        logger.error(f"文档切片失败: {str(e)}", exc_info=True)
        if 'kb' in locals():
            kb.status = 'error'
            kb.error_message = str(e)
            kb.save()
        return StandardResponse.error(message=f'文档切片失败: {str(e)}')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def vectorize_chunks(request):
    """向量化切片并存储到ChromaDB"""
    try:
        from .vector_service import VectorService
        
        kb_id = request.data.get('knowledge_base_id')
        chunks_data = request.data.get('chunks', [])
        
        if not kb_id:
            return StandardResponse.error(message='缺少knowledge_base_id参数')
        
        if not chunks_data:
            return StandardResponse.error(message='缺少切片数据')
        
        # 获取知识库
        kb = get_object_or_404(KnowledgeBase, id=kb_id, user=request.user)
        
        vector_service = VectorService()
        vectorized_count = 0
        
        # 准备批量向量化的数据
        texts = []
        chunk_mappings = []
        
        for chunk_data in chunks_data:
            content = chunk_data.get('content', '')
            metadata = chunk_data.get('metadata', {})
            
            if content:
                texts.append(content)
                chunk_mappings.append({
                    'content': content,
                    'index': chunk_data.get('index', 0),
                    'metadata': metadata
                })
        
        # 批量生成向量
        logger.info(f"开始批量向量化 {len(texts)} 个切片")
        embeddings = vector_service.get_embeddings_batch(texts)
        
        # 准备存储到ChromaDB的数据
        chroma_chunks = []
        db_chunks = []
        chunk_id_mapping = {}  # 用于记录chunk_id和数据库ID的映射
        
        for i, (chunk_mapping, embedding) in enumerate(zip(chunk_mappings, embeddings)):
            metadata = chunk_mapping['metadata']
            document_id = metadata.get('document_id')
            
            if not document_id:
                continue
            
            # 获取文档
            try:
                document = KnowledgeDocument.objects.get(id=document_id)
            except KnowledgeDocument.DoesNotExist:
                logger.warning(f"文档 {document_id} 不存在")
                continue
            
            # 先创建数据库记录，获取真实的chunk_id
            db_chunk = DocumentChunk(
                document=document,
                knowledge_base=kb,
                content=chunk_mapping['content'],
                chunk_index=chunk_mapping['index'],
                embedding='',  # 向量存储在ChromaDB，这里保存ChromaDB的chunk_id作为引用
                metadata=metadata,
                token_count=len(chunk_mapping['content']) // 4
            )
            db_chunks.append(db_chunk)
        
        # 批量创建数据库记录
        created_chunks = DocumentChunk.objects.bulk_create(db_chunks)
        
        # 准备ChromaDB数据（使用数据库生成的ID）
        for db_chunk in created_chunks:
            # ChromaDB的ID使用数据库chunk的ID，确保唯一性和可追溯性
            chunk_id = f"chunk_{db_chunk.id}"
            
            # 更新数据库记录，保存ChromaDB的引用ID
            db_chunk.embedding = chunk_id
            
            # 增强元数据，添加数据库关联信息
            enhanced_metadata = {
                **db_chunk.metadata,
                'db_chunk_id': db_chunk.id,
                'kb_id': kb.id,
                'kb_name': kb.name,
                'document_id': db_chunk.document.id,
                'document_name': db_chunk.document.filename,
                'chunk_index': db_chunk.chunk_index
            }
            
            chroma_chunks.append({
                'id': chunk_id,
                'content': db_chunk.content,
                'embedding': None,  # 稍后批量添加
                'metadata': enhanced_metadata,
                'index': db_chunk.chunk_index
            })
        
        # 批量更新数据库记录的embedding字段
        DocumentChunk.objects.bulk_update(created_chunks, ['embedding'])
        
        # 提取embeddings
        for i, chunk in enumerate(chroma_chunks):
            chunk['embedding'] = embeddings[i]
        
        # 批量存储到ChromaDB
        logger.info(f"存储 {len(chroma_chunks)} 个切片到ChromaDB")
        vector_service.add_chunks_to_collection(
            kb_id=kb.id,
            kb_name=kb.name,
            chunks=chroma_chunks
        )
        
        vectorized_count = len(created_chunks)
        
        # 更新知识库统计
        kb.chunk_count = DocumentChunk.objects.filter(knowledge_base=kb).count()
        kb.total_tokens = sum(chunk.token_count for chunk in DocumentChunk.objects.filter(knowledge_base=kb))
        kb.status = 'ready'
        kb.save()
        
        logger.info(f"向量化完成: KB={kb.name}, 处理 {vectorized_count} 个切片")
        
        return StandardResponse.success(
            data={
                'vectorized_count': vectorized_count,
                'total_chunks': kb.chunk_count,
                'total_tokens': kb.total_tokens
            },
            message=f'向量化完成，处理 {vectorized_count} 个切片'
        )
        
    except Exception as e:
        logger.error(f"向量化失败: {str(e)}", exc_info=True)
        return StandardResponse.error(message=f'向量化失败: {str(e)}')