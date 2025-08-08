from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
from django.core.exceptions import PermissionDenied, ValidationError
from rest_framework.exceptions import (
    AuthenticationFailed,
    NotAuthenticated,
    PermissionDenied as DRFPermissionDenied,
    ValidationError as DRFValidationError,
    NotFound,
    MethodNotAllowed,
    ParseError,
    Throttled
)
from .response import StandardResponse
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """自定义异常处理器"""
    
    # 获取request_id
    request = context.get('request')
    request_id = getattr(request, 'request_id', None) if request else None
    
    # 记录异常日志
    logger.error(f"API异常: {exc}", exc_info=True, extra={
        'request_id': request_id,
        'view': context.get('view'),
        'request': request
    })
    
    # DRF默认异常处理
    response = exception_handler(exc, context)
    
    if response is not None:
        # DRF异常
        custom_response_data = _handle_drf_exception(exc, response, request_id)
    else:
        # Django异常或自定义异常
        custom_response_data = _handle_django_exception(exc, request_id)
    
    return custom_response_data


def _handle_drf_exception(exc, response, request_id):
    """处理DRF异常"""
    
    if isinstance(exc, NotAuthenticated):
        return StandardResponse.error(
            message="未认证，请先登录",
            code=401,
            request_id=request_id,
            http_status=status.HTTP_401_UNAUTHORIZED
        )
    
    elif isinstance(exc, (DRFPermissionDenied, PermissionDenied)):
        return StandardResponse.error(
            message="权限不足",
            code=403,
            request_id=request_id,
            http_status=status.HTTP_403_FORBIDDEN
        )
    
    elif isinstance(exc, NotFound):
        return StandardResponse.error(
            message="资源不存在",
            code=404,
            request_id=request_id,
            http_status=status.HTTP_404_NOT_FOUND
        )
    
    elif isinstance(exc, MethodNotAllowed):
        return StandardResponse.error(
            message="请求方法不允许",
            code=405,
            data={"allowed_methods": exc.detail.get('allowed_methods', [])},
            request_id=request_id,
            http_status=status.HTTP_405_METHOD_NOT_ALLOWED
        )
    
    elif isinstance(exc, DRFValidationError):
        # 处理验证错误
        errors = {}
        if hasattr(exc, 'detail'):
            if isinstance(exc.detail, dict):
                for field, messages in exc.detail.items():
                    if isinstance(messages, list):
                        errors[field] = [str(msg) for msg in messages]
                    else:
                        errors[field] = [str(messages)]
            elif isinstance(exc.detail, list):
                errors['non_field_errors'] = [str(msg) for msg in exc.detail]
            else:
                errors['detail'] = [str(exc.detail)]
        
        return StandardResponse.error(
            message="参数验证失败",
            code=400,
            data={"errors": errors},
            request_id=request_id,
            http_status=status.HTTP_400_BAD_REQUEST
        )
    
    elif isinstance(exc, ParseError):
        return StandardResponse.error(
            message="请求数据解析错误",
            code=400,
            request_id=request_id,
            http_status=status.HTTP_400_BAD_REQUEST
        )
    
    elif isinstance(exc, Throttled):
        return StandardResponse.error(
            message=f"请求过于频繁，请在{exc.wait}秒后重试",
            code=429,
            request_id=request_id,
            http_status=status.HTTP_429_TOO_MANY_REQUESTS
        )
    
    else:
        # 其他DRF异常
        message = "请求处理失败"
        if hasattr(exc, 'detail'):
            if isinstance(exc.detail, str):
                message = exc.detail
            elif isinstance(exc.detail, dict):
                message = str(exc.detail)
        
        return StandardResponse.error(
            message=message,
            code=response.status_code,
            request_id=request_id,
            http_status=response.status_code
        )


def _handle_django_exception(exc, request_id):
    """处理Django异常"""
    
    if isinstance(exc, Http404):
        return StandardResponse.error(
            message="资源不存在",
            code=404,
            request_id=request_id,
            http_status=status.HTTP_404_NOT_FOUND
        )
    
    elif isinstance(exc, PermissionDenied):
        return StandardResponse.error(
            message="权限不足",
            code=403,
            request_id=request_id,
            http_status=status.HTTP_403_FORBIDDEN
        )
    
    elif isinstance(exc, ValidationError):
        return StandardResponse.error(
            message="数据验证失败",
            code=400,
            data={"errors": exc.message_dict if hasattr(exc, 'message_dict') else str(exc)},
            request_id=request_id,
            http_status=status.HTTP_400_BAD_REQUEST
        )
    
    else:
        # 未知异常
        return StandardResponse.error(
            message="服务器内部错误",
            code=500,
            request_id=request_id,
            http_status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )