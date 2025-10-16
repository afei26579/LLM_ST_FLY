"""
背景编辑视图
处理背景更换请求
"""
import logging
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from core.response import StandardResponse
from .background_edit_service import background_edit_service

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_background(request: Request) -> Response:
    """
    背景更换
    
    使用 qwen-image-edit 模型更换图片背景
    """
    try:
        data = request.data
        image_url = data.get('image_url')
        prompt = data.get('prompt')
        
        if not image_url:
            return StandardResponse.error(
                message="缺少 image_url 参数",
                code=400
            )
        
        if not prompt:
            return StandardResponse.error(
                message="缺少背景描述",
                code=400
            )
        
        logger.info(f"用户 {request.user.id} 开始更换背景，描述: {prompt[:50]}...")
        
        # 调用背景编辑服务
        result = background_edit_service.change_background(
            image_base64=image_url,
            prompt=prompt,
            user_id=request.user.id
        )
        
        return StandardResponse.success(
            data=result,
            message="背景更换成功"
        )
        
    except ValueError as e:
        logger.error(f"参数错误: {str(e)}")
        return StandardResponse.error(
            message=str(e),
            code=400
        )
    except Exception as e:
        logger.error(f"背景更换失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return StandardResponse.error(
            message=f"背景更换失败: {str(e)}",
            code=500
        )

