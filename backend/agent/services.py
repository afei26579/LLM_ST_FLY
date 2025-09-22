"""
智能体业务逻辑服务
"""

import logging
import json
from typing import Optional, Dict, Any, List, Tuple
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from django.conf import settings
import openai

from .models import Agent, Conversation, Message, UserAgentStats, AgentType

User = get_user_model()
logger = logging.getLogger(__name__)


class AgentServiceError(Exception):
    """智能体服务异常"""
    pass


class AIAgentService:
    """AI智能体服务"""
    
    # 预定义的智能体配置
    AGENT_CONFIGS = {
        AgentType.TRAVEL_ASSISTANT: {
            'name': '旅游助手',
            'description': '专业的旅游规划助手，可以帮您制定旅行计划、推荐景点、安排行程、预订酒店等。',
            'avatar': '/static/images/agents/travel-assistant.png',
            'system_prompt': '''你是一个专业的旅游助手，具有丰富的旅游知识和经验。你的任务是：
1. 根据用户需求制定详细的旅行计划
2. 推荐合适的旅游景点、美食、住宿
3. 提供交通路线和时间安排建议
4. 分享旅游注意事项和实用攻略
5. 预估旅行费用和最佳旅行时间

请以友好、专业的语气回答，提供具体、实用的建议。回答要结构清晰，包含具体的时间、地点、价格等信息。''',
            'greeting_message': '您好！我是您的专属旅游助手🧳，很高兴为您服务！无论您想去哪里旅行，我都可以为您制定完美的行程计划。请告诉我您的目的地和需求吧！'
        },
        AgentType.POETRY_PAINTING: {
            'name': '诗词绘画',
            'description': '融合古典诗词与现代绘画的艺术创作助手，可以创作诗词、分析诗意、生成绘画提示词。',
            'avatar': '/static/images/agents/poetry-painting.png',
            'system_prompt': '''你是一个博学的诗词绘画创作助手，精通中国古典诗词和绘画艺术。你的能力包括：
1. 创作各种体裁的诗词（律诗、绝句、词、古体诗等）
2. 分析和鉴赏经典诗词的意境和技法
3. 根据诗意生成相应的绘画创作提示词
4. 解释诗词中的典故、意象和文化背景
5. 提供诗词创作的技巧和指导

请用优雅的语言回答，体现深厚的文学底蕴。在创作时要注意平仄、对仗、意境等要素。''',
            'greeting_message': '诗酒趁年华，挥毫落纸如云烟🎨 我是您的诗词绘画助手，可以与您一同探索诗词的韵律之美，创作充满意境的艺术作品。请告诉我您想要创作什么主题的诗词呢？'
        },
        AgentType.CUSTOMER_SERVICE: {
            'name': '客服助手',
            'description': '专业的客户服务助手，提供产品咨询、问题解答、投诉处理等全方位客服支持。',
            'avatar': '/static/images/agents/customer-service.png',
            'system_prompt': '''你是一个专业的客服助手，具备优秀的客户服务技能。你需要：
1. 耐心倾听客户问题，准确理解需求
2. 提供清晰、准确的产品信息和解决方案
3. 处理客户投诉时保持专业和同理心
4. 主动引导客户完成服务流程
5. 记录重要信息并及时跟进

请始终保持礼貌、专业的态度，用简洁明了的语言回答问题。遇到无法解决的问题时，要及时转接人工客服。''',
            'greeting_message': '您好！欢迎来到客服中心😊 我是您的专属客服助手，很高兴为您服务！无论您有任何问题或需要帮助，我都会尽力为您解决。请问有什么可以帮助您的吗？'
        }
    }
    
    @classmethod
    def initialize_agents(cls):
        """初始化预定义的智能体"""
        for agent_type, config in cls.AGENT_CONFIGS.items():
            agent, created = Agent.objects.get_or_create(
                type=agent_type,
                defaults=config
            )
            if created:
                logger.info(f"创建智能体: {agent.name}")
            else:
                # 更新已存在的智能体配置
                for key, value in config.items():
                    setattr(agent, key, value)
                agent.save()
                logger.info(f"更新智能体: {agent.name}")
    
    @classmethod
    def get_agent_by_type(cls, agent_type: str) -> Agent:
        """根据类型获取智能体"""
        try:
            return Agent.objects.get(type=agent_type, is_active=True)
        except Agent.DoesNotExist:
            # 如果不存在，尝试创建
            cls.initialize_agents()
            return Agent.objects.get(type=agent_type, is_active=True)
    
    @classmethod
    def get_or_create_user_stats(cls, user: User) -> UserAgentStats:
        """获取或创建用户统计"""
        stats, created = UserAgentStats.objects.get_or_create(user=user)
        if created:
            logger.info(f"创建用户智能体统计: {user.username}")
        return stats
    
    @classmethod
    @transaction.atomic
    def create_conversation(cls, user: User, agent_type: str, title: Optional[str] = None) -> Conversation:
        """创建新对话"""
        agent = cls.get_agent_by_type(agent_type)
        
        # 生成标题
        if not title:
            timestamp = timezone.now().strftime("%m月%d日 %H:%M")
            title = f"与{agent.name}的对话 - {timestamp}"
        
        # 创建对话
        conversation = Conversation.objects.create(
            user=user,
            agent=agent,
            title=title
        )
        
        # 发送欢迎消息
        cls._create_message(
            conversation=conversation,
            message_type=Message.MessageType.ASSISTANT,
            content=agent.greeting_message,
            tokens_used=0
        )
        
        # 更新统计
        stats = cls.get_or_create_user_stats(user)
        stats.update_stats(agent_type, new_conversation=True)
        
        logger.info(f"创建新对话: {conversation.id} - {user.username} - {agent.name}")
        return conversation
    
    @classmethod
    def get_conversation(cls, conversation_id: str, user: User) -> Conversation:
        """获取对话"""
        try:
            return Conversation.objects.get(
                id=conversation_id,
                user=user,
                is_active=True
            )
        except Conversation.DoesNotExist:
            raise AgentServiceError(f"对话不存在或无权限访问: {conversation_id}")
    
    @classmethod
    def get_user_conversations(cls, user: User, agent_type: Optional[str] = None, 
                              limit: int = 20, offset: int = 0) -> List[Conversation]:
        """获取用户对话列表"""
        queryset = Conversation.objects.filter(user=user, is_active=True)
        
        if agent_type:
            queryset = queryset.filter(agent__type=agent_type)
        
        return list(queryset[offset:offset + limit])
    
    @classmethod
    def _create_message(cls, conversation: Conversation, message_type: str, 
                       content: str, tokens_used: int = 0, metadata: Optional[Dict] = None) -> Message:
        """创建消息"""
        message = Message.objects.create(
            conversation=conversation,
            type=message_type,
            content=content,
            tokens_used=tokens_used,
            metadata=metadata or {}
        )
        
        # 更新对话信息
        conversation.message_count += 1
        conversation.last_message_at = timezone.now()
        conversation.save(update_fields=['message_count', 'last_message_at'])
        
        return message
    
    @classmethod
    def _call_openai_api(cls, messages: List[Dict[str, str]], agent: Agent) -> Tuple[str, int]:
        """调用OpenAI API"""
        try:
            # 构建消息列表
            api_messages = [
                {"role": "system", "content": agent.system_prompt}
            ]
            api_messages.extend(messages)
            
            client = openai.OpenAI(
                api_key=settings.OPENAI_API_KEY,
                base_url=getattr(settings, 'OPENAI_BASE_URL', None)
            )
            
            response = client.chat.completions.create(
                model=getattr(settings, 'OPENAI_MODEL', 'gpt-3.5-turbo'),
                messages=api_messages,
                max_tokens=1000,
                temperature=0.7,
                stream=False
            )
            
            reply = response.choices[0].message.content
            tokens_used = response.usage.total_tokens
            
            return reply, tokens_used
            
        except Exception as e:
            logger.error(f"OpenAI API调用失败: {str(e)}")
            raise AgentServiceError(f"AI服务暂时不可用，请稍后重试")
    
    @classmethod
    @transaction.atomic
    def chat(cls, user: User, message_content: str, agent_type: str, 
             conversation_id: Optional[str] = None) -> Dict[str, Any]:
        """处理聊天请求"""
        
        # 获取或创建对话
        if conversation_id:
            conversation = cls.get_conversation(conversation_id, user)
            is_new_conversation = False
        else:
            conversation = cls.create_conversation(user, agent_type)
            is_new_conversation = True
        
        agent = conversation.agent
        
        # 保存用户消息
        user_message = cls._create_message(
            conversation=conversation,
            message_type=Message.MessageType.USER,
            content=message_content
        )
        
        try:
            # 获取对话历史（最近10条消息）
            recent_messages = list(
                conversation.messages.filter(
                    type__in=[Message.MessageType.USER, Message.MessageType.ASSISTANT]
                ).order_by('-created_at')[:10]
            )
            recent_messages.reverse()  # 按时间正序
            
            # 构建API消息格式
            api_messages = []
            for msg in recent_messages[:-1]:  # 排除刚添加的用户消息
                role = "user" if msg.type == Message.MessageType.USER else "assistant"
                api_messages.append({"role": role, "content": msg.content})
            
            # 添加当前用户消息
            api_messages.append({"role": "user", "content": message_content})
            
            # 调用AI服务
            reply, tokens_used = cls._call_openai_api(api_messages, agent)
            
            # 保存AI回复
            assistant_message = cls._create_message(
                conversation=conversation,
                message_type=Message.MessageType.ASSISTANT,
                content=reply,
                tokens_used=tokens_used
            )
            
            # 更新用户统计
            stats = cls.get_or_create_user_stats(user)
            stats.update_stats(agent_type, new_conversation=False, tokens=tokens_used)
            
            logger.info(f"聊天完成: {conversation.id} - tokens: {tokens_used}")
            
            return {
                'conversation_id': str(conversation.id),
                'message': reply,
                'message_id': str(assistant_message.id),
                'agent': agent,
                'tokens_used': tokens_used,
                'is_new_conversation': is_new_conversation
            }
            
        except Exception as e:
            logger.error(f"聊天处理失败: {str(e)}")
            # 回滚用户消息
            user_message.delete()
            raise AgentServiceError(str(e))


# 创建服务实例
ai_agent_service = AIAgentService()
