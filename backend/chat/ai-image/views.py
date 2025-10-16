"""
AI图像生成视图
处理图像生成相关的HTTP请求
"""

import logging
from typing import Any, Dict

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes

from core.response import StandardResponse
from .serializers import (
    ImageGenerationRequestSerializer,
    ImageGenerationResponseSerializer,
    ImageTaskStatusSerializer,
    ImageHistorySerializer
)
from .services import ai_image_service, ImageGenerationError, ImageDownloadError

logger = logging.getLogger(__name__)


@extend_schema(
    summary="生成AI图像",
    description="根据提示词生成AI图像，支持正面和反面提示词，以及多种风格参数",
    request=ImageGenerationRequestSerializer,
    responses={
        200: ImageGenerationResponseSerializer,
        400: OpenApiTypes.OBJECT,
        500: OpenApiTypes.OBJECT,
    },
    examples=[
        OpenApiExample(
            "基础图像生成",
            summary="基础图像生成示例",
            description="使用基本参数生成图像",
            value={
                "prompt": "一只可爱的小猫在花园里玩耍",
                "negative_prompt": "模糊，低质量",
                "size": "1328*1328",
                "n": 1,
                "prompt_extend": True,
                "watermark": True
            }
        ),
        OpenApiExample(
            "高级图像生成",
            summary="高级图像生成示例", 
            description="使用多种风格参数生成图像",
            value={
                "prompt": "未来城市的天际线",
                "negative_prompt": "模糊，噪点，低质量",
                "size": "1664*928",
                "n": 2,
                "prompt_extend": True,
                "watermark": False,
                "style": "3d",
                "shot_type": "long_shot",
                "angle": "aerial",
                "lighting": "neon"
            }
        )
    ]
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_image(request: Request) -> Response:
    """
    生成AI图像
    
    接收用户的图像生成请求，调用AI服务生成图像并返回结果
    """
    try:
        # 数据验证
        serializer = ImageGenerationRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return StandardResponse.error(
                message="请求参数验证失败",
                data=serializer.errors,
                code=400
            )
        
        validated_data = serializer.validated_data
        user_id = request.user.id if request.user.is_authenticated else None
        
        logger.info(f"用户 {user_id} 开始生成图像，提示词: {validated_data['prompt'][:100]}...")
        
        # 使用增强后的提示词
        enhanced_prompt = validated_data.get('enhanced_prompt', validated_data['prompt'])
        
        # 调用AI图像生成服务（固定生成1张图片）
        result = ai_image_service.generate_image(
            prompt=enhanced_prompt,
            negative_prompt=validated_data.get('negative_prompt'),
            size=validated_data.get('size', '1328*1328'),
            prompt_extend=validated_data.get('prompt_extend', True),
            watermark=validated_data.get('watermark', True),
            style=validated_data.get('style'),
            shot_type=validated_data.get('shot_type'),
            angle=validated_data.get('angle'),
            shooting_technique=validated_data.get('shooting_technique'),
            lighting=validated_data.get('lighting'),
            user_id=user_id
        )
        
        # 添加增强提示词到结果中
        result['enhanced_prompt'] = enhanced_prompt
        
        logger.info(f"用户 {user_id} 图像生成成功，任务ID: {result.get('task_id')}")
        
        return StandardResponse.success(
            data=result,
            message="图像生成成功"
        )
        
    except ImageGenerationError as e:
        logger.error(f"图像生成失败: {str(e)}")
        return StandardResponse.error(
            message=f"图像生成失败: {str(e)}",
            code=400
        )
    except ImageDownloadError as e:
        logger.error(f"图像下载失败: {str(e)}")
        return StandardResponse.error(
            message=f"图像处理失败: {str(e)}",
            code=500
        )
    except Exception as e:
        logger.error(f"生成图像时发生未预期错误: {str(e)}")
        return StandardResponse.error(
            message="服务器内部错误，请稍后重试",
            code=500
        )


@extend_schema(
    summary="查询图像生成任务状态",
    description="根据任务ID查询图像生成任务的状态",
    parameters=[
        OpenApiParameter(
            name='task_id',
            description='任务ID',
            required=True,
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY
        )
    ],
    responses={
        200: OpenApiTypes.OBJECT,
        400: OpenApiTypes.OBJECT,
        404: OpenApiTypes.OBJECT,
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_task_status(request: Request) -> Response:
    """
    查询图像生成任务状态
    
    用于查询异步图像生成任务的状态和结果
    """
    try:
        task_id = request.query_params.get('task_id')
        if not task_id:
            return StandardResponse.error(
                message="缺少任务ID参数",
                code=400
            )
        
        logger.info(f"查询任务状态: {task_id}")
        
        # 查询任务状态
        result = ai_image_service.get_task_status(task_id)
        
        return StandardResponse.success(
            data=result,
            message="查询任务状态成功"
        )
        
    except ImageGenerationError as e:
        logger.error(f"查询任务状态失败: {str(e)}")
        return StandardResponse.error(
            message=f"查询任务状态失败: {str(e)}",
            code=400
        )
    except Exception as e:
        logger.error(f"查询任务状态时发生未预期错误: {str(e)}")
        return StandardResponse.error(
            message="服务器内部错误，请稍后重试",
            code=500
        )


@extend_schema(
    summary="获取图像生成历史",
    description="获取用户的图像生成历史记录",
    parameters=[
        OpenApiParameter(
            name='page',
            description='页码',
            required=False,
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            default=1
        ),
        OpenApiParameter(
            name='page_size',
            description='每页数量',
            required=False,
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            default=20
        )
    ],
    responses={
        200: ImageHistorySerializer(many=True),
        400: OpenApiTypes.OBJECT,
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_image_history(request: Request) -> Response:
    """
    获取图像生成历史
    
    返回用户的图像生成历史记录，支持分页
    """
    try:
        from .models import GeneratedImage
        from django.core.paginator import Paginator
        
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))
        user_id = request.user.id
        
        logger.info(f"获取用户 {user_id} 的图像历史，页码: {page}, 页大小: {page_size}")
        
        # 查询用户的所有生成图片，按创建时间倒序
        all_images = GeneratedImage.objects.filter(
            task__user_id=user_id,
            task__status='completed'
        ).select_related('task').order_by('-created_at')
        
        # 分页
        paginator = Paginator(all_images, page_size)
        page_obj = paginator.get_page(page)
        
        # 构建响应数据
        images_list = []
        for img in page_obj:
            # 确保返回完整的URL
            saved_url = img.saved_url
            if saved_url and saved_url.startswith('/'):
                # 相对路径转为绝对路径
                from django.conf import settings
                base_url = getattr(settings, 'BASE_URL', 'http://localhost:8000')
                saved_url = f"{base_url}{saved_url}"
            
            images_list.append({
                'id': img.id,
                'task_id': img.task.task_id,
                'image_source': img.image_source,  # 图像来源标识
                'original_url': img.original_url,
                'saved_url': saved_url,
                'filename': img.filename,
                'size': img.file_size,
                'width': img.width,
                'height': img.height,
                'orig_prompt': img.orig_prompt or img.task.prompt,
                'actual_prompt': img.actual_prompt,
                'enhanced_prompt': img.task.enhanced_prompt,
                'negative_prompt': img.task.negative_prompt,
                'task_size': img.task.size,
                'style': img.task.style,
                'shot_type': img.task.shot_type,
                'angle': img.task.angle,
                'shooting_technique': img.task.shooting_technique,
                'lighting': img.task.lighting,
                'prompt_extend': img.task.prompt_extend,
                'watermark': img.task.watermark,
                'download_time': img.download_time.isoformat() if img.download_time else None,
                'created_at': img.created_at.isoformat(),
                'view_count': img.view_count,
                'download_count': img.download_count
            })
        
        return StandardResponse.success(
            data={
                'list': images_list,
                'total': paginator.count,
                'page': page,
                'page_size': page_size,
                'total_pages': paginator.num_pages,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous()
            },
            message="获取图像历史成功"
        )
        
    except ValueError as e:
        return StandardResponse.error(
            message="页码参数格式错误",
            code=400
        )
    except Exception as e:
        logger.error(f"获取图像历史时发生未预期错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return StandardResponse.error(
            message="服务器内部错误，请稍后重试",
            code=500
        )


@extend_schema(
    summary="获取用户图像统计",
    description="获取用户的图像生成统计信息",
    parameters=[
        OpenApiParameter(
            name='days',
            description='统计天数',
            required=False,
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            default=30
        )
    ],
    responses={
        200: OpenApiTypes.OBJECT,
        400: OpenApiTypes.OBJECT,
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_stats(request: Request) -> Response:
    """
    获取用户图像统计
    
    返回用户在指定时间段内的图像生成统计信息
    """
    try:
        days = int(request.query_params.get('days', 30))
        user_id = request.user.id
        
        if days <= 0 or days > 365:
            return StandardResponse.error(
                message="统计天数必须在1-365之间",
                code=400
            )
        
        logger.info(f"获取用户 {user_id} 的图像统计，统计天数: {days}")
        
        # 获取用户统计
        stats = ai_image_service.get_user_image_stats(user_id, days)
        
        return StandardResponse.success(
            data=stats,
            message="获取用户统计成功"
        )
        
    except ValueError as e:
        return StandardResponse.error(
            message="统计天数参数格式错误",
            code=400
        )
    except Exception as e:
        logger.error(f"获取用户统计时发生未预期错误: {str(e)}")
        return StandardResponse.error(
            message="服务器内部错误，请稍后重试",
            code=500
        )


@extend_schema(
    summary="获取预设参数",
    description="获取图像生成的预设参数选项",
    responses={
        200: OpenApiTypes.OBJECT,
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_presets(request: Request) -> Response:
    """
    获取预设参数
    
    返回图像生成可用的预设参数选项
    """
    try:
        presets = {
            'sizes': [
                {'value': '1328*1328', 'label': '1:1 (1328x1328)', 'aspect_ratio': '1:1'},
                {'value': '1664*928', 'label': '16:9 (1664x928)', 'aspect_ratio': '16:9'},
                {'value': '928*1664', 'label': '9:16 (928x1664)', 'aspect_ratio': '9:16'},
                {'value': '1472*1140', 'label': '4:3 (1472x1140)', 'aspect_ratio': '4:3'},
                {'value': '1140*1472', 'label': '3:4 (1140x1472)', 'aspect_ratio': '3:4'},
            ],
            'styles': [
                {'value': '', 'label': '默认'},
                {'value': '3d_cartoon', 'label': '3D卡通'},
                {'value': 'wasteland', 'label': '废土风'},
                {'value': 'pointillism', 'label': '点彩画'},
                {'value': 'surreal', 'label': '超现实'},
                {'value': 'watercolor', 'label': '水彩'},
                {'value': 'clay', 'label': '粘土'},
                {'value': 'realistic', 'label': '写实'},
                {'value': 'ceramic', 'label': '陶瓷'},
                {'value': '3d', 'label': '3D'},
                {'value': 'ink_wash', 'label': '水墨'},
                {'value': 'origami', 'label': '折纸'},
                {'value': 'meticulous', 'label': '工笔'},
                {'value': 'chinese_style', 'label': '国风水墨'},
            ],
            'shot_types': [
                {'value': '', 'label': '默认'},
                {'value': 'long_shot', 'label': '远景'},
                {'value': 'full_shot', 'label': '全景'},
                {'value': 'medium_shot', 'label': '中景'},
                {'value': 'close_up', 'label': '近景'},
                {'value': 'extreme_close_up', 'label': '特写'},
            ],
            'angles': [
                {'value': '', 'label': '默认'},
                {'value': 'eye_level', 'label': '平视'},
                {'value': 'high_angle', 'label': '俯视'},
                {'value': 'low_angle', 'label': '仰视'},
                {'value': 'aerial', 'label': '航拍'},
            ],
            'shooting_techniques': [
                {'value': '', 'label': '默认'},
                {'value': 'macro', 'label': '微距'},
                {'value': 'ultra_wide', 'label': '超广角'},
                {'value': 'telephoto', 'label': '长焦'},
                {'value': 'fisheye', 'label': '鱼眼'},
            ],
            'lighting': [
                {'value': '', 'label': '默认'},
                {'value': 'natural', 'label': '自然光'},
                {'value': 'backlight', 'label': '逆光'},
                {'value': 'neon', 'label': '霓虹灯'},
                {'value': 'ambient', 'label': '氛围光'},
            ]
        }
        
        return StandardResponse.success(
            data=presets,
            message="获取预设参数成功"
        )
        
    except Exception as e:
        logger.error(f"获取预设参数时发生未预期错误: {str(e)}")
        return StandardResponse.error(
            message="服务器内部错误，请稍后重试",
            code=500
        )


@extend_schema(
    summary="图像理解",
    description="上传图片，AI分析并描述图像内容",
    request={
        'multipart/form-data': {
            'type': 'object',
            'properties': {
                'image': {
                    'type': 'string',
                    'format': 'binary',
                    'description': '要分析的图片文件'
                }
            }
        }
    },
    responses={200: OpenApiTypes.OBJECT}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def understand_image(request: Request) -> Response:
    """
    图像理解功能
    上传图片，AI分析并描述图像内容
    """
    try:
        # 调试：打印所有接收到的数据
        logger.info(f"接收到的FILES: {list(request.FILES.keys())}")
        logger.info(f"接收到的POST数据: {list(request.POST.keys())}")
        
        # 检查多种可能的字段名
        image_file = None
        for field_name in ['image', 'file', 'picture', 'photo']:
            if field_name in request.FILES:
                image_file = request.FILES[field_name]
                logger.info(f"找到图片文件，字段名: {field_name}, 文件名: {image_file.name}")
                break
        
        if not image_file:
            logger.error(f"未找到图片文件。FILES keys: {list(request.FILES.keys())}")
            return StandardResponse.error(
                message="请上传图片文件",
                code=400,
                request_id=getattr(request, 'request_id', None)
            )
        
        # 获取分析类型（如果有的话）
        analyze_type = request.POST.get('analyze_type', 'description')
        logger.info(f"分析类型: {analyze_type}")
        
        # 调用图像理解服务
        result = ai_image_service.understand_image(request.user, image_file, analyze_type)
        
        return StandardResponse.success(
            data={
                'description': result['description'],
                'confidence': result.get('confidence', 0.8),
                'analyze_type': result.get('analyze_type', analyze_type)
            },
            message=f"{'图像分析' if analyze_type == 'description' else '题目解答' if analyze_type == 'question' else '文字识别'}完成",
            request_id=getattr(request, 'request_id', None)
        )
        
    except Exception as e:
        logger.error(f"图像理解失败: {e}")
        return StandardResponse.error(
            message=f"图像理解失败: {str(e)}",
            code=500,
            request_id=getattr(request, 'request_id', None)
        )


@extend_schema(
    summary="物体检测定位",
    description="使用qwen-image-edit模型检测并标注图像中的指定物体",
    request={
        'multipart/form-data': {
            'type': 'object',
            'properties': {
                'image': {
                    'type': 'string',
                    'format': 'binary',
                    'description': '要检测的图片文件'
                },
                'detection_prompt': {
                    'type': 'string',
                    'description': '要检测的物体描述，例如：红色汽车、戴帽子的人'
                }
            },
            'required': ['image', 'detection_prompt']
        }
    },
    responses={200: OpenApiTypes.OBJECT}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def detect_objects(request: Request) -> Response:
    """
    物体检测和定位功能
    使用qwen-image-edit模型检测并标注图像中的指定物体
    """
    try:
        # 调试：打印所有接收到的数据
        logger.info(f"物体检测接收到的FILES: {list(request.FILES.keys())}")
        logger.info(f"物体检测接收到的POST数据: {list(request.POST.keys())}")
        
        # 检查图片文件
        image_file = None
        for field_name in ['image', 'file', 'picture', 'photo']:
            if field_name in request.FILES:
                image_file = request.FILES[field_name]
                logger.info(f"找到图片文件，字段名: {field_name}, 文件名: {image_file.name}")
                break
        
        if not image_file:
            logger.error(f"未找到图片文件。FILES keys: {list(request.FILES.keys())}")
            return StandardResponse.error(
                message="请上传图片文件",
                code=400,
                request_id=getattr(request, 'request_id', None)
            )
        
        # 获取检测提示词
        detection_prompt = request.POST.get('detection_prompt', '').strip()
        logger.info(f"物体检测提示词: {detection_prompt}")
        
        if not detection_prompt:
            return StandardResponse.error(
                message="请提供要检测的物体描述",
                code=400,
                request_id=getattr(request, 'request_id', None)
            )
        
        # 调用物体检测服务
        result = ai_image_service.detect_objects(request.user, image_file, detection_prompt)
        
        return StandardResponse.success(
            data={
                'annotated_image_url': result.get('annotated_image_url'),  # 标注后的图片URL
                'description': result['description'],  # 文字描述
                'confidence': result.get('confidence', 0.8)
            },
            message="物体定位完成",
            request_id=getattr(request, 'request_id', None)
        )
        
    except Exception as e:
        logger.error(f"物体检测失败: {e}")
        return StandardResponse.error(
            message=f"物体检测失败: {str(e)}",
            code=500,
            request_id=getattr(request, 'request_id', None)
        )


@extend_schema(
    summary="图像编辑",
    description="上传图片并根据提示词进行编辑",
    request={
        'multipart/form-data': {
            'type': 'object',
            'properties': {
                'image': {
                    'type': 'string',
                    'format': 'binary',
                    'description': '要编辑的图片文件'
                },
                'prompt': {
                    'type': 'string',
                    'description': '编辑指令'
                },
                'edit_type': {
                    'type': 'string',
                    'enum': ['prompt', 'background', 'style'],
                    'description': '编辑类型'
                },
                'style': {
                    'type': 'string',
                    'description': '风格名称（当edit_type为style时使用）'
                }
            }
        }
    },
    responses={200: OpenApiTypes.OBJECT}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def edit_image(request: Request) -> Response:
    """
    图像编辑功能
    根据提示词对上传的图片进行编辑
    """
    try:
        if 'image' not in request.FILES:
            return StandardResponse.error(
                message="请上传图片文件",
                code=400,
                request_id=getattr(request, 'request_id', None)
            )
        
        image_file = request.FILES['image']
        prompt = request.data.get('prompt', '')
        edit_type = request.data.get('edit_type', 'prompt')
        style = request.data.get('style', '')
        
        if not prompt and edit_type != 'style':
            return StandardResponse.error(
                message="请提供编辑指令",
                code=400,
                request_id=getattr(request, 'request_id', None)
            )
        
        # 调用图像编辑服务
        result = ai_image_service.edit_image(
            user=request.user,
            image_file=image_file,
            prompt=prompt,
            edit_type=edit_type,
            style=style
        )
        
        return StandardResponse.success(
            data={
                'edited_image_url': result['edited_image_url'],
                'task_id': result.get('task_id'),
                'original_prompt': prompt
            },
            message="图像编辑完成",
            request_id=getattr(request, 'request_id', None)
        )
        
    except Exception as e:
        logger.error(f"图像编辑失败: {e}")
        return StandardResponse.error(
            message=f"图像编辑失败: {str(e)}",
            code=500,
            request_id=getattr(request, 'request_id', None)
        )
