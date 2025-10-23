"""
AI视频生成视图
"""

import logging
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from core.response import StandardResponse
from .services import ai_video_service, VideoGenerationError
from .serializers import (
    TextToVideoSerializer, ImageToVideoSerializer, VideoResponseSerializer,
    VideoTaskStatusSerializer, VideoHistorySerializer, UserVideoStatsSerializer,
    VideoStylePresetSerializer
)

logger = logging.getLogger(__name__)


@extend_schema(
    operation_id='text_to_video',
    summary="文生视频",
    description="根据文本提示词生成视频",
    request=TextToVideoSerializer,
    responses={
        200: VideoResponseSerializer,
        400: None,
        401: None,
        500: None
    },
    tags=['AI视频']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def text_to_video(request):
    """文生视频"""
    try:
        serializer = TextToVideoSerializer(data=request.data)
        if not serializer.is_valid():
            return StandardResponse.error(
                message="请求参数错误",
                data=serializer.errors,
                code=400
            )
        
        validated_data = serializer.validated_data
        
        # 处理风格预设
        prompt = validated_data['prompt']
        if validated_data.get('style_preset_id'):
            prompt = ai_video_service.apply_style_preset(
                validated_data['style_preset_id'],
                prompt
            )
        
        # 调用AI视频服务
        result = ai_video_service.text_to_video(
            user_id=request.user.id,
            prompt=prompt,
            model=validated_data.get('model', 'wan2.5-t2v-preview'),
            resolution=validated_data.get('resolution', '1280*720'),
            duration=validated_data.get('duration', 5),
            fps=validated_data.get('fps', 24),
            seed=validated_data.get('seed')  # 添加随机种子参数
        )
        
        return StandardResponse.success(
            data=result,
            message="文生视频任务创建成功"
        )
        
    except VideoGenerationError as e:
        logger.error(f"文生视频失败: {str(e)}")
        return StandardResponse.error(
            message="文生视频失败",
            data=str(e),
            code=500
        )
    except Exception as e:
        logger.error(f"文生视频异常: {str(e)}")
        return StandardResponse.error(
            message="服务器内部错误",
            data=str(e),
            code=500
        )


@extend_schema(
    operation_id='image_to_video',
    summary="图生视频",
    description="根据输入图片和文本提示词生成视频",
    request=ImageToVideoSerializer,
    responses={
        200: VideoResponseSerializer,
        400: None,
        401: None,
        500: None
    },
    tags=['AI视频']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def image_to_video(request):
    """图生视频"""
    try:
        serializer = ImageToVideoSerializer(data=request.data)
        if not serializer.is_valid():
            return StandardResponse.error(
                message="请求参数错误",
                data=serializer.errors,
                code=400
            )
        
        validated_data = serializer.validated_data
        
        # 调用AI视频服务
        result = ai_video_service.image_to_video(
            user_id=request.user.id,
            prompt=validated_data.get('prompt', ''),
            input_image=validated_data.get('input_image'),
            input_image_url=validated_data.get('input_image_url'),
            model=validated_data.get('model', 'wan2.5-i2v-preview'),
            resolution=validated_data.get('resolution', '720P'),  # 使用 P 格式
            duration=validated_data.get('duration', 5),
            fps=validated_data.get('fps', 24)
        )
        
        return StandardResponse.success(
            data=result,
            message="图生视频任务创建成功"
        )
        
    except VideoGenerationError as e:
        logger.error(f"图生视频失败: {str(e)}")
        return StandardResponse.error(
            message="图生视频失败",
            data=str(e),
            code=500
        )
    except Exception as e:
        logger.error(f"图生视频异常: {str(e)}")
        return StandardResponse.error(
            message="服务器内部错误",
            data=str(e),
            code=500
        )


@extend_schema(
    operation_id='get_video_task_status',
    summary="获取视频任务状态",
    description="根据任务ID获取视频生成任务的状态",
    parameters=[
        OpenApiParameter(
            name='task_id',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.PATH,
            description="任务ID",
            required=True
        )
    ],
    responses={
        200: VideoTaskStatusSerializer,
        404: None,
        401: None,
        500: None
    },
    tags=['AI视频']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_video_task_status(request, task_id):
    """获取视频任务状态"""
    try:
        result = ai_video_service.get_task_status(task_id)
        
        return StandardResponse.success(
            data=result,
            message="获取任务状态成功"
        )
        
    except VideoGenerationError as e:
        logger.error(f"获取视频任务状态失败: {str(e)}")
        return StandardResponse.error(
            message="获取任务状态失败",
            data=str(e),
            code=404
        )
    except Exception as e:
        logger.error(f"获取视频任务状态异常: {str(e)}")
        return StandardResponse.error(
            message="服务器内部错误",
            data=str(e),
            code=500
        )


@extend_schema(
    operation_id='get_video_history',
    summary="获取视频生成历史",
    description="获取用户的视频生成历史记录",
    parameters=[
        OpenApiParameter(
            name='task_type',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="任务类型筛选",
            enum=['text_to_video', 'image_to_video'],
            required=False
        ),
        OpenApiParameter(
            name='limit',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description="返回记录数量限制",
            default=20,
            required=False
        )
    ],
    responses={
        200: VideoHistorySerializer(many=True),
        401: None,
        500: None
    },
    tags=['AI视频']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_video_history(request):
    """获取视频生成历史"""
    try:
        task_type = request.GET.get('task_type')
        limit = int(request.GET.get('limit', 20))
        
        result = ai_video_service.get_user_video_history(
            user_id=request.user.id,
            task_type=task_type,
            limit=limit
        )
        
        return StandardResponse.success(
            data=result,
            message="获取视频历史成功"
        )
        
    except VideoGenerationError as e:
        logger.error(f"获取视频历史失败: {str(e)}")
        return StandardResponse.error(
            message="获取视频历史失败",
            data=str(e),
            code=500
        )
    except Exception as e:
        logger.error(f"获取视频历史异常: {str(e)}")
        return StandardResponse.error(
            message="服务器内部错误",
            data=str(e),
            code=500
        )


@extend_schema(
    operation_id='get_user_video_stats',
    summary="获取用户视频统计",
    description="获取用户的视频生成使用统计",
    responses={
        200: UserVideoStatsSerializer,
        401: None,
        500: None
    },
    tags=['AI视频']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_video_stats(request):
    """获取用户视频统计"""
    try:
        from .models import UserVideoStats
        
        stats, created = UserVideoStats.objects.get_or_create(user=request.user)
        
        if created or not stats.updated_at:
            # 如果是新创建的或者没有更新过，更新一次统计
            UserVideoStats.update_stats(request.user.id)
            stats.refresh_from_db()
        
        serializer = UserVideoStatsSerializer(stats)
        
        return StandardResponse.success(
            data=serializer.data,
            message="获取用户视频统计成功"
        )
        
    except Exception as e:
        logger.error(f"获取用户视频统计异常: {str(e)}")
        return StandardResponse.error(
            message="服务器内部错误",
            data=str(e),
            code=500
        )


@extend_schema(
    operation_id='get_video_style_presets',
    summary="获取视频风格预设",
    description="获取可用的视频风格预设列表",
    responses={
        200: VideoStylePresetSerializer(many=True),
        500: None
    },
    tags=['AI视频']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_video_style_presets(request):
    """获取视频风格预设"""
    try:
        result = ai_video_service.get_video_style_presets()
        
        return StandardResponse.success(
            data=result,
            message="获取视频风格预设成功"
        )
        
    except VideoGenerationError as e:
        logger.error(f"获取视频风格预设失败: {str(e)}")
        return StandardResponse.error(
            message="获取视频风格预设失败",
            data=str(e),
            code=500
        )
    except Exception as e:
        logger.error(f"获取视频风格预设异常: {str(e)}")
        return StandardResponse.error(
            message="服务器内部错误",
            data=str(e),
            code=500
        )
