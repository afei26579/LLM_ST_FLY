from django.db import transaction
import time
import json
import logging
from datetime import datetime

from chat.models import Conversation, Message
from chat.services import ChatService as BaseChatService
from chat.ai_service import AIService
from chat.deep_thinking_service import DeepThinkingService

# 配置日志
logger = logging.getLogger(__name__)


class APITimeoutError(Exception):
    """API请求超时异常"""
    pass


class AIChatService(BaseChatService):
    """AI Chat 服务类，处理AI聊天相关的业务逻辑"""
    def __init__(self):
        super().__init__()
        self.ai_service = AIService()
        self.deep_thinking_service = DeepThinkingService()
        
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
        try:
            start_time = time.time()
            
            # 保存用户消息
            user_message_obj = self._save_user_message(conversation, user_message)
            
            # 更新对话的更新时间
            conversation.updated_at = datetime.now()
            conversation.save()
            
            # 准备消息历史
            message_history = self._prepare_message_history(conversation)
            
            # 根据功能开关选择模型和参数
            model_name, api_params = self._select_model_and_params(
                message_history, 
                deep_thinking=deep_thinking, 
                web_search=web_search
            )
            
            # 如果启用了深度思考，先进行深度思考
            thinking_process = ""
            if deep_thinking:
                thinking_process = self._perform_deep_thinking(message_history, user_message)
                
                # 保存思考过程
                if thinking_process:
                    self._save_thinking_process(conversation, thinking_process)
            
            # 获取AI回复
            ai_response = self._get_ai_response(
                model_name, 
                api_params, 
                message_history, 
                user_message
            )
            
            # 保存AI回复
            ai_message_obj = self._save_ai_message(
                conversation, 
                ai_response, 
                thinking_process=thinking_process
            )
            
            # 如果对话标题是默认的，尝试从用户消息中生成标题
            self._update_conversation_title_if_needed(conversation, user_message)
            
            # 记录处理时间
            processing_time = time.time() - start_time
            logger.info(f"处理消息完成，耗时: {processing_time:.2f}秒")
            
            # 构造返回结果
            result = {
                'conversation_id': conversation.id,
                'user_message': {
                    'id': user_message_obj.id,
                    'content': user_message_obj.content,
                    'timestamp': user_message_obj.timestamp.strftime('%Y-%m-%d %H:%M:%S')
                },
                'ai_message': {
                    'id': ai_message_obj.id,
                    'content': ai_message_obj.content,
                    'timestamp': ai_message_obj.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    'tokens_used': ai_message_obj.tokens_used,
                    'thinking_process': ai_message_obj.thinking_process
                },
                'processing_time': round(processing_time, 2),
                'conversation_title': conversation.title
            }
            
            return result
            
        except Exception as e:
            logger.error(f"处理消息时出错: {str(e)}")
            
            # 如果是网络错误，尝试重试一次
            if self._is_network_error(e):
                try:
                    logger.info("网络错误，尝试重试一次...")
                    time.sleep(1)  # 等待1秒后重试
                    return self.process_message(conversation, user_message, user, deep_thinking, web_search)
                except Exception as retry_error:
                    logger.error(f"重试失败: {str(retry_error)}")
            
            # 保存错误消息
            error_message = f"处理消息时发生错误: {str(e)}"
            self._save_error_message(conversation, error_message)
            
            raise
    
    def _prepare_message_history(self, conversation):
        """准备消息历史，用于上下文理解"""
        messages = Message.objects.filter(conversation=conversation).order_by('created_at')
        history = []
        
        # 只保留最近的20条消息（10轮对话）以避免上下文过长
        recent_messages = messages[-20:] if messages.count() > 20 else messages
        
        for message in recent_messages:
            history.append({
                'role': message.role,
                'content': message.content
            })
        
        return history
    
    def _select_model_and_params(self, message_history, deep_thinking=False, web_search=False):
        """根据功能开关选择合适的模型和API参数"""
        # 默认使用通用模型
        model_name = "qwen-plus-latest"
        
        # 构建基础参数
        api_params = {
            'temperature': 0.7,
            'max_tokens': 2000,
            'top_p': 0.95,
            'frequency_penalty': 0,
            'presence_penalty': 0
        }
        
        # 如果启用了深度思考，使用更强大的模型
        if deep_thinking:
            model_name = "qwen3-max-preview"
            api_params['temperature'] = 0.8
            api_params['max_tokens'] = 4000
        
        # 如果启用了联网搜索，添加系统指令
        if web_search:
            system_prompt = "你现在可以访问网络搜索功能。如果用户的问题需要最新的信息或具体的实时数据，请先进行网络搜索，然后结合搜索结果回答用户问题。"
            if message_history and message_history[0]['role'] == 'system':
                # 如果已有系统指令，追加联网搜索指令
                message_history[0]['content'] += f"\n{system_prompt}"
            else:
                # 否则添加新的系统指令
                message_history.insert(0, {'role': 'system', 'content': system_prompt})
        
        return model_name, api_params
    
    def _perform_deep_thinking(self, message_history, user_message):
        """执行深度思考过程"""
        try:
            logger.info("开始深度思考...")
            
            # 调用深度思考服务
            thinking_result = self.deep_thinking_service.think_deeply(
                message_history=message_history,
                user_message=user_message
            )
            
            logger.info("深度思考完成")
            return thinking_result.get('thinking_process', "")
            
        except Exception as e:
            logger.error(f"深度思考过程出错: {str(e)}")
            return f"深度思考过程中发生错误: {str(e)}"
    
    def _get_ai_response(self, model_name, api_params, message_history, user_message):
        """获取AI回复"""
        try:
            logger.info(f"调用AI模型: {model_name}")
            
            # 构建完整的消息列表
            messages = message_history.copy()
            messages.append({'role': 'user', 'content': user_message})
            
            # 调用AI服务获取回复
            response = self.ai_service.get_ai_response(
                model_name=model_name,
                messages=messages,
                **api_params
            )
            
            # 提取回复内容
            ai_response = response.get('choices', [{}])[0].get('message', {}).get('content', "")
            
            if not ai_response:
                raise Exception("未能获取AI回复")
            
            logger.info("AI回复获取成功")
            return ai_response
            
        except Exception as e:
            logger.error(f"获取AI回复时出错: {str(e)}")
            raise
    
    @transaction.atomic
    def _save_user_message(self, conversation, content):
        """保存用户消息"""
        return Message.objects.create(
            conversation=conversation,
            role='user',
            content=content
        )
    
    @transaction.atomic
    def _save_ai_message(self, conversation, content, thinking_process=""):
        """保存AI消息"""
        # 估算使用的令牌数（实际应用中应该从API响应中获取准确值）
        tokens_used = self._estimate_tokens_used(content)
        
        return Message.objects.create(
            conversation=conversation,
            role='assistant',
            content=content,
            tokens_used=tokens_used,
            thinking_process=thinking_process
        )
    
    @transaction.atomic
    def _save_thinking_process(self, conversation, thinking_process):
        """保存思考过程"""
        return Message.objects.create(
            conversation=conversation,
            role='assistant',
            content="",
            thinking_process=thinking_process,
            is_thinking=True
        )
    
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
                    'timestamp': message.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    'tokens_used': message.tokens_used,
                    'thinking_process': message.thinking_process
                })
            
            # 转换为JSON字符串
            return json.dumps(export_data, ensure_ascii=False, indent=2)
            
        except Exception as e:
            logger.error(f"导出对话历史时出错: {str(e)}")
            raise