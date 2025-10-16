"""
描述编辑视图
处理基于描述的图片修改请求
"""
import logging
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from core.response import StandardResponse
from .prompt_edit_service import prompt_edit_service

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def edit_by_prompt(request: Request) -> Response:
    """
    描述修改
    
    使用 qwen-image-edit 模型根据描述修改图片
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
                message="缺少修改描述",
                code=400
            )
        
        logger.info(f"用户 {request.user.id} 开始描述修改，描述: {prompt[:50]}...")
        
        # 调用描述编辑服务
        result = prompt_edit_service.edit_by_prompt(
            image_base64=image_url,
            prompt=prompt,
            user_id=request.user.id
        )
        
        return StandardResponse.success(
            data=result,
            message="图片修改成功"
        )
        
    except ValueError as e:
        logger.error(f"参数错误: {str(e)}")
        return StandardResponse.error(
            message=str(e),
            code=400
        )
    except Exception as e:
        logger.error(f"描述修改失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return StandardResponse.error(
            message=f"图片修改失败: {str(e)}",
            code=500
        )

