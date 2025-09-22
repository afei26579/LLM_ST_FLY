"""
聊天服务模块
包含聊天相关的业务逻辑
"""
import os
import time
import threading
from http import HTTPStatus
from typing import Dict, List, Any, Generator, Optional
import dashscope
from dashscope import Generation
from django.conf import settings
from django.db import transaction
from .models import Conversation, Message


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
            title = user_message.get('content', '新对话')[:50] if user_message else '新对话'
            conversation = Conversation.objects.create(
                user=user,
                title=title
            )
            print(f"创建新对话: id={conversation.id}, title={conversation.title}")
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
    
    def call_dashscope_api(self, messages: List[Dict], deep_thinking: bool = False, web_search: bool = False) -> Generator[Dict[str, Any], None, None]:
        """
        使用DashScope SDK进行流式API调用
        
        Args:
            messages: 对话历史消息列表
            deep_thinking: 是否启用深度思考
            web_search: 是否启用联网搜索
            
        Yields:
            Dict: 包含流式响应数据的字典
        """
        print("准备调用DashScope流式API...")
        
        try:
            # 设置超时时间：深度思考模式60秒，普通模式15秒
            timeout_seconds = 60 if deep_thinking else 15
            
            # 构建API调用参数
            api_params = self.build_api_params(messages, deep_thinking, web_search)
            print(f"API调用参数: {api_params}")
            print(f"API调用参数: 当前模型={api_params.get('model')},深度思考={api_params.get('enable_thinking')},联网搜索={api_params.get('enable_search')}")
            
            # 调用DashScope流式API
            responses = Generation.call(**api_params)
            
            # 处理流式响应 - 统一处理所有内容
            full_response_content = ""  # 完整的响应内容（包含思考过程和回答）
            reasoning_content = ""     # 仅用于记录思考过程
            is_thinking_phase = True   # 当前是否处于思考阶段
            chunk_count = 0
            start_time = time.time()
            
            print("SDK调用成功，开始处理流式响应")
            
            response_completed = False
            
            for resp in responses:
                try:
                    chunk_count += 1
                    
                    # 安全地检查响应状态
                    if not hasattr(resp, 'status_code') or resp.status_code != HTTPStatus.OK:
                        print(f"响应状态异常: {getattr(resp, 'status_code', 'unknown')}")
                        continue
                    
                    # 安全地访问响应数据
                    if not hasattr(resp, 'output') or not hasattr(resp.output, 'choices') or not resp.output.choices:
                        print("响应格式异常: 缺少output或choices")
                        continue
                    
                    choice = resp.output.choices[0]
                    if not hasattr(choice, 'message'):
                        print("响应格式异常: 缺少message")
                        continue
                    
                    message = choice.message
                    
                    # 获取思考内容和回答内容
                    reasoning_text = None
                    content_text = None
                    
                    # 获取思考内容（仅在深度思考模式下）
                    if deep_thinking:
                        try:
                            # 尝试多种方式获取思考内容
                            possible_keys = ['reasoning_content', 'reasoningContent', 'thinking', 'reasoning']
                            for key in possible_keys:
                                try:
                                    if hasattr(message, 'get'):
                                        reasoning_text = message.get(key, None)
                                    elif hasattr(message, '__getitem__'):
                                        try:
                                            reasoning_text = message[key]
                                        except KeyError:
                                            reasoning_text = None
                                    
                                    if reasoning_text and isinstance(reasoning_text, str) and reasoning_text.strip():
                                        break
                                except (KeyError, AttributeError, TypeError):
                                    continue
                        except Exception as e:
                            print(f"获取思考内容时出错: {str(e)}")
                    
                    # 获取回答内容
                    try:
                        if hasattr(message, 'get'):
                            content_text = message.get('content', None)
                        elif hasattr(message, '__getitem__'):
                            try:
                                content_text = message['content']
                            except KeyError:
                                content_text = None
                    except Exception as e:
                        print(f"获取回答内容时出错: {str(e)}")
                    
                    # 处理内容流
                    current_chunk_content = ""
                    
                    # 如果有思考内容且当前处于思考阶段
                    if reasoning_text and isinstance(reasoning_text, str) and reasoning_text.strip():
                        # 计算新增的思考内容
                        new_reasoning = reasoning_text[len(reasoning_content):]
                        if new_reasoning:
                            reasoning_content += new_reasoning
                            current_chunk_content = new_reasoning
                            print(f"思考内容片段: {len(new_reasoning)} 字符")
                    
                    # 如果有回答内容
                    if content_text and isinstance(content_text, str) and content_text.strip():
                        # 如果从思考阶段转换到回答阶段
                        if is_thinking_phase:
                            is_thinking_phase = False
                            print("从思考阶段转换到回答阶段")
                        
                        # 计算新增的回答内容
                        current_answer_length = len(full_response_content) - len(reasoning_content)
                        new_answer = content_text[current_answer_length:]
                        if new_answer:
                            current_chunk_content = new_answer
                            print(f"回答内容片段: {len(new_answer)} 字符")
                    
                    # 如果有新内容，添加到完整响应中并流式输出
                    if current_chunk_content:
                        full_response_content += current_chunk_content
                        
                        # 直接发送完整的新内容块，而不是逐字符输出
                        yield {
                            'type': 'content',
                            'content': current_chunk_content,
                            'full_content': full_response_content,
                            'is_thinking': is_thinking_phase,
                            'thinking_content': reasoning_content if deep_thinking else None
                        }
                    
                    # 安全地检查是否完成
                    finish_reason = getattr(choice, 'finish_reason', None)
                    if finish_reason == 'stop':
                        print(f"流式响应完成 - 处理了 {chunk_count} 个数据块")
                        response_completed = True
                        
                        # 返回最终结果和使用统计
                        final_data = {
                            'type': 'final',
                            'content': full_response_content,
                            'usage': {
                                'input_tokens': getattr(resp.usage, 'input_tokens', 0) if hasattr(resp, 'usage') else 0,
                                'output_tokens': getattr(resp.usage, 'output_tokens', 0) if hasattr(resp, 'usage') else 0,
                                'total_tokens': getattr(resp.usage, 'total_tokens', 0) if hasattr(resp, 'usage') else 0
                            },
                            'request_id': getattr(resp, 'request_id', '')
                        }
                        
                        # 如果有思考过程，添加到最终结果中
                        if reasoning_content:
                            final_data['thinking_process'] = reasoning_content
                            final_data['has_thinking'] = True
                        
                        yield final_data
                        return  # 成功完成，直接返回，不执行后续的错误检查
                        
                except Exception as chunk_error:
                    import traceback
                    chunk_error_message = str(chunk_error)
                    print(f"处理响应块时出错: {chunk_error_message}")
                    print(f"错误详情: {traceback.format_exc()}")
                    
                    # 检查是否为网络连接错误
                    if is_network_error(chunk_error_message):
                        print(f"检测到网络连接错误: {chunk_error_message}")
                        yield {
                            'type': 'error',
                            'message': '网络连接超时'
                        }
                        return
                    
                    # 继续处理下一个块，不中断整个流程
                    continue
                    
            # 只有在响应没有正常完成时才检查错误情况
            if not response_completed:
                if not full_response_content:
                    print("警告: 没有收集到任何响应内容")
                    yield {
                        'type': 'error',
                        'message': '没有收到有效的AI响应'
                    }
                else:
                    print("警告: 响应异常结束，但收集到了部分内容")
                    
        except Exception as e:
            import traceback
            error_message = str(e)
            print(f"流式API调用异常: {error_message}")
            print(f"详细错误信息: {traceback.format_exc()}")
            
            # 检查是否为网络连接错误
            if is_network_error(error_message):
                print(f"检测到网络连接错误: {error_message}")
                yield {
                    'type': 'error',
                    'message': '网络连接超时'
                }
            else:
                yield {
                    'type': 'error',
                    'message': f"流式API调用异常: {error_message}"
                }


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