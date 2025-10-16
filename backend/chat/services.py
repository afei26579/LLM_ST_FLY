"""
聊天服务模块
包含聊天相关的业务逻辑
"""
import os
import time
import threading
import logging
import json
from typing import Dict, List, Any, Optional
import dashscope
from django.conf import settings
from django.db import transaction
from .models import Conversation, Message

# 配置详细日志 - 创建Chat专用的logger
logger = logging.getLogger('chat_service')

# 如果还没有配置handler，则添加一个
if not logger.handlers:
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    
    # 创建格式器
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s [%(name)s:%(lineno)d] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    
    # 添加处理器到logger
    logger.addHandler(console_handler)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False  # 防止重复输出


class APITimeoutError(Exception):
    """API调用超时异常"""
    pass


def is_network_error(error_message: str) -> bool:
    """
    检测是否为网络连接错误
    
    Args:
        error_message: 错误消息字符串
        
    Returns:
        bool: 如果是网络连接错误返回True
    """
    network_error_keywords = [
        'SSLError',
        'SSLEOFError', 
        'EOF occurred in violation of protocol',
        'Max retries exceeded',
        'Connection refused',
        'Connection timeout',
        'Connection aborted',
        'Network is unreachable',
        'Name or service not known',
        'Temporary failure in name resolution',
        'HTTPSConnectionPool',
        'ConnectionError',
        'ConnectTimeout',
        'ReadTimeout',
        'timeout',
        'timed out',
        'connection reset',
        'connection closed',
        'unable to connect',
        'network error',
        'dns resolution failed'
    ]
    
    error_lower = error_message.lower()
    return any(keyword.lower() in error_lower for keyword in network_error_keywords)


class ChatService:
    """聊天服务类"""
    
    def __init__(self):
        # 从环境变量或设置中获取DashScope API密钥
        self.api_key = getattr(settings, 'DASHSCOPE_API_KEY', os.environ.get('DASHSCOPE_API_KEY', ''))
        if self.api_key:
            dashscope.api_key = self.api_key
    
    def get_or_create_conversation(self, user, conversation_id: Optional[int] = None, messages: List[Dict] = None) -> Conversation:
        """
        获取或创建对话
        
        Args:
            user: 用户对象
            conversation_id: 对话ID（可选）
            messages: 消息列表，用于生成新对话标题
            
        Returns:
            Conversation: 对话对象
        """
        if conversation_id:
            try:
                conversation = Conversation.objects.get(id=conversation_id, user=user)
                print(f"找到现有对话: id={conversation.id}, title={conversation.title}")
                return conversation
            except Conversation.DoesNotExist:
                raise ValueError(f'对话不存在 (ID: {conversation_id})')
        else:
            # 创建新对话，使用第一条用户消息作为标题
            user_message = next((m for m in messages if m.get('role') == 'user'), None) if messages else None
            title = user_message.get('content', '新对话') if user_message else '新对话'
            
            # 如果有用户消息，同时设置为custom_title（截取前50个字符）
            custom_title = None
            if user_message and title != '新对话':
                # 截取前50个字符作为自定义标题
                custom_title = title[:50]
                if len(title) > 50:
                    custom_title += '...'
            
            conversation = Conversation.objects.create(
                user=user,
                title=title,
                custom_title=custom_title
            )
            print(f"创建新对话: id={conversation.id}, title={conversation.title}, custom_title={conversation.custom_title}")
            return conversation
    
    def save_user_message(self, conversation: Conversation, content: str) -> Message:
        """
        保存用户消息到数据库
        
        Args:
            conversation: 对话对象
            content: 消息内容
            
        Returns:
            Message: 消息对象
        """
        message = Message.objects.create(
            conversation=conversation,
            role='user',
            content=content
        )
        print(f"保存用户消息: id={message.id}, content={content[:50]}...")
        return message
    
    def save_ai_message(self, conversation: Conversation, content: str, tokens_used: int = 0) -> Message:
        """
        保存AI回复到数据库
        
        Args:
            conversation: 对话对象
            content: AI回复内容
            tokens_used: 使用的token数量
            
        Returns:
            Message: 消息对象
        """
        message = Message.objects.create(
            conversation=conversation,
            role='assistant',
            content=content,
            tokens_used=tokens_used
        )
        print(f"保存AI回复到数据库: id={message.id}, tokens={tokens_used}, content_length={len(content)}")
        return message
    
    def update_conversation_title(self, conversation: Conversation, messages: List[Dict]):
        """
        更新对话标题（如果是新对话）
        
        Args:
            conversation: 对话对象
            messages: 消息列表
        """
        if conversation.title == '新对话':
            user_message = next((m for m in messages if m.get('role') == 'user'), None)
            if user_message:
                title = user_message.get('content', '新对话')[:50]
                conversation.title = title
                conversation.save(update_fields=['title'])
                print(f"更新对话标题: {title}")
    
    def select_model(self, deep_thinking: bool = False, web_search: bool = False) -> str:
        """
        根据功能模式选择合适的模型
        
        Args:
            deep_thinking: 是否启用深度思考
            web_search: 是否启用联网搜索
            
        Returns:
            str: 模型名称
        """
        if deep_thinking:
            return 'qwen3-max-preview'  # 深度思考使用plus模型
        elif web_search:
            return 'qwen-plus-latest'  # 联网搜索使用plus模型
        else:
            return 'qwen-flash'  # 普通模式使用turbo模型
    
    def build_api_params(self, messages: List[Dict], deep_thinking: bool = False, web_search: bool = False) -> Dict[str, Any]:
        """
        构建API调用参数
        
        Args:
            messages: 消息列表
            deep_thinking: 是否启用深度思考
            web_search: 是否启用联网搜索
            
        Returns:
            Dict: API调用参数
        """
        model = self.select_model(deep_thinking, web_search)
        
        # 如果启用联网搜索，修改消息以包含搜索指令
        processed_messages = messages.copy()
        if web_search:
            print("启用联网搜索模式")
            # 在系统消息中添加联网搜索指令
            search_instruction = {
                "role": "system",
                "content": "你现在可以访问互联网获取最新信息。当用户询问需要实时数据、最新新闻、当前事件或时效性信息时，请主动搜索相关信息并提供准确的答案。请在回答中明确标注信息来源和获取时间。"
            }
            
            # 检查是否已有系统消息
            has_system = any(msg.get('role') == 'system' for msg in processed_messages)
            if has_system:
                # 如果已有系统消息，在第一个系统消息后插入搜索指令
                for i, msg in enumerate(processed_messages):
                    if msg.get('role') == 'system':
                        processed_messages.insert(i + 1, search_instruction)
                        break
            else:
                # 如果没有系统消息，在开头插入
                processed_messages.insert(0, search_instruction)
        
        api_params = {
            'api_key': self.api_key,
            'model': model,
            'messages': processed_messages,
            'result_format': 'message',
            'stream': True,
            'incremental_output': True,
        }
        
        # 如果启用深度思考，添加相应参数
        if deep_thinking:
            api_params['enable_thinking'] = True
            print("启用深度思考模式")
        else:
            # 明确禁用思考模式
            api_params['enable_thinking'] = False
            print("禁用深度思考模式")
        
        # 尝试添加搜索参数（如果DashScope支持的话）
        if web_search:
            try:
                api_params['enable_search'] = True
                print("尝试启用DashScope原生搜索功能")
            except:
                print("使用系统消息方式实现联网搜索")
        
        return api_params
    

class ConversationService:
    """对话管理服务类"""
    
    @staticmethod
    def get_user_conversations(user, limit: int = 10):
        """
        获取用户的对话列表
        
        Args:
            user: 用户对象
            limit: 返回数量限制
            
        Returns:
            QuerySet: 对话查询集
        """
        return Conversation.objects.filter(user=user).order_by('-updated_at')[:limit]
    
    @staticmethod
    def create_conversation(user, title: str = "新对话") -> Conversation:
        """
        创建新对话
        
        Args:
            user: 用户对象
            title: 对话标题
            
        Returns:
            Conversation: 新创建的对话对象
        """
        conversation = Conversation.objects.create(
            user=user,
            title=title
        )
        print(f"创建新对话: id={conversation.id}, title={conversation.title}")
        return conversation
    
    @staticmethod
    def clear_conversation_messages(conversation: Conversation) -> int:
        """
        清空对话中的所有消息
        
        Args:
            conversation: 对话对象
            
        Returns:
            int: 删除的消息数量
        """
        count = conversation.messages.count()
        conversation.messages.all().delete()
        print(f"清空对话消息: conversation_id={conversation.id}, 删除了 {count} 条消息")
        return count


class MessageService:
    """消息管理服务类"""
    
    @staticmethod
    def create_message(conversation: Conversation, role: str, content: str, tokens_used: int = 0) -> Message:
        """
        创建消息
        
        Args:
            conversation: 对话对象
            role: 角色（user/assistant/system）
            content: 消息内容
            tokens_used: 使用的token数量
            
        Returns:
            Message: 新创建的消息对象
        """
        message = Message.objects.create(
            conversation=conversation,
            role=role,
            content=content,
            tokens_used=tokens_used
        )
        print(f"创建消息: id={message.id}, role={role}, content_length={len(content)}")
        return message
    
    @staticmethod
    def get_conversation_messages(conversation: Conversation):
        """
        获取对话的所有消息
        
        Args:
            conversation: 对话对象
            
        Returns:
            QuerySet: 消息查询集
        """
        return conversation.messages.order_by('created_at')