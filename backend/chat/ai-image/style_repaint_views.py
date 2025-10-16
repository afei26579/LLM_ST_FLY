"""
图像风格重绘视图
处理风格转换请求
"""
import logging
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from core.response import StandardResponse
from .style_repaint_service import style_repaint_service

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def style_repaint(request: Request) -> Response:
    """
    图像风格重绘
    
    使用 wanx-style-repaint-v1 模型进行风格转换
    """
    try:
        data = request.data
        image_url = data.get('image_url')
        style_index = data.get('style_index')
        
        if not image_url:
            return StandardResponse.error(
                message="缺少 image_url 参数",
                code=400
            )
        
        if style_index is None:
            return StandardResponse.error(
                message="缺少 style_index 参数",
                code=400
            )
        
        # 验证 style_index 范围
        if not isinstance(style_index, int) or style_index < 0 or style_index > 40:
            return StandardResponse.error(
                message="style_index 必须是 0-40 之间的整数",
                code=400
            )
        
        logger.info(f"用户 {request.user.id} 开始风格重绘，风格索引: {style_index}")
        
        # 调用风格重绘服务
        result = style_repaint_service.repaint_style(
            image_url=image_url,
            style_index=style_index,
            user_id=request.user.id
        )
        
        return StandardResponse.success(
            data=result,
            message="风格转换成功"
        )
        
    except ValueError as e:
        logger.error(f"参数错误: {str(e)}")
        return StandardResponse.error(
            message=str(e),
            code=400
        )
    except Exception as e:
        logger.error(f"风格重绘失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return StandardResponse.error(
            message=f"风格转换失败: {str(e)}",
            code=500
        )

