from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django.db import transaction

from .models import Conversation, Message
from .serializers import (
    ConversationSerializer, ConversationListSerializer,
    MessageSerializer, MessageCreateSerializer
)
from .services import ChatService, ConversationService, MessageService
from core.response import StandardResponse
from core.views import StandardModelViewSet


class ConversationViewSet(StandardModelViewSet):
    """
    对话管理视图集
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ConversationSerializer
    
    def get_queryset(self):
        # 只返回当前用户的对话
        if self.action == 'list':
            # 列表查询时：优先获取置顶对话，然后获取最新的10条未置顶对话
            from itertools import chain
            
            # 1. 获取所有置顶的对话（按置顶时间降序）
            pinned_conversations = Conversation.objects.filter(
                user=self.request.user, 
                is_pinned=True
            ).order_by('-pinned_at')
            
            # 2. 获取最新的10条未置顶对话（按更新时间降序）
            unpinned_conversations = Conversation.objects.filter(
                user=self.request.user, 
                is_pinned=False
            ).order_by('-updated_at')[:10]
            
            # 3. 合并两个查询集（置顶在前）
            # 使用 chain 合并两个查询集，并转换为列表以支持切片
            combined = list(chain(pinned_conversations, unpinned_conversations))
            
            # 返回合并后的查询集（需要转换回QuerySet以支持后续操作）
            # 获取所有ID
            conversation_ids = [conv.id for conv in combined]
            
            # 使用ID列表创建新的查询集，并保持原有顺序
            from django.db.models import Case, When
            preserved_order = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(conversation_ids)])
            
            return Conversation.objects.filter(
                id__in=conversation_ids
            ).order_by(preserved_order)
        
        # 其他操作（如retrieve详情查询）返回完整查询集，仍按置顶优先排序
        return Conversation.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        # 根据操作选择不同的序列化器
        if self.action == 'list':
            return ConversationListSerializer
        return ConversationSerializer
    
    def create(self, request, *args, **kwargs):
        """
        创建新对话
        """
        try:
            # 使用服务类创建对话
            conversation = ConversationService.create_conversation(
                user=request.user,
                title=request.data.get('title', '新对话')
            )

            # 构建响应
            response_data = self.get_serializer(conversation).data

            return StandardResponse.success(
                data=response_data,
                message="创建成功",
                code=201,
                request_id=getattr(request, 'request_id', None)
            )
        except Exception as e:
            # 返回错误响应而不是抛出异常
            return StandardResponse.error(
                message=f'创建对话失败: {str(e)}',
                code=500,
                request_id=getattr(request, 'request_id', None)
            )
    
    @action(detail=True, methods=['post'])
    def add_message(self, request, pk=None):
        """
        向对话添加消息
        """
        try:
            conversation = self.get_object()
            print(f"向对话添加消息: conversation_id={conversation.id}")
            serializer = MessageCreateSerializer(data=request.data)
            
            if serializer.is_valid():
                instance = serializer.save()
                
                return StandardResponse.success(
                    data=serializer.data,
                    message="消息添加成功",
                    request_id=getattr(request, 'request_id', None)
                )
            else:
                return StandardResponse.error(
                    message="请求参数错误",
                    code=400,
                    data=serializer.errors,
                    request_id=getattr(request, 'request_id', None)
                )
        except Exception as e:
            return StandardResponse.error(
                message=f'添加消息失败: {str(e)}',
                code=500,
                request_id=getattr(request, 'request_id', None)
            )
    
    @action(detail=True, methods=['delete'])
    def clear_messages(self, request, pk=None):
        """
        清空对话中的所有消息
        """
        try:
            conversation = self.get_object()
            count = ConversationService.clear_conversation_messages(conversation)
            
            return StandardResponse.success(
                data=None,
                message=f'对话消息已清空，共删除 {count} 条消息',
                request_id=getattr(request, 'request_id', None)
            )
        except Exception as e:
            print(f"清空消息失败: {str(e)}")
            return StandardResponse.error(
                message=f'清空消息失败: {str(e)}',
                code=500,
                request_id=getattr(request, 'request_id', None)
            )
    
    @action(detail=True, methods=['post'])
    def pin(self, request, pk=None):
        """
        置顶/取消置顶对话
        """
        try:
            from django.utils import timezone
            
            conversation = self.get_object()
            
            # 检查权限
            if conversation.user != request.user:
                return StandardResponse.error(
                    message="无权操作此对话",
                    code=403,
                    request_id=getattr(request, 'request_id', None)
                )
            
            # 切换置顶状态
            conversation.is_pinned = not conversation.is_pinned
            conversation.pinned_at = timezone.now() if conversation.is_pinned else None
            conversation.save()
            
            return StandardResponse.success(
                data={
                    'id': conversation.id,
                    'is_pinned': conversation.is_pinned,
                    'pinned_at': conversation.pinned_at.isoformat() if conversation.pinned_at else None
                },
                message=f"{'已置顶' if conversation.is_pinned else '已取消置顶'}",
                request_id=getattr(request, 'request_id', None)
            )
        except Exception as e:
            print(f"置顶操作失败: {str(e)}")
            return StandardResponse.error(
                message=f'置顶操作失败: {str(e)}',
                code=500,
                request_id=getattr(request, 'request_id', None)
            )
    
    @action(detail=True, methods=['patch'])
    def rename(self, request, pk=None):
        """
        重命名对话（设置自定义标题）
        """
        try:
            conversation = self.get_object()
            
            # 检查权限
            if conversation.user != request.user:
                return StandardResponse.error(
                    message="无权操作此对话",
                    code=403,
                    request_id=getattr(request, 'request_id', None)
                )
            
            # 获取新标题
            new_title = request.data.get('custom_title', '').strip()
            
            if not new_title:
                return StandardResponse.error(
                    message="标题不能为空",
                    code=400,
                    request_id=getattr(request, 'request_id', None)
                )
            
            # 更新自定义标题
            conversation.custom_title = new_title
            conversation.save()
            
            return StandardResponse.success(
                data={
                    'id': conversation.id,
                    'title': conversation.title,
                    'custom_title': conversation.custom_title,
                    'display_title': conversation.custom_title if conversation.custom_title else conversation.title
                },
                message="重命名成功",
                request_id=getattr(request, 'request_id', None)
            )
        except Exception as e:
            print(f"重命名失败: {str(e)}")
            return StandardResponse.error(
                message=f'重命名失败: {str(e)}',
                code=500,
                request_id=getattr(request, 'request_id', None)
            )