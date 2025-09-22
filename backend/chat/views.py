from django.shortcuts import render, get_object_or_404
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django.http import StreamingHttpResponse, JsonResponse
import json
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
        queryset = Conversation.objects.filter(user=self.request.user).order_by('-updated_at')
        
        # 只有在列表查询时才限制为最近10条
        if self.action == 'list':
            return queryset[:10]
        
        # 其他操作（如retrieve详情查询）返回完整查询集
        return queryset
    
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


@method_decorator(csrf_exempt, name='dispatch')
class ChatCompletionView(View):
    """
    使用阿里云DashScope大模型进行对话
    支持流式和非流式响应
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.chat_service = ChatService()
    
    def dispatch(self, request, *args, **kwargs):
        # JWT token认证
        from rest_framework_simplejwt.authentication import JWTAuthentication
        from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
        
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return JsonResponse({'error': '未授权访问'}, status=401)
        
        try:
            # 使用JWT认证
            jwt_auth = JWTAuthentication()
            validated_token = jwt_auth.get_validated_token(auth_header.split(' ')[1])
            user = jwt_auth.get_user(validated_token)
            request.user = user
        except (InvalidToken, TokenError) as e:
            return JsonResponse({'error': '无效的认证令牌'}, status=401)
        except Exception as e:
            return JsonResponse({'error': f'认证失败: {str(e)}'}, status=401)
        
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request):
        try:
            # 解析JSON请求体
            data = json.loads(request.body)
            
            # 检查是否请求流式响应
            stream = data.get('stream', True)
            accept_header = request.headers.get('Accept', '')
            
            # 如果是流式请求，直接返回流式响应
            if stream or 'text/event-stream' in accept_header:
                return self.stream_response(request, data)
            else:
                return self.regular_response(request, data)
                
        except json.JSONDecodeError:
            return JsonResponse({'error': '无效的JSON数据'}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'服务器错误: {str(e)}'}, status=500)
    
    def regular_response(self, request, data):
        try:
            # 获取用户输入的消息和历史消息
            messages = data.get('messages', [])
            conversation_id = data.get('conversation_id')
            deep_thinking = data.get('deep_thinking', False)
            web_search = data.get('web_search', False)
            
            print(f"收到聊天请求: messages={len(messages)}条, conversation_id={conversation_id}, deep_thinking={deep_thinking}, web_search={web_search}")
            
            if not messages:
                print("错误: 消息为空")
                return StandardResponse.error(
                    message="消息不能为空",
                    code=400,
                    request_id=getattr(request, 'request_id', None)
                )
            
            # 处理对话
            with transaction.atomic():
                # 获取或创建对话
                try:
                    conversation = self.chat_service.get_or_create_conversation(
                        user=request.user,
                        conversation_id=conversation_id,
                        messages=messages
                    )
                except ValueError as e:
                    return StandardResponse.error(
                        message=str(e),
                        code=404,
                        request_id=getattr(request, 'request_id', None)
                    )
                
                # 保存当前用户消息到数据库
                latest_message = messages[-1]
                if latest_message.get('role') == 'user':
                    self.chat_service.save_user_message(
                        conversation=conversation,
                        content=latest_message.get('content')
                    )
                
                # 调用流式DashScope API并收集完整响应
                try:
                    print("调用流式DashScope API...")
                    full_content = ""
                    thinking_process = ""
                    usage_info = {}
                    
                    # 收集流式响应的完整内容
                    for chunk_data in self.chat_service.call_dashscope_api(messages, deep_thinking, web_search):
                        if chunk_data.get('type') == 'content':
                            full_content = chunk_data.get('full_content', '')
                        elif chunk_data.get('type') == 'thinking':
                            thinking_process = chunk_data.get('full_thinking', '')
                        elif chunk_data.get('type') == 'final':
                            full_content = chunk_data.get('content', '')
                            thinking_process = chunk_data.get('thinking_process', '')
                            usage_info = chunk_data.get('usage', {})
                        elif chunk_data.get('type') == 'error':
                            raise Exception(chunk_data.get('message', '未知错误'))
                    
                    print(f"流式API调用成功, 响应长度: {len(full_content)}")
                    
                    # 构建API响应格式
                    api_response = {
                        'content': full_content,
                        'usage': usage_info
                    }
                    
                    # 如果启用了深度思考且有思考过程，添加相关字段
                    if deep_thinking and thinking_process:
                        api_response.update({
                            'thinking_process': thinking_process,
                            'final_answer': full_content,
                            'has_structured_response': True
                        })
                        
                except Exception as api_error:
                    error_message = str(api_error)
                    print(f"流式API调用失败: {error_message}")
                    
                    # 直接返回异常消息，如果是网络错误，services.py已经处理为"网络连接超时"
                    return StandardResponse.error(
                        message=error_message,
                        code=500,
                        request_id=getattr(request, 'request_id', None)
                    )
                
                # 保存AI回复到数据库
                if 'content' in api_response and api_response['content']:
                    tokens = api_response.get('usage', {}).get('total_tokens', 0)
                    self.chat_service.save_ai_message(
                        conversation=conversation,
                        content=api_response['content'],
                        tokens_used=tokens
                    )
                else:
                    print("警告: API响应中没有content字段或内容为空")
                
                # 更新对话标题（如果是新对话）
                self.chat_service.update_conversation_title(conversation, messages)
                
                # 构建响应
                response_data = {
                    'content': api_response.get('content', ''),
                    'usage': api_response.get('usage', {}),
                    'conversation_id': conversation.id,
                    'deep_thinking': deep_thinking,
                    'web_search': web_search
                }
                
                # 如果启用了深度思考，添加思考过程相关字段
                if deep_thinking:
                    response_data.update({
                        'thinking_process': api_response.get('thinking_process', ''),
                        'final_answer': api_response.get('final_answer', api_response.get('content', '')),
                        'has_structured_response': api_response.get('has_structured_response', False)
                    })
                
                print(f"请求处理成功, 返回响应: conversation_id={conversation.id}")
                return StandardResponse.success(
                    data=response_data,
                    message="成功",
                    request_id=getattr(request, 'request_id', None)
                )
            
        except Exception as e:
            import traceback
            print(f"处理请求时出错: {str(e)}")
            print(traceback.format_exc())
            return StandardResponse.error(
                message=f'服务器错误: {str(e)}',
                code=500,
                request_id=getattr(request, 'request_id', None)
            )
    
    def stream_response(self, request, data):
        """处理流式响应请求"""
        try:
            # 获取用户输入的消息和历史消息
            messages = data.get('messages', [])
            conversation_id = data.get('conversation_id')
            deep_thinking = data.get('deep_thinking', False)
            web_search = data.get('web_search', False)
            
            print(f"收到流式聊天请求: messages={len(messages)}条, conversation_id={conversation_id}, deep_thinking={deep_thinking}, web_search={web_search}")
            
            if not messages:
                # 对于流式响应，直接返回错误的SSE格式
                def error_stream():
                    yield f"data: {json.dumps({'error': '消息不能为空'})}\n\n"
                
                response = StreamingHttpResponse(
                    error_stream(),
                    content_type='text/event-stream'
                )
                response['Cache-Control'] = 'no-cache'
                response['Access-Control-Allow-Origin'] = '*'
                response['Access-Control-Allow-Headers'] = 'Cache-Control'
                return response
            
            # 创建流式响应生成器
            def generate_stream():
                try:
                    # 处理对话
                    with transaction.atomic():
                        # 获取或创建对话
                        try:
                            conversation = self.chat_service.get_or_create_conversation(
                                user=request.user,
                                conversation_id=conversation_id,
                                messages=messages
                            )
                        except ValueError as e:
                            yield f"data: {json.dumps({'error': str(e)})}\n\n"
                            return
                        
                        # 保存当前用户消息到数据库
                        latest_message = messages[-1]
                        if latest_message.get('role') == 'user':
                            self.chat_service.save_user_message(
                                conversation=conversation,
                                content=latest_message.get('content')
                            )
                        
                        # 发送对话ID
                        yield f"data: {json.dumps({'conversation_id': conversation.id, 'type': 'conversation_id'})}\n\n"
                        
                        # 调用流式API并收集完整回复
                        full_content = ""
                        thinking_process = ""
                        usage_info = {}
                        
                        try:
                            for chunk_data in self.chat_service.call_dashscope_api(messages, deep_thinking, web_search):
                                # 发送流式数据给前端
                                yield f"data: {json.dumps(chunk_data)}\n\n"
                                
                                # 收集完整内容用于保存到数据库
                                if chunk_data.get('type') == 'content':
                                    full_content = chunk_data.get('full_content', '')
                                elif chunk_data.get('type') == 'thinking':
                                    thinking_process = chunk_data.get('full_thinking', '')
                                elif chunk_data.get('type') == 'final':
                                    full_content = chunk_data.get('content', '')
                                    thinking_process = chunk_data.get('thinking_process', '')
                                    usage_info = chunk_data.get('usage', {})
                                    
                        except Exception as api_error:
                            print(f"API调用失败: {str(api_error)}")
                            error_message = str(api_error)
                            # 直接返回异常消息，如果是网络错误，services.py已经处理为"网络连接超时"
                            yield f"data: {json.dumps({'error': error_message})}\n\n"
                            return
                        
                        # 保存AI回复到数据库
                        if full_content:
                            try:
                                tokens_used = usage_info.get('total_tokens', 0)
                                self.chat_service.save_ai_message(
                                    conversation=conversation,
                                    content=full_content,
                                    tokens_used=tokens_used
                                )
                                
                                # 如果有思考过程，也可以保存（可选）
                                if thinking_process and deep_thinking:
                                    print(f"思考过程长度: {len(thinking_process)}")
                                    
                            except Exception as save_error:
                                print(f"保存AI回复到数据库失败: {str(save_error)}")
                        else:
                            print("警告: 没有收集到完整的AI回复内容")
                        
                        # 发送完成信号
                        yield f"data: {json.dumps({'type': 'done'})}\n\n"
                        
                except Exception as e:
                    print(f"流式响应处理错误: {str(e)}")
                    yield f"data: {json.dumps({'error': f'服务器错误: {str(e)}'})}\n\n"
            
            # 返回流式响应
            response = StreamingHttpResponse(
                generate_stream(),
                content_type='text/event-stream'
            )
            response['Cache-Control'] = 'no-cache'
            response['Access-Control-Allow-Origin'] = '*'
            response['Access-Control-Allow-Headers'] = 'Cache-Control'
            
            return response
            
        except Exception as e:
            print(f"流式响应初始化错误: {str(e)}")
            # 对于流式响应，返回SSE格式的错误
            def error_stream():
                yield f"data: {json.dumps({'error': f'服务器错误: {str(e)}'})}\n\n"
            
            response = StreamingHttpResponse(
                error_stream(),
                content_type='text/event-stream'
            )
            response['Cache-Control'] = 'no-cache'
            response['Access-Control-Allow-Origin'] = '*'
            response['Access-Control-Allow-Headers'] = 'Cache-Control'
            return response