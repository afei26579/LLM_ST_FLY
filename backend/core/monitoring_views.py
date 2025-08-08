"""
响应格式监控视图
"""
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator
from .response import StandardResponse
from .monitoring import ResponseMonitor
from .validators import ResponseValidator


class ResponseStatsAPIView(APIView):
    """响应统计API视图"""
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get(self, request):
        """获取响应统计信息"""
        try:
            stats = ResponseMonitor.get_stats()
            return StandardResponse.success(
                data=stats,
                message="获取响应统计成功",
                request_id=getattr(request, 'request_id', None)
            )
        except Exception as e:
            return StandardResponse.error(
                message=f"获取响应统计失败: {str(e)}",
                code=500,
                request_id=getattr(request, 'request_id', None)
            )
    
    def delete(self, request):
        """重置响应统计"""
        try:
            ResponseMonitor.reset_stats()
            return StandardResponse.success(
                data=None,
                message="响应统计已重置",
                request_id=getattr(request, 'request_id', None)
            )
        except Exception as e:
            return StandardResponse.error(
                message=f"重置响应统计失败: {str(e)}",
                code=500,
                request_id=getattr(request, 'request_id', None)
            )


class ResponseHealthAPIView(APIView):
    """响应健康状态API视图"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """获取系统健康状态"""
        try:
            health_status = ResponseMonitor.get_health_status()
            return StandardResponse.success(
                data=health_status,
                message="获取健康状态成功",
                request_id=getattr(request, 'request_id', None)
            )
        except Exception as e:
            return StandardResponse.error(
                message=f"获取健康状态失败: {str(e)}",
                code=500,
                request_id=getattr(request, 'request_id', None)
            )


class ResponseValidationAPIView(APIView):
    """响应格式验证API视图"""
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def post(self, request):
        """验证响应格式"""
        try:
            response_data = request.data.get('response_data')
            if not response_data:
                return StandardResponse.error(
                    message="请提供要验证的响应数据",
                    code=400,
                    request_id=getattr(request, 'request_id', None)
                )
            
            # 验证基本格式
            basic_result = ResponseValidator.validate_response_format(response_data)
            
            # 如果是分页响应，进行分页验证
            is_paginated = (
                isinstance(response_data.get('data'), dict) and 
                'list' in response_data.get('data', {})
            )
            
            paginated_result = None
            if is_paginated:
                paginated_result = ResponseValidator.validate_paginated_response(response_data)
            
            result = {
                'basic_validation': basic_result,
                'is_paginated': is_paginated,
                'paginated_validation': paginated_result,
                'overall_valid': basic_result['is_valid'] and (
                    not is_paginated or (paginated_result and paginated_result['is_valid'])
                )
            }
            
            return StandardResponse.success(
                data=result,
                message="响应格式验证完成",
                request_id=getattr(request, 'request_id', None)
            )
            
        except Exception as e:
            return StandardResponse.error(
                message=f"验证响应格式失败: {str(e)}",
                code=500,
                request_id=getattr(request, 'request_id', None)
            )