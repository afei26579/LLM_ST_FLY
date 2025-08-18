from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
import os
from django.conf import settings
from django.db import transaction
from django.utils.translation import gettext_lazy as _
import dashscope
from dashscope import Generation

from openai import OpenAI
from .models import Conversation, Message
from .serializers import (
    ConversationSerializer, ConversationListSerializer,
    MessageSerializer, MessageCreateSerializer
)
from .ai_service import AIService
from core.response import StandardResponse
from core.views import StandardModelViewSet

# 从环境变量或设置中获取DashScope API密钥
DASHSCOPE_API_KEY = getattr(settings, 'DASHSCOPE_API_KEY', os.environ.get('DASHSCOPE_API_KEY', ''))
BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
# 设置DashScope API密钥
if DASHSCOPE_API_KEY:
    dashscope.api_key = DASHSCOPE_API_KEY

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
            # 手动实现create逻辑，确保用户关联
            serializer = self.get_serializer(data=request.data)           
            serializer.is_valid(raise_exception=True)
                      
            # 直接在这里保存，确保用户关联
           
            instance = serializer.save(user=request.user)

            # 构建响应
            response_data = self.get_serializer(instance).data

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

    # def perform_create(self, serializer):
    #     # 创建对话时自动关联当前用户
    #     try:
            
    #         instance = serializer.save(user=self.request.user)      
    #     except Exception as e:
    #         raise
    
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
            print(f"清空对话消息: conversation_id={conversation.id}")
            count = conversation.messages.count()
            conversation.messages.all().delete()
            print(f"已删除 {count} 条消息")
            
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
                return StandardResponse.error(
                    message="消息不能为空",
                    code=400,
                    request_id=getattr(request, 'request_id', None)
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
                        return StandardResponse.error(
                            message=f'对话不存在 (ID: {conversation_id})',
                            code=404,
                            request_id=getattr(request, 'request_id', None)
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
                    return StandardResponse.error(
                        message=f'AI服务调用失败: {str(api_error)}',
                        code=500,
                        request_id=getattr(request, 'request_id', None)
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
    
    def call_dashscope_api(self, messages):
        """
        使用DashScope SDK调用API进行对话
        """
        print("准备调用DashScope API (使用SDK)")
        if not DASHSCOPE_API_KEY:
            print("错误: DashScope API密钥未配置")
            raise ValueError("DashScope API密钥未配置")
        
        # 转换消息格式以适应DashScope SDK
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
        
        try:
            # 使用SDK调用API
            print("使用DashScope SDK发送请求")

            response = Generation.call(
                model="qwen-plus-latest",  # 使用通义千问模型
                messages=formatted_messages,
                temperature=0.7,
                top_p=0.8,
                result_format='message',
                enable_search=True
            )
            
            print("SDK调用成功，解析响应")
            
            # 检查响应状态
            if response.status_code != 200:
                error_message = f"API调用失败: 状态码={response.status_code}, 消息={response.message}"
                print(error_message)
                raise Exception(error_message)
            
            # 提取并返回回复内容
            content = response.output.choices[0].message.content if response.output.choices else ""
            usage = {
                "input_tokens": response.usage.input_tokens if hasattr(response.usage, 'input_tokens') else 0,
                "output_tokens": response.usage.output_tokens if hasattr(response.usage, 'output_tokens') else 0,
                "total_tokens": response.usage.total_tokens if hasattr(response.usage, 'total_tokens') else 0
            }
            
            if not content:
                print("警告: API响应中没有找到内容")
            
            return {
                "content": content,
                "usage": usage
            }
        except Exception as e:
            print(f"SDK调用异常: {str(e)}")
            raise Exception(f"DashScope SDK调用失败: {str(e)}")
