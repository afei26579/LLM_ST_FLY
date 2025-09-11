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
            return 'qwen-plus'  # 深度思考使用plus模型
        elif web_search:
            return 'qwen-plus'  # 联网搜索使用plus模型
        else:
            return 'qwen-turbo'  # 普通模式使用turbo模型
    
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
    
    def call_dashscope_api(self, messages: List[Dict], deep_thinking: bool = False, web_search: bool = False) -> Dict[str, Any]:
        """
        使用DashScope SDK调用API进行对话（非流式）
        
        Args:
            messages: 对话历史消息列表
            deep_thinking: 是否启用深度思考模式
            web_search: 是否启用联网搜索模式
            
        Returns:
            Dict: API响应结果
        """
        print("准备调用DashScope API (使用SDK)")
        if not self.api_key:
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
            # 设置超时时间：深度思考模式20秒，普通模式10秒
            timeout_seconds = 20 if deep_thinking else 10
            
            # 构建API调用参数
            api_params = self.build_api_params(formatted_messages, deep_thinking, web_search)
            
            print(f"API调用超时设置: {timeout_seconds}秒 (深度思考: {deep_thinking})")

            # 使用线程和超时控制来调用API
            completion = None
            exception_occurred = None
            
            def api_call():
                nonlocal completion, exception_occurred
                try:
                    completion = Generation.call(**api_params)
                except Exception as e:
                    exception_occurred = e
            
            # 启动API调用线程
            api_thread = threading.Thread(target=api_call)
            api_thread.daemon = True
            api_thread.start()
            
            # 等待线程完成或超时
            api_thread.join(timeout=timeout_seconds)
            
            if api_thread.is_alive():
                # 超时了
                raise APITimeoutError(f"API调用超时（{timeout_seconds}秒）")
            
            if exception_occurred:
                raise exception_occurred
                
            if completion is None:
                raise Exception("API调用失败，未获得响应")
            
            print("SDK调用成功，开始处理流式响应")
            
            # 定义完整思考过程和回复
            reasoning_content = ""
            answer_content = ""
            is_answering = False
            start_time = time.time()
            
            # 处理流式响应（也需要超时控制）
            for chunk in completion:
                # 检查处理时间是否超时
                if time.time() - start_time > timeout_seconds:
                    raise APITimeoutError(f"流式响应处理超时（{timeout_seconds}秒）")
                
                # 如果思考过程与回复皆为空，则忽略
                if (hasattr(chunk.output.choices[0].message, 'content') and 
                    hasattr(chunk.output.choices[0].message, 'reasoning_content') and
                    chunk.output.choices[0].message.content == "" and
                    chunk.output.choices[0].message.reasoning_content == ""):
                    continue
                
                # 如果当前为思考过程
                if (hasattr(chunk.output.choices[0].message, 'reasoning_content') and
                    chunk.output.choices[0].message.reasoning_content != "" and
                    chunk.output.choices[0].message.content == ""):
                    reasoning_content += chunk.output.choices[0].message.reasoning_content
                    print(f"思考过程片段: {chunk.output.choices[0].message.reasoning_content}")
                
                # 如果当前为回复
                elif (hasattr(chunk.output.choices[0].message, 'content') and
                      chunk.output.choices[0].message.content != ""):
                    if not is_answering:
                        print("开始接收最终回答")
                        is_answering = True
                    answer_content += chunk.output.choices[0].message.content
                    print(f"回答片段: {chunk.output.choices[0].message.content}")
            
            # 构建使用统计（流式响应可能没有详细的usage信息）
            usage = {
                "input_tokens": 0,
                "output_tokens": 0,
                "total_tokens": 0
            }
            
            # 构建返回结果
            result = {
                "content": answer_content if answer_content else reasoning_content,
                "usage": usage
            }
            
            # 如果启用了深度思考且有思考过程，添加相关字段
            if deep_thinking and reasoning_content:
                result.update({
                    "thinking_process": reasoning_content,
                    "final_answer": answer_content,
                    "has_structured_response": True
                })
                print(f"深度思考完成 - 思考过程长度: {len(reasoning_content)}, 最终回答长度: {len(answer_content)}")
            
            return result
            
        except APITimeoutError as e:
            error_message = str(e)
            print(f"API调用超时: {error_message}")
            if deep_thinking:
                error_message += "，深度思考模式需要更多时间处理，请稍后重试"
            raise Exception(error_message)
        except Exception as e:
            error_message = str(e)
            print(f"SDK调用异常: {error_message}")
            
            # 检查是否为其他类型的超时异常
            if "timeout" in error_message.lower() or "timed out" in error_message.lower():
                timeout_msg = f"请求超时（超时时间: {timeout_seconds}秒）"
                if deep_thinking:
                    timeout_msg += "，深度思考模式需要更多时间处理，请稍后重试"
                raise Exception(timeout_msg)
            else:
                raise Exception(f"DashScope SDK调用失败: {error_message}")
    
    def call_dashscope_api_stream(self, messages: List[Dict], deep_thinking: bool = False, web_search: bool = False) -> Generator[Dict[str, Any], None, None]:
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
            
            print(f"API调用超时设置: {timeout_seconds}秒 (深度思考: {deep_thinking})")
            
            # 调用DashScope流式API
            responses = Generation.call(**api_params)
            
            # 处理流式响应
            reasoning_content = ""
            answer_content = ""
            is_answering = False
            chunk_count = 0
            start_time = time.time()
            
            print("SDK调用成功，开始处理流式响应")
            
            response_completed = False
            
            for resp in responses:
                try:
                    # 检查超时
                    if time.time() - start_time > timeout_seconds:
                        error_msg = f"流式响应处理超时（{timeout_seconds}秒）"
                        if deep_thinking:
                            error_msg += "，深度思考模式需要更多时间处理，请稍后重试"
                        print(f"API调用超时: {error_msg}")
                        yield {
                            'type': 'error',
                            'message': error_msg
                        }
                        return
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
                    
                    # 只在深度思考模式下才处理思考过程
                    if deep_thinking:
                        try:
                            if hasattr(message, 'reasoning_content'):
                                reasoning_text = message.reasoning_content
                                if reasoning_text:
                                    reasoning_content += reasoning_text
                                    yield {
                                        'type': 'thinking',
                                        'content': reasoning_text,
                                        'full_thinking': reasoning_content
                                    }
                        except Exception as reasoning_error:
                            print(f"处理思考过程时出错: {str(reasoning_error)}")
                    
                    # 处理回答内容 - 实现服务器端打字机效果
                    try:
                        if hasattr(message, 'content') and message.content:
                            content_text = message.content
                            if not is_answering:
                                is_answering = True
                                print("开始输出回答内容")
                            
                            # 计算新增的内容
                            new_content = content_text[len(answer_content):]
                            if new_content:
                                # 逐字符发送，实现打字机效果
                                for char in new_content:
                                    answer_content += char
                                    yield {
                                        'type': 'content',
                                        'content': char,  # 发送单个字符
                                        'full_content': answer_content
                                    }
                                    # 添加延迟以控制打字速度
                                    time.sleep(0.03)  # 30ms延迟，可调整打字速度
                    except Exception as content_error:
                        print(f"处理回答内容时出错: {str(content_error)}")
                    
                    # 安全地检查是否完成
                    finish_reason = getattr(choice, 'finish_reason', None)
                    if finish_reason == 'stop':
                        print(f"流式响应完成 - 处理了 {chunk_count} 个数据块")
                        response_completed = True
                        
                        # 返回最终结果和使用统计
                        final_data = {
                            'type': 'final',
                            'content': answer_content,
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
                    print(f"处理响应块时出错: {str(chunk_error)}")
                    print(f"错误详情: {traceback.format_exc()}")
                    # 继续处理下一个块，不中断整个流程
                    continue
                    
            # 只有在响应没有正常完成时才检查错误情况
            if not response_completed:
                if not answer_content and not reasoning_content:
                    print("警告: 没有收集到任何响应内容")
                    yield {
                        'type': 'error',
                        'message': '没有收到有效的AI响应'
                    }
                else:
                    print("警告: 响应异常结束，但收集到了部分内容")
                    
        except Exception as e:
            import traceback
            error_message = f"流式API调用异常: {str(e)}"
            print(error_message)
            print(f"详细错误信息: {traceback.format_exc()}")
            yield {
                'type': 'error',
                'message': error_message
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