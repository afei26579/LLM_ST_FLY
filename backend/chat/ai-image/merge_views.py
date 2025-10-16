"""
图像融合视图
处理多图融合请求
"""
import logging
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from core.response import StandardResponse
from .merge_service import image_merge_service

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def merge_images(request: Request) -> Response:
    """
    多图融合
    
    接收1-3张图片和融合描述，生成融合后的图片
    """
    try:
        data = request.data
        messages = data.get('messages', [])
        
        if not messages or len(messages) == 0:
            return StandardResponse.error(
                message="缺少 messages 参数",
                code=400
            )
        
        # 提取第一个消息的内容
        message = messages[0]
        content = message.get('content', [])
        
        # 分离图片和文字
        images_base64 = []
        prompt = ""
        
        for item in content:
            if 'image' in item:
                images_base64.append(item['image'])
            elif 'text' in item:
                prompt = item['text']
        
        if len(images_base64) < 2:
            return StandardResponse.error(
                message="至少需要2张图片",
                code=400
            )
        
        if len(images_base64) > 3:
            return StandardResponse.error(
                message="最多支持3张图片",
                code=400
            )
        
        if not prompt:
            return StandardResponse.error(
                message="请提供融合描述",
                code=400
            )
        
        logger.info(f"用户 {request.user.id} 开始融合 {len(images_base64)} 张图片")
        
        # 调用融合服务
        result = image_merge_service.merge_images(
            images_base64=images_base64,
            prompt=prompt,
            user_id=request.user.id
        )
        
        return StandardResponse.success(
            data=result,
            message="图片融合成功"
        )
        
    except ValueError as e:
        logger.error(f"参数错误: {str(e)}")
        return StandardResponse.error(
            message=str(e),
            code=400
        )
    except Exception as e:
        logger.error(f"图片融合失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return StandardResponse.error(
            message=f"图片融合失败: {str(e)}",
            code=500
        )

