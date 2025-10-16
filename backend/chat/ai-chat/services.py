from django.db import transaction
import time
import json
import logging
import os
import dashscope
from dashscope import Generation
from datetime import datetime
from typing import Dict, List, Any, Optional, Generator
from django.conf import settings

from chat.models import Conversation, Message
from chat.services import ChatService as BaseChatService
from chat.ai_service import AIService
from chat.deep_thinking_service import DeepThinkingService

# 配置日志 - 创建AI Chat专用的logger
logger = logging.getLogger('ai_chat')

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
    """API请求超时异常"""
    pass


class AIChatService(BaseChatService):
    """AI Chat 服务类，处理AI聊天相关的业务逻辑"""
    def __init__(self):
        super().__init__()
        self.ai_service = AIService()
        self.deep_thinking_service = DeepThinkingService()
        
        # 设置API密钥用于流式调用
        self.api_key = getattr(settings, 'DASHSCOPE_API_KEY', os.environ.get('DASHSCOPE_API_KEY', ''))
        if self.api_key:
            dashscope.api_key = self.api_key
        
    def _is_network_error(self, error_message):
        """检查是否为网络错误"""
        network_keywords = [
            'connection reset by peer', 
            'timed out', 
            'connection refused',
            'ssl: certificate_verify_failed',
            'name or service not known',
            'no route to host'
        ]
        return any(keyword in str(error_message).lower() for keyword in network_keywords)
    
    @transaction.atomic
    def process_message(self, conversation, user_message, user, deep_thinking=False, web_search=False):
        """处理用户消息并获取AI回复"""
        method_name = "process_message"
        logger.info(f"🚀 {method_name} 开始执行")
        logger.info(f"📋 输入参数: conversation_id={conversation.id}, user={user.username}, "
                   f"deep_thinking={deep_thinking}, web_search={web_search}")
        logger.info(f"📝 用户消息: {user_message}")
        
        try:
            start_time = time.time()
            
            # 保存用户消息
            logger.debug(f"💾 开始保存用户消息...")
            user_message_obj = self._save_user_message(conversation, user_message)
            logger.info(f"✅ 用户消息已保存, ID: {user_message_obj.id}")
            
            # 更新对话的更新时间
            logger.debug(f"⏰ 更新对话时间...")
            conversation.updated_at = datetime.now()
            conversation.save()
            
            # 准备消息历史
            logger.debug(f"📚 开始准备消息历史...")
            message_history = self._prepare_message_history(conversation)
            logger.info(f"📚 消息历史已准备完成，共 {len(message_history)} 条历史消息")
            logger.debug(f"📜 历史消息详情: {json.dumps(message_history, ensure_ascii=False, indent=2)}")
            
            # 根据功能开关选择模型和参数
            logger.debug(f"🔧 开始选择模型和参数...")
            model_name, api_params = self._select_model_and_params(
                message_history, 
                deep_thinking=deep_thinking, 
                web_search=web_search
            )
            logger.info(f"🤖 已选择模型: {model_name}")
            logger.info(f"⚙️ API参数: {json.dumps(api_params, ensure_ascii=False)}")
            
            # 如果启用了深度思考，先进行深度思考
            thinking_process = ""
            if deep_thinking:
                logger.info(f"🤔 深度思考模式已启用，开始执行...")
                thinking_process = self._perform_deep_thinking(message_history, user_message)
                logger.debug(f"🧠 思考过程结果: {thinking_process}")
                
                # 保存思考过程
                if thinking_process:
                    logger.debug(f"💾 保存思考过程...")
                    self._save_thinking_process(conversation, thinking_process)
                    logger.info(f"✅ 思考过程已保存")
            
            # 获取AI回复
            logger.info(f"🤖 开始获取AI回复...")
            ai_response = self._get_ai_response(
                model_name, 
                api_params, 
                message_history, 
                user_message,
                deep_thinking=deep_thinking,
                web_search=web_search
            )
            logger.info(f"🎯 AI回复获取成功")
            logger.info(f"📄 AI回复内容: {ai_response}")
            logger.debug(f"📏 AI回复长度: {len(ai_response)} 字符")
            
            # 保存AI回复
            logger.debug(f"💾 开始保存AI回复...")
            ai_message_obj = self._save_ai_message(
                conversation, 
                ai_response, 
                thinking_process=thinking_process
            )
            logger.info(f"✅ AI回复已保存, ID: {ai_message_obj.id}, tokens: {ai_message_obj.tokens_used}")
            
            # 如果对话标题是默认的，尝试从用户消息中生成标题
            logger.debug(f"🏷️ 检查是否需要更新对话标题...")
            self._update_conversation_title_if_needed(conversation, user_message)
            
            # 记录处理时间
            processing_time = time.time() - start_time
            logger.info(f"⏱️ 消息处理完成，总耗时: {processing_time:.2f}秒")
            
            # 构造返回结果
            logger.debug(f"🔧 开始构造返回结果...")
            result = {
                'conversation_id': conversation.id,
                'user_message': {
                    'id': user_message_obj.id,
                    'content': user_message_obj.content,
                    'timestamp': user_message_obj.created_at.strftime('%Y-%m-%d %H:%M:%S')
                },
                'ai_message': {
                    'id': ai_message_obj.id,
                    'content': ai_message_obj.content,
                    'timestamp': ai_message_obj.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'tokens_used': ai_message_obj.tokens_used or 0,
                    'thinking_process': thinking_process  # 从参数中获取
                },
                'processing_time': round(processing_time, 2),
                'conversation_title': conversation.title
            }
            
            logger.info(f"🎉 {method_name} 执行成功完成")
            logger.debug(f"📊 返回结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
            return result
            
        except Exception as e:
            logger.error(f"❌ {method_name} 执行失败: {str(e)}")
            logger.error(f"🔍 错误详情: {type(e).__name__}: {str(e)}")
            
            # 如果是网络错误，尝试重试一次
            if self._is_network_error(e):
                logger.warning(f"🌐 检测到网络错误，尝试重试一次...")
                try:
                    time.sleep(1)  # 等待1秒后重试
                    logger.info(f"🔄 开始重试 {method_name}...")
                    return self.process_message(conversation, user_message, user, deep_thinking, web_search)
                except Exception as retry_error:
                    logger.error(f"🔄 重试失败: {str(retry_error)}")
            
            # 保存错误消息
            logger.debug(f"💾 保存错误消息到对话中...")
            error_message = f"处理消息时发生错误: {str(e)}"
            self._save_error_message(conversation, error_message)
            
            logger.error(f"💥 {method_name} 最终失败，抛出异常")
            raise
    
    def _prepare_message_history(self, conversation):
        """准备消息历史，用于上下文理解"""
        method_name = "_prepare_message_history"
        logger.debug(f"🔄 {method_name} 开始执行")
        
        messages = Message.objects.filter(conversation=conversation).order_by('created_at')
        total_messages = messages.count()
        logger.debug(f"📊 对话中共有 {total_messages} 条消息")
        
        history = []
        
        # 只保留最近的20条消息（10轮对话）以避免上下文过长
        recent_messages = messages[-20:] if total_messages > 20 else messages
        used_messages = len(recent_messages)
        
        if total_messages > 20:
            logger.debug(f"⚠️ 消息过多，只保留最近的 {used_messages} 条消息作为上下文")
        
        for i, message in enumerate(recent_messages):
            history.append({
                'role': message.role,
                'content': message.content
            })
            logger.debug(f"📝 消息 {i+1}: [{message.role}] {message.content[:50]}...")
        
        logger.debug(f"✅ {method_name} 完成，返回 {len(history)} 条历史消息")
        return history
    
    def _select_model_and_params(self, message_history, deep_thinking=False, web_search=False):
        """根据功能开关选择合适的模型和API参数"""
        method_name = "_select_model_and_params"
        logger.debug(f"🔄 {method_name} 开始执行")
        logger.debug(f"🎛️ 功能开关: deep_thinking={deep_thinking}, web_search={web_search}")
        
        # 默认使用通用模型
        model_name = "qwen-plus-latest"
        logger.debug(f"🤖 初始模型选择: {model_name}")
        
        # 构建基础参数
        api_params = {
            'temperature': 0.7,
            'max_tokens': 2000,
            'top_p': 0.95,
            'frequency_penalty': 0,
            'presence_penalty': 0
        }
        logger.debug(f"⚙️ 初始API参数: {json.dumps(api_params, ensure_ascii=False)}")
        
        # 如果启用了深度思考，使用更强大的模型
        if deep_thinking:
            model_name = "qwen3-max-preview"
            api_params['temperature'] = 0.8
            api_params['max_tokens'] = 4000
            logger.info(f"🧠 深度思考模式：切换到模型 {model_name}，调整参数")
            logger.debug(f"🧠 深度思考参数: temperature={api_params['temperature']}, max_tokens={api_params['max_tokens']}")
        
        # 如果启用了联网搜索，添加系统指令
        if web_search:
            logger.debug(f"🌐 联网搜索模式：添加系统指令")
            system_prompt = "你现在可以访问网络搜索功能。如果用户的问题需要最新的信息或具体的实时数据，请先进行网络搜索，然后结合搜索结果回答用户问题。"
            
            if message_history and message_history[0]['role'] == 'system':
                # 如果已有系统指令，追加联网搜索指令
                logger.debug(f"🔗 发现现有系统指令，追加联网搜索指令")
                message_history[0]['content'] += f"\n{system_prompt}"
            else:
                # 否则添加新的系统指令
                logger.debug(f"➕ 添加新的系统指令")
                message_history.insert(0, {'role': 'system', 'content': system_prompt})
            
            logger.debug(f"🌐 系统指令内容: {system_prompt}")
        
        logger.debug(f"✅ {method_name} 完成")
        logger.info(f"🎯 最终选择: 模型={model_name}")
        return model_name, api_params
    
    def _perform_deep_thinking(self, message_history, user_message):
        """执行深度思考过程"""
        try:
            logger.info("开始深度思考...")
            
            # 深度思考服务只提供提示词，实际思考在AI回复中处理
            thinking_prompt = self.deep_thinking_service.build_deep_thinking_prompt()
            logger.info("深度思考提示词构建完成")
            
            return ""  # 返回空字符串，实际思考过程在AI回复中
            
        except Exception as e:
            logger.error(f"深度思考过程出错: {str(e)}")
            return f"深度思考过程中发生错误: {str(e)}"
    
    def _get_ai_response(self, model_name, api_params, message_history, user_message, deep_thinking=False, web_search=False):
        """获取AI回复"""
        method_name = "_get_ai_response"
        logger.info(f"🚀 {method_name} 开始执行")
        logger.info(f"🤖 使用模型: {model_name}")
        logger.debug(f"⚙️ API参数: {json.dumps(api_params, ensure_ascii=False)}")
        
        try:
            # 构建完整的消息列表
            logger.debug(f"🔧 构建完整的消息列表...")
            messages = message_history.copy()
            messages.append({'role': 'user', 'content': user_message})
            
            logger.info(f"📤 准备发送 {len(messages)} 条消息到AI服务")
            logger.debug(f"📜 完整消息列表:")
            for i, msg in enumerate(messages):
                content_preview = msg['content'][:100] + '...' if len(msg['content']) > 100 else msg['content']
                logger.debug(f"  消息 {i+1}: [{msg['role']}] {content_preview}")
            
            # 记录调用开始时间
            api_start_time = time.time()
            logger.info(f"🔄 开始调用AI服务...")
            
            # 调用AI服务获取回复 - 使用实际的方法名
            ai_response = self.ai_service.generate_response(
                messages=messages,
                deep_thinking=deep_thinking,
                web_search=web_search
            )
            
            api_duration = time.time() - api_start_time
            logger.info(f"⏱️ AI服务调用完成，耗时: {api_duration:.2f}秒")
            
            if not ai_response:
                logger.error(f"❌ AI服务返回空回复")
                raise Exception("未能获取AI回复")
            
            # 详细记录AI回复信息
            logger.info(f"✅ AI回复获取成功")
            logger.info(f"📄 AI回复长度: {len(ai_response)} 字符")
            logger.info(f"📖 AI回复内容:")
            
            # 如果回复很长，分段显示
            if len(ai_response) > 500:
                logger.info(f"  开头: {ai_response[:200]}...")
                logger.info(f"  结尾: ...{ai_response[-200:]}")
                logger.debug(f"📄 完整AI回复内容: {ai_response}")
            else:
                logger.info(f"  完整内容: {ai_response}")
            
            logger.debug(f"✅ {method_name} 执行成功")
            return ai_response
            
        except Exception as e:
            api_duration = time.time() - api_start_time if 'api_start_time' in locals() else 0
            logger.error(f"❌ {method_name} 执行失败")
            logger.error(f"⏱️ 失败前耗时: {api_duration:.2f}秒")
            logger.error(f"🔍 错误类型: {type(e).__name__}")
            logger.error(f"🔍 错误详情: {str(e)}")
            
            # 记录更多错误上下文
            logger.error(f"🔍 错误上下文:")
            logger.error(f"  - 模型: {model_name}")
            logger.error(f"  - 深度思考: {deep_thinking}")
            logger.error(f"  - 联网搜索: {web_search}")
            logger.error(f"  - 消息数量: {len(messages) if 'messages' in locals() else '未知'}")
            
            raise
    
    @transaction.atomic
    def _save_user_message(self, conversation, content):
        """保存用户消息"""
        method_name = "_save_user_message"
        logger.debug(f"🔄 {method_name} 开始执行")
        logger.debug(f"📝 保存用户消息: 对话ID={conversation.id}, 内容长度={len(content)}")
        
        try:
            message = Message.objects.create(
                conversation=conversation,
                role='user',
                content=content
            )
            logger.info(f"✅ 用户消息保存成功: ID={message.id}")
            logger.debug(f"📋 消息详情: {content[:100]}{'...' if len(content) > 100 else ''}")
            return message
        except Exception as e:
            logger.error(f"❌ {method_name} 失败: {str(e)}")
            raise
    
    @transaction.atomic
    def _save_ai_message(self, conversation, content, thinking_process=""):
        """保存AI消息"""
        method_name = "_save_ai_message"
        logger.debug(f"🔄 {method_name} 开始执行")
        logger.debug(f"🤖 保存AI消息: 对话ID={conversation.id}, 内容长度={len(content)}")
        
        try:
            # 估算使用的令牌数（实际应用中应该从API响应中获取准确值）
            tokens_used = self._estimate_tokens_used(content)
            logger.debug(f"📊 估算Token使用量: {tokens_used}")
            
            # 如果启用了深度思考且AI回复包含结构化内容，解析思考过程
            final_content = content
            actual_thinking_process = thinking_process
            
            if thinking_process or ('<思考过程>' in content and '</思考过程>' in content):
                logger.debug(f"🧠 检测到思考过程，开始解析...")
                parsed_result = self.deep_thinking_service.parse_deep_thinking_response(content)
                final_content = parsed_result['final_answer']
                if parsed_result['thinking_process']:
                    actual_thinking_process = parsed_result['thinking_process']
                    logger.debug(f"✅ 思考过程解析成功，长度: {len(actual_thinking_process)}")
            
            # 保存AI消息（暂时将思考过程放在content中，因为模型没有thinking_process字段）
            if actual_thinking_process:
                logger.debug(f"📝 将思考过程合并到消息内容中")
                final_content = f"{final_content}\n\n[思考过程: {actual_thinking_process}]"
            
            logger.debug(f"💾 创建AI消息记录...")
            message = Message.objects.create(
                conversation=conversation,
                role='assistant',
                content=final_content,
                tokens_used=tokens_used
            )
            
            logger.info(f"✅ AI消息保存成功: ID={message.id}, tokens={tokens_used}")
            logger.debug(f"📄 最终内容长度: {len(final_content)}")
            if len(final_content) > 200:
                logger.debug(f"📄 内容预览: {final_content[:100]}...{final_content[-100:]}")
            else:
                logger.debug(f"📄 完整内容: {final_content}")
            
            return message
            
        except Exception as e:
            logger.error(f"❌ {method_name} 失败: {str(e)}")
            raise
    
    @transaction.atomic
    def _save_thinking_process(self, conversation, thinking_process):
        """保存思考过程"""
        # 由于Message模型没有thinking_process和is_thinking字段
        # 我们创建一个system类型的消息来记录思考过程
        if thinking_process:
            return Message.objects.create(
                conversation=conversation,
                role='system',
                content=f"[思考过程] {thinking_process}"
            )
        return None
    
    @transaction.atomic
    def _save_error_message(self, conversation, error_content):
        """保存错误消息"""
        return Message.objects.create(
            conversation=conversation,
            role='system',
            content=error_content
        )
    
    def _update_conversation_title_if_needed(self, conversation, user_message):
        """如果对话标题是默认的，尝试从用户消息中生成标题"""
        # 检查标题是否为默认值
        if conversation.title in ['新对话', 'New Conversation'] and user_message:
            try:
                # 从用户消息生成简短标题
                title = self._generate_conversation_title(user_message)
                
                # 更新对话标题
                conversation.title = title
                conversation.save()
                
            except Exception as e:
                logger.error(f"生成对话标题时出错: {str(e)}")
    
    def _generate_conversation_title(self, user_message):
        """从用户消息生成对话标题"""
        # 简单实现：截取用户消息的前30个字符作为标题
        # 实际应用中可以使用更复杂的方法，如调用AI模型生成标题
        title = user_message[:30].strip()
        if len(user_message) > 30:
            title += '...'
        return title
    
    def _estimate_tokens_used(self, text):
        """估算文本使用的令牌数"""
        # 这是一个简单的估算方法，实际应用中应该使用与模型匹配的令牌计数方法
        # 通常一个中文字符约等于2个令牌，一个英文单词约等于1-1.3个令牌
        # 这里使用一个简化的估算：每个字符0.5个令牌
        return max(1, int(len(text) * 0.5))
    
    @transaction.atomic
    def regenerate_response(self, conversation, user):
        """重新生成AI回复"""
        try:
            # 获取对话的所有消息
            messages = Message.objects.filter(conversation=conversation).order_by('created_at')
            
            if not messages:
                raise Exception("对话中没有消息")
            
            # 找到最后一条用户消息和AI消息
            last_user_message = None
            last_ai_message = None
            
            for message in reversed(messages):
                if message.role == 'assistant' and not last_ai_message:
                    last_ai_message = message
                elif message.role == 'user' and not last_user_message:
                    last_user_message = message
                    break
            
            if not last_user_message:
                raise Exception("找不到用户消息")
            
            # 删除最后一条AI消息及其之后的所有消息
            if last_ai_message:
                Message.objects.filter(
                    conversation=conversation,
                    created_at__gte=last_ai_message.created_at
                ).delete()
            
            # 重新处理用户消息
            return self.process_message(
                conversation=conversation,
                user_message=last_user_message.content,
                user=user,
                # 可以从原消息中获取深度思考和联网搜索的设置
                deep_thinking=False,  # 默认不开启
                web_search=False      # 默认不开启
            )
            
        except Exception as e:
            logger.error(f"重新生成回复时出错: {str(e)}")
            raise
    
    def get_conversation_stats(self, user):
        """获取用户的对话统计信息"""
        try:
            # 获取所有对话
            conversations = Conversation.objects.filter(user=user)
            
            # 计算统计数据
            stats = {
                'total_conversations': conversations.count(),
                'total_messages': Message.objects.filter(conversation__in=conversations).count(),
                'active_conversations': conversations.filter(
                    updated_at__gte=datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                ).count()
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"获取对话统计信息时出错: {str(e)}")
            raise
    
    def export_conversation_history(self, conversation):
        """导出对话历史"""
        try:
            # 获取对话的所有消息
            messages = Message.objects.filter(conversation=conversation).order_by('created_at')
            
            # 构建导出数据
            export_data = {
                'conversation_id': conversation.id,
                'conversation_title': conversation.title,
                'created_at': conversation.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': conversation.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
                'export_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'messages': []
            }
            
            # 添加消息数据
            for message in messages:
                export_data['messages'].append({
                    'id': message.id,
                    'role': message.role,
                    'content': message.content,
                    'timestamp': message.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'tokens_used': message.tokens_used or 0
                })
            
            # 转换为JSON字符串
            return json.dumps(export_data, ensure_ascii=False, indent=2)
            
        except Exception as e:
            logger.error(f"导出对话历史时出错: {str(e)}")
            raise

    def process_message_stream(self, conversation, user_message, user, deep_thinking=False, web_search=False) -> Generator[Dict[str, Any], None, None]:
        """流式处理用户消息并获取AI回复"""
        method_name = "process_message_stream"
        logger.info(f"🚀 {method_name} 开始流式执行")
        logger.info(f"📋 输入参数: conversation_id={conversation.id}, user={user.username}, "
                   f"deep_thinking={deep_thinking}, web_search={web_search}")
        logger.info(f"📝 用户消息: {user_message}")
        
        try:
            start_time = time.time()
            
            # 保存用户消息
            logger.debug(f"💾 开始保存用户消息...")
            user_message_obj = self._save_user_message(conversation, user_message)
            logger.info(f"✅ 用户消息已保存, ID: {user_message_obj.id}")
            
            # 构建消息历史
            messages = []
            conversation_messages = Message.objects.filter(
                conversation=conversation
            ).order_by('created_at')
            
            for msg in conversation_messages:
                messages.append({
                    'role': msg.role,
                    'content': msg.content
                })
            
            logger.info(f"📜 构建消息历史完成, 消息数量: {len(messages)}")
            
            # 选择模型
            model = self._select_model(deep_thinking, web_search)
            logger.info(f"🤖 选择AI模型: {model}")
            
            # 准备API参数
            api_params = {
                'api_key': self.api_key,
                'model': model,
                'messages': messages,
                'result_format': 'message',
                'stream': True,
                'incremental_output': True,
                'temperature': 0.8 if deep_thinking else 0.7,
                'max_tokens': 3000 if deep_thinking else 2000
            }
            
            # 如果启用深度思考，设置 enable_thinking
            if deep_thinking:
                api_params['enable_thinking'] = True
                logger.info(f"🤔 启用深度思考模式")
            else:
                api_params['enable_thinking'] = False
                logger.info(f"🚫 禁用深度思考模式")
            
            # 如果启用联网搜索
            if web_search:
                api_params['enable_search'] = True
                logger.info(f"🌐 启用联网搜索模式")
            
            logger.debug(f"📡 API调用参数: {api_params}")
            
            # 调用DashScope流式API
            logger.info(f"📞 开始调用DashScope流式API...")
            responses = Generation.call(**api_params)
            logger.info(f"✅ SDK调用成功，开始处理流式响应")
            
            # 处理流式响应
            full_response_content = ""
            thinking_content = ""
            is_thinking_phase = True
            chunk_count = 0
            total_tokens = 0
            
            for response in responses:
                chunk_count += 1
                
                if hasattr(response, 'status_code') and response.status_code != 200:
                    error_msg = f"API调用失败: {response.message}"
                    logger.error(f"❌ {error_msg}")
                    yield {
                        'type': 'error',
                        'error': error_msg
                    }
                    return
                
                # 获取响应输出
                if hasattr(response, 'output') and response.output:
                    choices = response.output.get('choices', [])
                    if choices and len(choices) > 0:
                        choice = choices[0]
                        message = choice.get('message', {})
                        content = message.get('content', '')
                        
                        if content:
                            # 检查是否从思考阶段转换到回答阶段
                            if is_thinking_phase and '<think>' not in content:
                                is_thinking_phase = False
                                logger.debug(f"🔄 从思考阶段转换到回答阶段")
                            
                            if is_thinking_phase:
                                # 思考阶段
                                thinking_content += content
                            else:
                                # 回答阶段
                                full_response_content += content
                                
                                # 发送内容片段
                                yield {
                                    'type': 'content',
                                    'content': content,
                                    'full_content': full_response_content
                                }
                        
                        # 处理token使用量
                        if hasattr(response, 'usage') and response.usage:
                            total_tokens = response.usage.get('total_tokens', 0)
            
            logger.info(f"🔄 流式响应完成 - 处理了 {chunk_count} 个数据块")
            logger.info(f"📄 AI完整回复: {full_response_content}")
            logger.debug(f"📏 AI回复长度: {len(full_response_content)} 字符")
            
            # 保存AI回复
            ai_message_obj = self._save_ai_message(
                conversation, 
                full_response_content, 
                thinking_content if deep_thinking else ""
            )
            logger.info(f"✅ AI回复已保存, ID: {ai_message_obj.id}")
            
            # 计算执行时间
            execution_time = time.time() - start_time
            logger.info(f"⏱️ {method_name} 总执行时间: {execution_time:.2f} 秒")
            
            # 发送最终结果（包含时间戳）
            yield {
                'type': 'final',
                'content': full_response_content,
                'thinking_process': thinking_content if deep_thinking else "",
                'usage': {
                    'total_tokens': ai_message_obj.tokens_used or total_tokens
                },
                'conversation_id': conversation.id,
                'message_id': ai_message_obj.id,
                'user_message_timestamp': user_message_obj.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'ai_message_timestamp': ai_message_obj.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            logger.info(f"🎉 {method_name} 流式执行成功完成")
            
        except Exception as e:
            logger.error(f"❌ {method_name} 流式执行失败: {str(e)}")
            logger.error(f"🔍 错误详情: {type(e).__name__}: {str(e)}")
            
            yield {
                'type': 'error',
                'error': str(e),
                'message': '处理消息时发生错误'
            }

    def _select_model(self, deep_thinking=False, web_search=False):
        """选择合适的AI模型"""
        if deep_thinking:
            return 'qwen-plus-latest'  # 深度思考使用更强大的模型
        elif web_search:
            return 'qwen-plus-latest'  # 联网搜索使用强化模型
        else:
            return 'qwen-flash'  # 普通对话使用快速模型