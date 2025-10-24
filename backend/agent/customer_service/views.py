"""
客服系统视图
"""
import uuid
import logging
from datetime import datetime

from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.conf import settings

from core.response import StandardResponse
from .models import (
    CustomerServiceSession,
    CustomerServiceMessage,
    CustomerServiceKnowledgeBase,
    CustomerServiceStats
)
from .serializers import (
    CustomerServiceSessionSerializer,
    CustomerServiceSessionListSerializer,
    CustomerServiceMessageSerializer,
    ChatRequestSerializer,
    ChatResponseSerializer,
    CustomerServiceKnowledgeBaseSerializer,
    CustomerServiceStatsSerializer,
    SatisfactionFeedbackSerializer
)
from .langgraph_service import CustomerServiceGraph

logger = logging.getLogger(__name__)


class CustomerServiceSessionViewSet(viewsets.ModelViewSet):
    """客服会话视图集"""
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """只返回当前用户的会话"""
        return CustomerServiceSession.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        """根据动作选择序列化器"""
        if self.action == 'list':
            return CustomerServiceSessionListSerializer
        return CustomerServiceSessionSerializer
    
    def list(self, request):
        """获取会话列表"""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return StandardResponse.success(data=serializer.data, message="获取会话列表成功")
    
    def retrieve(self, request, pk=None):
        """获取会话详情（包含消息）"""
        try:
            session = self.get_queryset().get(pk=pk)
            serializer = CustomerServiceSessionSerializer(session)
            return StandardResponse.success(data=serializer.data)
        except CustomerServiceSession.DoesNotExist:
            return StandardResponse.error(message="会话不存在", code=404)
    
    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        """关闭会话"""
        try:
            session = self.get_queryset().get(pk=pk)
            session.status = 'closed'
            session.ended_at = timezone.now()
            session.save()
            
            return StandardResponse.success(message="会话已关闭")
        except CustomerServiceSession.DoesNotExist:
            return StandardResponse.error(message="会话不存在", code=404)
    
    @action(detail=False, methods=['delete'])
    def clear_history(self, request):
        """清空历史会话"""
        count = self.get_queryset().filter(status='closed').delete()[0]
        return StandardResponse.success(message=f"已清空 {count} 个历史会话")


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def customer_service_chat(request):
    """
    客服对话接口
    """
    # 验证请求数据
    serializer = ChatRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return StandardResponse.error(
            message="请求参数错误",
            code=400
        )
    
    user_message = serializer.validated_data['message']
    session_id = serializer.validated_data.get('session_id') or str(uuid.uuid4())
    assistant_id = serializer.validated_data.get('assistant_id')
    
    logger.info(f"收到客服消息: user={request.user.username}, session={session_id}, assistant={assistant_id}")
    
    try:
        # 获取助手信息（如果提供了assistant_id）
        assistant = None
        knowledge_bases = []
        
        if assistant_id:
            from .models_extended import CustomerServiceAssistant
            try:
                assistant = CustomerServiceAssistant.objects.prefetch_related('knowledge_bases').get(
                    id=assistant_id,
                    user=request.user
                )
                knowledge_bases = list(assistant.knowledge_bases.all())
                logger.info(f"使用助手: {assistant.name}, 关联知识库: {len(knowledge_bases)}")
            except CustomerServiceAssistant.DoesNotExist:
                logger.warning(f"助手不存在: {assistant_id}")
        
        # 获取或创建会话
        session, created = CustomerServiceSession.objects.get_or_create(
            session_id=session_id,
            defaults={
                'user': request.user,
                'title': user_message[:50] + '...' if len(user_message) > 50 else user_message,
                'status': 'active'
            }
        )
        
        # 如果会话不属于当前用户，返回错误
        if session.user != request.user:
            return StandardResponse.error(message="无权访问此会话", code=403)
        
        # 获取历史消息（用于上下文）
        history_messages = list(session.messages.order_by('created_at').values('role', 'content'))
        
        # 保存用户消息
        user_msg = CustomerServiceMessage.objects.create(
            session=session,
            role='user',
            content=user_message
        )
        
        # 初始化 LangGraph 服务（传递知识库信息）
        try:
            graph_service = CustomerServiceGraph(
                api_key=settings.DASHSCOPE_API_KEY,
                model=assistant.model if assistant else "qwen-plus",
                knowledge_bases=knowledge_bases
            )
            
            # 运行工作流
            result = graph_service.run(
                user_message=user_message,
                user_id=request.user.id,
                session_id=session_id,
                history=history_messages
            )
            
            if not result.get('success', False):
                raise Exception(result.get('error', '未知错误'))
            
        except Exception as e:
            logger.error(f"LangGraph 执行失败: {e}", exc_info=True)
            result = {
                'response': '抱歉，系统暂时无法处理您的请求。让我为您转接人工客服。',
                'intent': 'error',
                'entities': {},
                'need_human': True,
                'confidence': 0.0,
                'tools_result': {}
            }
        
        # 保存AI回复
        ai_msg = CustomerServiceMessage.objects.create(
            session=session,
            role='assistant',
            content=result['response'],
            intent=result.get('intent', ''),
            entities=result.get('entities', {}),
            confidence=result.get('confidence', 0.0),
            tools_result=result.get('tools_result', {})
        )
        
        # 更新会话信息
        session.message_count = session.messages.count()
        session.updated_at = timezone.now()
        
        # 如果需要转人工
        if result.get('need_human', False):
            session.status = 'transferred'
        
        session.save()
        
        # 更新用户统计
        _update_user_stats(request.user, session)
        
        # 返回响应
        response_data = {
            'response': result['response'],
            'session_id': session_id,
            'intent': result.get('intent', ''),
            'entities': result.get('entities', {}),
            'need_human': result.get('need_human', False),
            'confidence': result.get('confidence', 0.0),
            'message_id': ai_msg.id
        }
        
        return StandardResponse.success(data=response_data, message="消息发送成功")
        
    except Exception as e:
        logger.error(f"客服对话处理失败: {e}", exc_info=True)
        return StandardResponse.error(
            message=f"处理失败: {str(e)}",
            code=500
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_satisfaction(request):
    """
    提交满意度反馈
    """
    serializer = SatisfactionFeedbackSerializer(data=request.data)
    if not serializer.is_valid():
        return StandardResponse.error(message="参数错误", code=400)
    
    session_id = serializer.validated_data['session_id']
    score = serializer.validated_data['score']
    comment = serializer.validated_data.get('comment', '')
    
    try:
        session = CustomerServiceSession.objects.get(
            session_id=session_id,
            user=request.user
        )
        
        session.satisfaction_score = score
        session.status = 'resolved'
        session.ended_at = timezone.now()
        session.save()
        
        # 更新用户统计
        _update_user_stats(request.user, session)
        
        logger.info(f"满意度反馈: session={session_id}, score={score}")
        
        return StandardResponse.success(message="感谢您的反馈！")
        
    except CustomerServiceSession.DoesNotExist:
        return StandardResponse.error(message="会话不存在", code=404)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_stats(request):
    """
    获取用户客服统计信息
    """
    try:
        stats = CustomerServiceStats.objects.get(user=request.user)
        serializer = CustomerServiceStatsSerializer(stats)
        return StandardResponse.success(data=serializer.data)
    except CustomerServiceStats.DoesNotExist:
        # 返回空统计
        return StandardResponse.success(data={
            'user_name': request.user.username,
            'total_sessions': 0,
            'resolved_sessions': 0,
            'transferred_sessions': 0,
            'total_messages': 0,
            'avg_session_messages': 0.0,
            'avg_satisfaction_score': None,
            'last_session_at': None
        })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_greeting(request):
    """
    获取欢迎语
    """
    greeting_messages = [
        f"您好，{request.user.username}！我是智能客服助手，有什么可以帮您的吗？",
        "欢迎使用智能客服系统！请告诉我您遇到的问题。",
        "您好！我是您的专属客服助手，很高兴为您服务！",
    ]
    
    import random
    greeting = random.choice(greeting_messages)
    
    return StandardResponse.success(data={'greeting': greeting})


class CustomerServiceKnowledgeBaseViewSet(viewsets.ModelViewSet):
    """知识库管理视图集（管理员使用）"""
    queryset = CustomerServiceKnowledgeBase.objects.all()
    serializer_class = CustomerServiceKnowledgeBaseSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """支持筛选"""
        queryset = super().get_queryset()
        
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)
        
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset.order_by('-use_count', '-created_at')
    
    @action(detail=True, methods=['post'])
    def mark_helpful(self, request, pk=None):
        """标记为有用"""
        try:
            knowledge = self.get_object()
            knowledge.helpful_count += 1
            knowledge.save()
            return StandardResponse.success(message="已标记为有用")
        except CustomerServiceKnowledgeBase.DoesNotExist:
            return StandardResponse.error(message="知识条目不存在", code=404)


def _update_user_stats(user, session):
    """更新用户统计信息"""
    stats, created = CustomerServiceStats.objects.get_or_create(user=user)
    
    # 重新统计
    all_sessions = CustomerServiceSession.objects.filter(user=user)
    
    stats.total_sessions = all_sessions.count()
    stats.resolved_sessions = all_sessions.filter(status='resolved').count()
    stats.transferred_sessions = all_sessions.filter(status='transferred').count()
    stats.total_messages = CustomerServiceMessage.objects.filter(session__user=user).count()
    
    if stats.total_sessions > 0:
        stats.avg_session_messages = stats.total_messages / stats.total_sessions
    
    # 计算平均满意度
    sessions_with_score = all_sessions.exclude(satisfaction_score__isnull=True)
    if sessions_with_score.exists():
        from django.db.models import Avg
        avg_score = sessions_with_score.aggregate(Avg('satisfaction_score'))['satisfaction_score__avg']
        stats.avg_satisfaction_score = round(avg_score, 2)
    
    stats.last_session_at = session.created_at
    stats.save()
    
    logger.info(f"更新用户统计: user={user.username}, sessions={stats.total_sessions}")

