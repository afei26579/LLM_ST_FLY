"""
智能体视图
"""

import logging
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from core.response import StandardResponse
from .services import ai_agent_service, AgentServiceError
from .serializers import (
    AgentSerializer, ConversationSerializer, ConversationDetailSerializer,
    MessageSerializer, UserAgentStatsSerializer, ChatRequest, ChatResponse,
    CreateConversationRequest, ConversationListRequest
)
from .models import Agent, AgentType

logger = logging.getLogger(__name__)


@extend_schema(
    operation_id='list_agents',
    summary="获取智能体列表",
    description="获取所有可用的智能体列表",
    responses={
        200: AgentSerializer(many=True),
        401: None
    },
    tags=['智能体']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_agents(request):
    """获取智能体列表"""
    try:
        # 确保智能体已初始化
        ai_agent_service.initialize_agents()
        
        agents = Agent.objects.filter(is_active=True).order_by('created_at')
        serializer = AgentSerializer(agents, many=True)
        
        return StandardResponse.success(
            data=serializer.data,
            message="获取智能体列表成功"
        )
        
    except Exception as e:
        logger.error(f"获取智能体列表失败: {str(e)}")
        return StandardResponse.error(
            message="获取智能体列表失败",
            data=str(e),
            code=500
        )


@extend_schema(
    operation_id='agent_chat',
    summary="与智能体聊天",
    description="发送消息给指定类型的智能体，获取AI回复",
    request=ChatRequest,
    responses={
        200: ChatResponse,
        400: None,
        401: None,
        500: None
    },
    tags=['智能体']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def chat(request):
    """与智能体聊天"""
    try:
        serializer = ChatRequest(data=request.data)
        if not serializer.is_valid():
            return StandardResponse.error(
                message="请求参数错误",
                data=serializer.errors,
                code=400
            )
        
        validated_data = serializer.validated_data
        
        # 调用聊天服务
        result = ai_agent_service.chat(
            user=request.user,
            message_content=validated_data['message'],
            agent_type=validated_data['agent_type'],
            conversation_id=validated_data.get('conversation_id')
        )
        
        # 序列化返回数据
        response_data = {
            'conversation_id': result['conversation_id'],
            'message': result['message'],
            'message_id': result['message_id'],
            'agent': AgentSerializer(result['agent']).data,
            'tokens_used': result['tokens_used'],
            'is_new_conversation': result['is_new_conversation']
        }
        
        return StandardResponse.success(
            data=response_data,
            message="聊天成功"
        )
        
    except AgentServiceError as e:
        logger.error(f"聊天服务错误: {str(e)}")
        return StandardResponse.error(
            message=str(e),
            code=400
        )
    except Exception as e:
        logger.error(f"聊天失败: {str(e)}")
        return StandardResponse.error(
            message="聊天失败，请重试",
            data=str(e),
            code=500
        )


@extend_schema(
    operation_id='create_conversation',
    summary="创建新对话",
    description="创建与指定智能体的新对话会话",
    request=CreateConversationRequest,
    responses={
        200: ConversationSerializer,
        400: None,
        401: None,
        500: None
    },
    tags=['智能体']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_conversation(request):
    """创建新对话"""
    try:
        serializer = CreateConversationRequest(data=request.data)
        if not serializer.is_valid():
            return StandardResponse.error(
                message="请求参数错误",
                data=serializer.errors,
                code=400
            )
        
        validated_data = serializer.validated_data
        
        # 创建对话
        conversation = ai_agent_service.create_conversation(
            user=request.user,
            agent_type=validated_data['agent_type'],
            title=validated_data.get('title')
        )
        
        response_data = ConversationSerializer(conversation).data
        
        return StandardResponse.success(
            data=response_data,
            message="创建对话成功"
        )
        
    except AgentServiceError as e:
        logger.error(f"创建对话失败: {str(e)}")
        return StandardResponse.error(
            message=str(e),
            code=400
        )
    except Exception as e:
        logger.error(f"创建对话异常: {str(e)}")
        return StandardResponse.error(
            message="创建对话失败，请重试",
            data=str(e),
            code=500
        )


@extend_schema(
    operation_id='list_conversations',
    summary="获取对话列表",
    description="获取用户的对话会话列表",
    parameters=[
        OpenApiParameter(
            name='agent_type',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="按智能体类型筛选",
            enum=[choice[0] for choice in AgentType.choices],
            required=False
        ),
        OpenApiParameter(
            name='limit',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description="返回数量限制",
            default=20,
            required=False
        ),
        OpenApiParameter(
            name='offset',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description="偏移量",
            default=0,
            required=False
        )
    ],
    responses={
        200: ConversationSerializer(many=True),
        401: None,
        500: None
    },
    tags=['智能体']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_conversations(request):
    """获取对话列表"""
    try:
        # 验证查询参数
        agent_type = request.GET.get('agent_type')
        # 将空字符串转换为None
        if agent_type == '':
            agent_type = None
            
        params = {
            'agent_type': agent_type,
            'limit': int(request.GET.get('limit', 20)),
            'offset': int(request.GET.get('offset', 0))
        }
        
        serializer = ConversationListRequest(data=params)
        if not serializer.is_valid():
            return StandardResponse.error(
                message="查询参数错误",
                data=serializer.errors,
                code=400
            )
        
        validated_data = serializer.validated_data
        
        # 获取对话列表
        conversations = ai_agent_service.get_user_conversations(
            user=request.user,
            agent_type=validated_data.get('agent_type'),
            limit=validated_data['limit'],
            offset=validated_data['offset']
        )
        
        response_data = ConversationSerializer(conversations, many=True).data
        
        return StandardResponse.success(
            data=response_data,
            message="获取对话列表成功"
        )
        
    except ValueError as e:
        return StandardResponse.error(
            message="参数格式错误",
            data=str(e),
            code=400
        )
    except Exception as e:
        logger.error(f"获取对话列表失败: {str(e)}")
        return StandardResponse.error(
            message="获取对话列表失败",
            data=str(e),
            code=500
        )


@extend_schema(
    operation_id='get_conversation_detail',
    summary="获取对话详情",
    description="获取指定对话的详细信息，包含所有消息",
    parameters=[
        OpenApiParameter(
            name='conversation_id',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.PATH,
            description="对话ID",
            required=True
        )
    ],
    responses={
        200: ConversationDetailSerializer,
        404: None,
        401: None,
        500: None
    },
    tags=['智能体']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_conversation_detail(request, conversation_id):
    """获取对话详情"""
    try:
        conversation = ai_agent_service.get_conversation(conversation_id, request.user)
        response_data = ConversationDetailSerializer(conversation).data
        
        return StandardResponse.success(
            data=response_data,
            message="获取对话详情成功"
        )
        
    except AgentServiceError as e:
        return StandardResponse.error(
            message=str(e),
            code=404
        )
    except Exception as e:
        logger.error(f"获取对话详情失败: {str(e)}")
        return StandardResponse.error(
            message="获取对话详情失败",
            data=str(e),
            code=500
        )


@extend_schema(
    operation_id='get_user_agent_stats',
    summary="获取用户智能体统计",
    description="获取当前用户的智能体使用统计信息",
    responses={
        200: UserAgentStatsSerializer,
        401: None,
        500: None
    },
    tags=['智能体']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_stats(request):
    """获取用户智能体统计"""
    try:
        stats = ai_agent_service.get_or_create_user_stats(request.user)
        response_data = UserAgentStatsSerializer(stats).data
        
        return StandardResponse.success(
            data=response_data,
            message="获取用户统计成功"
        )
        
    except Exception as e:
        logger.error(f"获取用户统计失败: {str(e)}")
        return StandardResponse.error(
            message="获取用户统计失败",
            data=str(e),
            code=500
        )


@extend_schema(
    operation_id='delete_conversation',
    summary="删除对话",
    description="删除指定的对话会话",
    parameters=[
        OpenApiParameter(
            name='conversation_id',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.PATH,
            description="对话ID",
            required=True
        )
    ],
    responses={
        200: None,
        404: None,
        401: None,
        500: None
    },
    tags=['智能体']
)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_conversation(request, conversation_id):
    """删除对话"""
    try:
        conversation = ai_agent_service.get_conversation(conversation_id, request.user)
        conversation.is_active = False
        conversation.save()
        
        return StandardResponse.success(
            message="删除对话成功"
        )
        
    except AgentServiceError as e:
        return StandardResponse.error(
            message=str(e),
            code=404
        )
    except Exception as e:
        logger.error(f"删除对话失败: {str(e)}")
        return StandardResponse.error(
            message="删除对话失败",
            data=str(e),
            code=500
        )
