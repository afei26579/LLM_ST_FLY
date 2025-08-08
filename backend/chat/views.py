from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
import requests
import json
import os
from django.conf import settings
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from .models import Conversation, Message
from .serializers import (
    ConversationSerializer, ConversationListSerializer,
    MessageSerializer, MessageCreateSerializer
)

# 从环境变量或设置中获取DashScope API密钥
DASHSCOPE_API_KEY = getattr(settings, 'DASHSCOPE_API_KEY', os.environ.get('DASHSCOPE_API_KEY', ''))

# 自定义API响应类
class ApiResponse:
    """
    标准化API响应格式
    """
    @staticmethod
    def success(data=None, message="Success", status_code=200):
        """
        成功响应
        """
        return Response({
            "code": status_code,
            "message": message,
            "data": data
        }, status=status_code)
    
    @staticmethod
    def error(message="Error", status_code=400, data=None):
        """
        错误响应
        """
        return Response({
            "code": status_code,
            "message": message,
            "data": data
        }, status=status_code)

class ConversationViewSet(viewsets.ModelViewSet):
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
    
    def perform_create(self, serializer):
        # 创建对话时自动关联当前用户
        try:
            print(f"创建新对话: {serializer.validated_data}")
            instance = serializer.save(user=self.request.user)
            print(f"对话创建成功: id={instance.id}, title={instance.title}")
        except Exception as e:
            print(f"创建对话失败: {str(e)}")
            raise
    
    def list(self, request, *args, **kwargs):
        try:
            print(f"获取用户 {request.user.username} 的对话列表")
            queryset = self.filter_queryset(self.get_queryset())
            print(f"找到 {queryset.count()} 个对话")
            
            # 如果需要分页
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                # 不使用分页器的响应格式，直接返回标准格式
                return ApiResponse.success(
                    serializer.data,
                    message="成功",
                    status_code=200
                )
            
            serializer = self.get_serializer(queryset, many=True)
            
            return ApiResponse.success(
                serializer.data,
                message="成功",
                status_code=200
            )
        except Exception as e:
            print(f"获取对话列表失败: {str(e)}")
            return ApiResponse.error(
                message=f'服务器错误: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            print(f"获取对话详情: id={instance.id}, title={instance.title}")
            serializer = self.get_serializer(instance)
            return ApiResponse.success(
                serializer.data,
                message="成功",
                status_code=200
            )
        except Exception as e:
            print(f"获取对话详情失败: {str(e)}")
            return ApiResponse.error(
                message=f'服务器错误: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def create(self, request, *args, **kwargs):
        try:
            print(f"创建对话请求: {request.data}")
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return ApiResponse.success(
                serializer.data,
                message="对话创建成功",
                status_code=status.HTTP_201_CREATED
            )
        except Exception as e:
            print(f"创建对话失败: {str(e)}")
            return ApiResponse.error(
                message=f'创建对话失败: {str(e)}',
                status_code=status.HTTP_400_BAD_REQUEST
            )
    
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            print(f"删除对话: id={instance.id}, title={instance.title}")
            self.perform_destroy(instance)
            return ApiResponse.success(
                None,
                message="对话删除成功",
                status_code=status.HTTP_200_OK
            )
        except Exception as e:
            print(f"删除对话失败: {str(e)}")
            return ApiResponse.error(
                message=f'删除对话失败: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
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
                print(f"消息数据有效: {serializer.validated_data}")
                instance = serializer.save()
                print(f"消息添加成功: id={instance.id}")
                return ApiResponse.success(
                    serializer.data,
                    message="消息添加成功",
                    status_code=200
                )
            else:
                print(f"消息数据无效: {serializer.errors}")
                return ApiResponse.error(
                    message="请求参数错误",
                    status_code=status.HTTP_400_BAD_REQUEST,
                    data=serializer.errors
                )
        except Exception as e:
            print(f"添加消息失败: {str(e)}")
            return ApiResponse.error(
                message=f'添加消息失败: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['delete'])
    def clear_messages(self, request, pk=None):
        """
        清空对话中的所有消息
        """
        try:
            conversation = self.get_object()
            print(f"清空对话消息: conversation_id={conversation.id}")
            count = conversation.messages.count()
            conversation.messages.all().delete()
            print(f"已删除 {count} 条消息")
            
            return ApiResponse.success(
                None,
                message=f'对话消息已清空，共删除 {count} 条消息',
                status_code=200
            )
        except Exception as e:
            print(f"清空消息失败: {str(e)}")
            return ApiResponse.error(
                message=f'清空消息失败: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ChatCompletionView(APIView):
    """
    使用阿里云DashScope大模型进行对话
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            # 获取用户输入的消息和历史消息
            messages = request.data.get('messages', [])
            conversation_id = request.data.get('conversation_id')
            
            print(f"收到聊天请求: messages={len(messages)}条, conversation_id={conversation_id}")
            
            if not messages:
                print("错误: 消息为空")
                return ApiResponse.error(
                    message="消息不能为空",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            # 处理对话
            with transaction.atomic():
                # 获取或创建对话
                conversation = None
                if conversation_id:
                    try:
                        conversation = Conversation.objects.get(id=conversation_id, user=request.user)
                        print(f"找到现有对话: id={conversation.id}, title={conversation.title}")
                    except Conversation.DoesNotExist:
                        print(f"错误: 对话不存在, id={conversation_id}")
                        return ApiResponse.error(
                            message=f'对话不存在 (ID: {conversation_id})',
                            status_code=status.HTTP_404_NOT_FOUND
                        )
                else:
                    # 创建新对话，使用第一条用户消息作为标题
                    user_message = next((m for m in messages if m.get('role') == 'user'), None)
                    title = user_message.get('content', '新对话')[:50] if user_message else '新对话'
                    conversation = Conversation.objects.create(
                        user=request.user,
                        title=title
                    )
                    print(f"创建新对话: id={conversation.id}, title={conversation.title}")
                
                # 保存当前消息到数据库
                latest_message = messages[-1]
                if latest_message.get('role') == 'user':
                    user_message = Message.objects.create(
                        conversation=conversation,
                        role=latest_message.get('role'),
                        content=latest_message.get('content')
                    )
                    print(f"保存用户消息: id={user_message.id}, content={user_message.content[:50]}...")
                
                # 调用DashScope API
                try:
                    print("调用DashScope API...")
                    api_response = self.call_dashscope_api(messages)
                    print(f"API调用成功, 响应长度: {len(api_response.get('content', ''))}")
                except Exception as api_error:
                    print(f"API调用失败: {str(api_error)}")
                    return ApiResponse.error(
                        message=f'AI服务调用失败: {str(api_error)}',
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
                
                # 保存AI回复到数据库
                if 'content' in api_response:
                    tokens = api_response.get('usage', {}).get('total_tokens', 0)
                    ai_message = Message.objects.create(
                        conversation=conversation,
                        role='assistant',
                        content=api_response['content'],
                        tokens_used=tokens
                    )
                    print(f"保存AI回复: id={ai_message.id}, tokens={tokens}")
                else:
                    print("警告: API响应中没有content字段")
                
                # 更新对话标题（如果是新对话）
                if conversation and conversation.title == '新对话':
                    user_message = next((m for m in messages if m.get('role') == 'user'), None)
                    if user_message:
                        title = user_message.get('content', '新对话')[:50]
                        conversation.title = title
                        conversation.save(update_fields=['title'])
                        print(f"更新对话标题: {title}")
                
                # 构建响应
                response_data = {
                    'content': api_response.get('content', ''),
                    'usage': api_response.get('usage', {}),
                    'conversation_id': conversation.id
                }
                
                print(f"请求处理成功, 返回响应: conversation_id={conversation.id}")
                return ApiResponse.success(
                    response_data,
                    message="成功",
                    status_code=200
                )
            
        except Exception as e:
            import traceback
            print(f"处理请求时出错: {str(e)}")
            print(traceback.format_exc())
            return ApiResponse.error(
                message=f'服务器错误: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def call_dashscope_api(self, messages):
        """
        调用DashScope API进行对话
        """
        if not DASHSCOPE_API_KEY:
            print("错误: DashScope API密钥未配置")
            raise ValueError("DashScope API密钥未配置")
        
        url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {DASHSCOPE_API_KEY}"
        }
        
        # 转换消息格式以适应DashScope API
        formatted_messages = []
        for msg in messages:
            role = msg.get('role')
            content = msg.get('content')
            
            # DashScope使用system/user/assistant角色
            if role in ['system', 'user', 'assistant']:
                formatted_messages.append({
                    "role": role,
                    "content": content
                })
        
        print(f"格式化后的消息数量: {len(formatted_messages)}")
        
        # 构建请求体
        payload = {
            "model": "qwen-max",  # 使用通义千问Max模型
            "input": {
                "messages": formatted_messages
            },
            "parameters": {
                "temperature": 0.7,
                "top_p": 0.8,
                "result_format": "message"
            }
        }
        
        try:
            # 发送请求
            print(f"发送请求到DashScope API: {url}")
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code != 200:
                error_message = f"API调用失败: 状态码={response.status_code}, 响应={response.text}"
                print(error_message)
                raise Exception(error_message)
            
            result = response.json()
            print("API调用成功，解析响应")
            
            # 提取并返回回复内容
            content = result.get("output", {}).get("choices", [{}])[0].get("message", {}).get("content", "")
            usage = result.get("usage", {})
            
            if not content:
                print("警告: API响应中没有找到内容")
            
            return {
                "content": content,
                "usage": usage
            }
        except requests.RequestException as e:
            print(f"请求异常: {str(e)}")
            raise Exception(f"网络请求失败: {str(e)}")
        except json.JSONDecodeError as e:
            print(f"JSON解析错误: {str(e)}")
            raise Exception(f"响应解析失败: {str(e)}") 