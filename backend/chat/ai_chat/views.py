from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import JSONParser, MultiPartParser

from django.db import transaction
from django.shortcuts import get_object_or_404

from chat.models import Conversation, Message
from chat.ai_chat.serializers import (
    AIChatConversationSerializer, 
    AIChatMessageSerializer,
    AIChatMessageCreateSerializer
)
from chat.ai_chat.services import AIChatService


class AIChatViewSet(viewsets.ModelViewSet):
    """AI Chat 视图集，处理对话和消息相关的API请求"""
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser, MultiPartParser]
    service = AIChatService()

    def get_queryset(self):
        """获取当前用户的对话列表"""
        user = self.request.user
        return Conversation.objects.filter(user=user).order_by('-updated_at')

    def get_serializer_class(self):
        """根据不同的请求类型返回不同的序列化器"""
        if self.action == 'create_message':
            return AIChatMessageCreateSerializer
        if self.action == 'list' or self.action == 'retrieve':
            return AIChatConversationSerializer
        return AIChatConversationSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """创建新的AI对话"""
        try:
            # 获取用户输入的标题
            title = request.data.get('title', '新对话')
            user = request.user
            
            # 创建新对话
            conversation = Conversation.objects.create(
                user=user,
                title=title
            )
            
            # 序列化返回创建的对话
            serializer = self.get_serializer_class()(conversation)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {'detail': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        """删除AI对话"""
        try:
            conversation = get_object_or_404(
                Conversation,
                id=kwargs.get('pk'),
                user=request.user
            )
            
            # 删除对话及其所有消息
            conversation.delete()
            
            return Response(
                {'detail': '对话已删除'}, 
                status=status.HTTP_204_NO_CONTENT
            )
            
        except Exception as e:
            return Response(
                {'detail': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'], url_path='list-conversations')
    def list_conversations(self, request, *args, **kwargs):
        """获取所有对话列表（包含最后一条消息和消息数量）"""
        try:
            user = request.user
            conversations = Conversation.objects.filter(user=user).order_by('-updated_at')
            
            # 序列化对话列表
            serializer = self.get_serializer_class()(conversations, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'detail': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['get'], url_path='get-messages')
    def get_messages(self, request, *args, **kwargs):
        """获取特定对话的所有消息"""
        try:
            conversation = get_object_or_404(
                Conversation,
                id=kwargs.get('pk'),
                user=request.user
            )
            
            # 获取对话的所有消息
            messages = Message.objects.filter(conversation=conversation).order_by('created_at')
            
            # 序列化消息列表
            serializer = AIChatMessageSerializer(messages, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'detail': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'], url_path='create-message')
    def create_message(self, request, *args, **kwargs):
        """发送消息并获取AI回复"""
        try:
            # 验证请求数据
            serializer = self.get_serializer_class()(data=request.data)
            if not serializer.is_valid():
                return Response(
                    serializer.errors, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 获取对话对象
            conversation = get_object_or_404(
                Conversation,
                id=kwargs.get('pk'),
                user=request.user
            )
            
            # 提取请求数据
            message_content = serializer.validated_data.get('content')
            deep_thinking = serializer.validated_data.get('deep_thinking', False)
            web_search = serializer.validated_data.get('web_search', False)
            
            # 调用AI服务处理消息
            result = self.service.process_message(
                conversation=conversation,
                user_message=message_content,
                user=request.user,
                deep_thinking=deep_thinking,
                web_search=web_search
            )
            
            # 返回处理结果
            return Response(result, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'detail': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'], url_path='update-title')
    def update_title(self, request, *args, **kwargs):
        """更新对话标题"""
        try:
            # 获取对话对象
            conversation = get_object_or_404(
                Conversation,
                id=kwargs.get('pk'),
                user=request.user
            )
            
            # 获取新标题
            new_title = request.data.get('title')
            if not new_title or not new_title.strip():
                return Response(
                    {'detail': '标题不能为空'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 更新对话标题
            conversation.title = new_title.strip()
            conversation.save()
            
            # 序列化返回更新后的对话
            serializer = self.get_serializer_class()(conversation)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'detail': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'], url_path='regenerate-response')
    def regenerate_response(self, request, *args, **kwargs):
        """重新生成AI回复"""
        try:
            # 获取对话对象
            conversation = get_object_or_404(
                Conversation,
                id=kwargs.get('pk'),
                user=request.user
            )
            
            # 调用AI服务重新生成回复
            result = self.service.regenerate_response(
                conversation=conversation,
                user=request.user
            )
            
            # 返回处理结果
            return Response(result, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'detail': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'], url_path='get-total-stats')
    def get_total_stats(self, request, *args, **kwargs):
        """获取用户的AI Chat统计信息"""
        try:
            user = request.user
            
            # 计算统计信息
            total_conversations = Conversation.objects.filter(user=user).count()
            total_messages = Message.objects.filter(conversation__user=user).count()
            
            # 获取最近的对话
            recent_conversations = Conversation.objects.filter(user=user)
            .order_by('-updated_at')[:5]
            
            # 序列化最近的对话
            recent_conversations_data = self.get_serializer_class()(recent_conversations, many=True).data
            
            # 构造返回数据
            stats = {
                'total_conversations': total_conversations,
                'total_messages': total_messages,
                'recent_conversations': recent_conversations_data
            }
            
            return Response(stats, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'detail': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )