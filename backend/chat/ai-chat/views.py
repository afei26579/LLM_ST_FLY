from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import JSONParser, MultiPartParser
from rest_framework.renderers import BaseRenderer
from django.http import StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json

from django.db import transaction
from django.shortcuts import get_object_or_404

from chat.models import Conversation, Message
from .serializers import (
    AIChatConversationSerializer, 
    AIChatMessageSerializer,
    AIChatMessageCreateSerializer
)
from .services import AIChatService


@csrf_exempt
def stream_chat_view(request):
    """独立的流式聊天视图函数 - 避免DRF内容协商问题"""
    if request.method != 'POST':
        return StreamingHttpResponse(
            iter([f"data: {json.dumps({'error': '只支持POST方法'})}\n\n"]),
            content_type='text/event-stream'
        )
    
    # JWT认证
    from rest_framework_simplejwt.authentication import JWTAuthentication
    from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
    
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        def error_stream():
            yield f"data: {json.dumps({'error': '需要Authorization header'})}\n\n"
        return StreamingHttpResponse(
            error_stream(),
            content_type='text/event-stream'
        )
    
    try:
        jwt_auth = JWTAuthentication()
        validated_token = jwt_auth.get_validated_token(auth_header.split(' ')[1])
        user = jwt_auth.get_user(validated_token)
        request.user = user
    except (InvalidToken, TokenError) as e:
        def error_stream():
            yield f"data: {json.dumps({'error': '无效的认证令牌'})}\n\n"
        return StreamingHttpResponse(
            error_stream(),
            content_type='text/event-stream'
        )
    except Exception as e:
        def error_stream():
            yield f"data: {json.dumps({'error': f'认证失败: {str(e)}'})}\n\n"
        return StreamingHttpResponse(
            error_stream(),
            content_type='text/event-stream'
        )
    
    try:
        # 解析JSON数据
        data = json.loads(request.body)
        messages = data.get('messages', [])
        conversation_id = data.get('conversation_id')
        deep_thinking = data.get('deep_thinking', False)
        web_search = data.get('web_search', False)
        
        if not messages:
            def error_stream():
                yield f"data: {json.dumps({'error': '消息不能为空'})}\n\n"
            return StreamingHttpResponse(
                error_stream(),
                content_type='text/event-stream'
            )
        
        # 获取最新的用户消息
        latest_message = messages[-1]
        if latest_message.get('role') != 'user':
            def error_stream():
                yield f"data: {json.dumps({'error': '最后一条消息必须是用户消息'})}\n\n"
            return StreamingHttpResponse(
                error_stream(),
                content_type='text/event-stream'
            )
        
        user_message = latest_message.get('content', '')
        
        def generate_stream():
            """生成流式响应"""
            try:
                # 获取或创建对话
                if conversation_id:
                    try:
                        conversation = Conversation.objects.get(
                            id=conversation_id, 
                            user=request.user
                        )
                    except Conversation.DoesNotExist:
                        yield f"data: {json.dumps({'error': '对话不存在'})}\n\n"
                        return
                else:
                    # 创建新对话
                    title = user_message[:50] if len(user_message) > 50 else user_message
                    conversation = Conversation.objects.create(
                        user=request.user,
                        title=title
                    )
                
                # 发送对话ID
                yield f"data: {json.dumps({'conversation_id': conversation.id, 'type': 'conversation_id'})}\n\n"
                
                # 调用AI Chat服务处理消息
                service = AIChatService()
                for chunk in service.process_message_stream(
                    conversation=conversation,
                    user_message=user_message,
                    user=request.user,
                    deep_thinking=deep_thinking,
                    web_search=web_search
                ):
                    yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"
                    
            except Exception as e:
                error_data = {
                    'type': 'error', 
                    'error': str(e),
                    'message': '处理消息时发生错误'
                }
                yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"
        
        # 返回流式响应
        response = StreamingHttpResponse(
            generate_stream(),
            content_type='text/event-stream'
        )
        response['Cache-Control'] = 'no-cache'
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Headers'] = 'Cache-Control, Authorization, Content-Type, Accept'
        
        return response
        
    except json.JSONDecodeError:
        def error_stream():
            yield f"data: {json.dumps({'error': '无效的JSON数据'})}\n\n"
        return StreamingHttpResponse(
            error_stream(),
            content_type='text/event-stream'
        )
    except Exception as e:
        def error_stream():
            yield f"data: {json.dumps({'error': f'服务器错误: {str(e)}'})}\n\n"
        return StreamingHttpResponse(
            error_stream(),
            content_type='text/event-stream'
        )


class ServerSentEventRenderer(BaseRenderer):
    """Server-Sent Events 渲染器"""
    media_type = 'text/event-stream'
    format = 'sse'
    charset = 'utf-8'

    def render(self, data, media_type=None, renderer_context=None):
        # 对于StreamingHttpResponse，直接返回原始数据
        return data


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
            recent_conversations = Conversation.objects.filter(user=user).order_by('-updated_at')[:5]
            
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
