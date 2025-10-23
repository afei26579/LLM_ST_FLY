"""
AI音频处理视图
"""

import logging
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from core.response import StandardResponse
from .services import ai_audio_service, AudioProcessingError
from .serializers import (
    SpeechToTextSerializer, TextToSpeechSerializer, VoiceCloneSerializer,
    AudioResponseSerializer, TaskStatusSerializer, AudioHistorySerializer,
    UserAudioStatsSerializer
)

logger = logging.getLogger(__name__)


@extend_schema(
    operation_id='speech_to_text',
    summary="语音转文字（流式输出）",
    description="上传音频文件，将语音转换为文字（支持流式输出）",
    request=SpeechToTextSerializer,
    responses={
        200: AudioResponseSerializer,
        400: None,
        401: None,
        500: None
    },
    tags=['AI音频']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def speech_to_text(request):
    """语音转文字（流式输出）"""
    from django.http import StreamingHttpResponse
    import json
    
    try:
        serializer = SpeechToTextSerializer(data=request.data)
        if not serializer.is_valid():
            return StandardResponse.error(
                message="请求参数错误",
                data=serializer.errors,
                code=400
            )
        
        validated_data = serializer.validated_data
        
        # 创建音频任务记录
        from .models import AudioTask, SpeechToTextTask
        from django.db import transaction
        
        with transaction.atomic():
            audio_task = AudioTask.objects.create(
                user_id=request.user.id,
                task_type='speech_to_text',
                status='pending'
            )
            
            # 保存上传的文件
            if validated_data.get('audio_file'):
                audio_task.input_audio_file = validated_data['audio_file']
                audio_task.save()
            
            # 创建详细配置
            stt_task = SpeechToTextTask.objects.create(
                audio_task=audio_task,
                language=validated_data.get('language', 'auto'),
                model=validated_data.get('model', 'qwen-audio-turbo-latest')
            )
        
        logger.info(f"开始流式语音识别任务: {audio_task.task_id}")
        
        # 更新状态为处理中
        audio_task.status = 'processing'
        audio_task.save()
        
        # 生成流式响应
        def generate_stream():
            try:
                full_text = ""
                
                # 调用流式识别 API
                for chunk in ai_audio_service._call_speech_recognition_api_stream(audio_task, stt_task):
                    # 发送 SSE 格式数据
                    data = json.dumps(chunk, ensure_ascii=False)
                    yield f"data: {data}\n\n"
                    
                    # 累积完整文本
                    if chunk.get('type') == 'chunk':
                        full_text = chunk.get('full_text', '')
                    elif chunk.get('type') == 'done':
                        full_text = chunk.get('text', '')
                
                # 更新数据库
                audio_task.status = 'completed'
                audio_task.completed_at = timezone.now()
                audio_task.output_text = full_text
                audio_task.save()
                
                # 更新用户统计
                from .models import UserAudioStats
                UserAudioStats.update_stats(request.user.id)
                
                logger.info(f"流式语音识别完成: {audio_task.task_id}")
                
            except Exception as e:
                logger.error(f"流式识别异常: {str(e)}")
                audio_task.status = 'failed'
                audio_task.error_message = str(e)
                audio_task.save()
                
                error_data = json.dumps({'type': 'error', 'message': str(e)}, ensure_ascii=False)
                yield f"data: {error_data}\n\n"
        
        # 返回流式响应
        response = StreamingHttpResponse(
            generate_stream(),
            content_type='text/event-stream'
        )
        response['Cache-Control'] = 'no-cache'
        response['X-Accel-Buffering'] = 'no'
        return response
        
    except Exception as e:
        logger.error(f"语音转文字异常: {str(e)}")
        return StandardResponse.error(
            message="服务器内部错误",
            data=str(e),
            code=500
        )


@extend_schema(
    operation_id='text_to_speech',
    summary="文字转语音",
    description="将文本转换为语音音频",
    request=TextToSpeechSerializer,
    responses={
        200: AudioResponseSerializer,
        400: None,
        401: None,
        500: None
    },
    tags=['AI音频']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def text_to_speech(request):
    """文字转语音"""
    try:
        serializer = TextToSpeechSerializer(data=request.data)
        if not serializer.is_valid():
            return StandardResponse.error(
                message="请求参数错误",
                data=serializer.errors,
                code=400
            )
        
        validated_data = serializer.validated_data
        
        # 调用AI音频服务
        result = ai_audio_service.text_to_speech(
            user_id=request.user.id,
            text=validated_data['text'],
            voice=validated_data.get('voice', 'Cherry'),
            language_type=validated_data.get('language_type', 'Chinese'),
            format=validated_data.get('format', 'wav')
        )
        
        return StandardResponse.success(
            data=result,
            message="文字转语音成功"
        )
        
    except AudioProcessingError as e:
        logger.error(f"文字转语音失败: {str(e)}")
        return StandardResponse.error(
            message="文字转语音失败",
            data=str(e),
            code=500
        )
    except Exception as e:
        logger.error(f"文字转语音异常: {str(e)}")
        return StandardResponse.error(
            message="服务器内部错误",
            data=str(e),
            code=500
        )


@extend_schema(
    operation_id='voice_clone',
    summary="语音克隆",
    description="基于参考音频和文本克隆语音",
    request=VoiceCloneSerializer,
    responses={
        200: AudioResponseSerializer,
        400: None,
        401: None,
        500: None
    },
    tags=['AI音频']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def voice_clone(request):
    """语音克隆"""
    try:
        serializer = VoiceCloneSerializer(data=request.data)
        if not serializer.is_valid():
            return StandardResponse.error(
                message="请求参数错误",
                data=serializer.errors,
                code=400
            )
        
        validated_data = serializer.validated_data
        
        # 调用AI音频服务
        result = ai_audio_service.voice_clone(
            user_id=request.user.id,
            reference_audio=validated_data['reference_audio'],
            reference_text=validated_data['reference_text'],
            target_text=validated_data['target_text'],
            model=validated_data.get('model', 'sambert-v1')
        )
        
        return StandardResponse.success(
            data=result,
            message="语音克隆成功"
        )
        
    except AudioProcessingError as e:
        logger.error(f"语音克隆失败: {str(e)}")
        return StandardResponse.error(
            message="语音克隆失败",
            data=str(e),
            code=500
        )
    except Exception as e:
        logger.error(f"语音克隆异常: {str(e)}")
        return StandardResponse.error(
            message="服务器内部错误",
            data=str(e),
            code=500
        )


@extend_schema(
    operation_id='get_audio_task_status',
    summary="获取任务状态",
    description="根据任务ID获取音频处理任务的状态",
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
        200: TaskStatusSerializer,
        404: None,
        401: None,
        500: None
    },
    tags=['AI音频']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_task_status(request, task_id):
    """获取任务状态"""
    try:
        result = ai_audio_service.get_task_status(task_id)
        
        return StandardResponse.success(
            data=result,
            message="获取任务状态成功"
        )
        
    except AudioProcessingError as e:
        logger.error(f"获取任务状态失败: {str(e)}")
        return StandardResponse.error(
            message="获取任务状态失败",
            data=str(e),
            code=404
        )
    except Exception as e:
        logger.error(f"获取任务状态异常: {str(e)}")
        return StandardResponse.error(
            message="服务器内部错误",
            data=str(e),
            code=500
        )


@extend_schema(
    operation_id='get_audio_history',
    summary="获取音频处理历史",
    description="获取用户的音频处理历史记录",
    parameters=[
        OpenApiParameter(
            name='task_type',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="任务类型筛选",
            enum=['speech_to_text', 'text_to_speech', 'voice_clone'],
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
        200: AudioHistorySerializer(many=True),
        401: None,
        500: None
    },
    tags=['AI音频']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_audio_history(request):
    """获取音频处理历史"""
    try:
        task_type = request.GET.get('task_type')
        limit = int(request.GET.get('limit', 20))
        
        result = ai_audio_service.get_user_audio_history(
            user_id=request.user.id,
            task_type=task_type,
            limit=limit
        )
        
        return StandardResponse.success(
            data=result,
            message="获取音频历史成功"
        )
        
    except AudioProcessingError as e:
        logger.error(f"获取音频历史失败: {str(e)}")
        return StandardResponse.error(
            message="获取音频历史失败",
            data=str(e),
            code=500
        )
    except Exception as e:
        logger.error(f"获取音频历史异常: {str(e)}")
        return StandardResponse.error(
            message="服务器内部错误",
            data=str(e),
            code=500
        )


@extend_schema(
    operation_id='get_user_audio_stats',
    summary="获取用户音频统计",
    description="获取用户的音频处理使用统计",
    responses={
        200: UserAudioStatsSerializer,
        401: None,
        500: None
    },
    tags=['AI音频']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_stats(request):
    """获取用户音频统计"""
    try:
        from .models import UserAudioStats
        
        stats, created = UserAudioStats.objects.get_or_create(user=request.user)
        
        if created or not stats.updated_at:
            # 如果是新创建的或者没有更新过，更新一次统计
            UserAudioStats.update_stats(request.user.id)
            stats.refresh_from_db()
        
        serializer = UserAudioStatsSerializer(stats)
        
        return StandardResponse.success(
            data=serializer.data,
            message="获取用户统计成功"
        )
        
    except Exception as e:
        logger.error(f"获取用户统计异常: {str(e)}")
        return StandardResponse.error(
            message="服务器内部错误",
            data=str(e),
            code=500
        )
