import uuid
from datetime import datetime
from typing import Any, Dict, Optional, Union
from rest_framework.response import Response
from rest_framework import status
from django.core.paginator import Page
from rest_framework.pagination import PageNumberPagination


class StandardResponse:
    """统一响应格式工具类"""
    
    @staticmethod
    def success(
        data: Any = None,
        message: str = "操作成功",
        code: int = 200,
        request_id: Optional[str] = None
    ) -> Response:
        """成功响应"""
        return StandardResponse._build_response(
            code=code,
            message=message,
            data=data,
            request_id=request_id,
            http_status=status.HTTP_200_OK
        )
    
    @staticmethod
    def error(
        message: str = "操作失败",
        code: int = 400,
        data: Any = None,
        request_id: Optional[str] = None,
        http_status: int = None
    ) -> Response:
        """错误响应"""
        if http_status is None:
            # 根据业务状态码映射HTTP状态码
            http_status_map = {
                400: status.HTTP_400_BAD_REQUEST,
                401: status.HTTP_401_UNAUTHORIZED,
                403: status.HTTP_403_FORBIDDEN,
                404: status.HTTP_404_NOT_FOUND,
                500: status.HTTP_500_INTERNAL_SERVER_ERROR,
            }
            http_status = http_status_map.get(code, status.HTTP_400_BAD_REQUEST)
        
        return StandardResponse._build_response(
            code=code,
            message=message,
            data=data,
            request_id=request_id,
            http_status=http_status
        )
    
    @staticmethod
    def paginated_success(
        queryset_or_page,
        serializer_class,
        message: str = "获取数据成功",
        request_id: Optional[str] = None,
        context: Optional[Dict] = None
    ) -> Response:
        """分页成功响应"""
        if isinstance(queryset_or_page, Page):
            # Django Paginator
            page = queryset_or_page
            serializer = serializer_class(page.object_list, many=True, context=context)
            data = {
                "list": serializer.data,
                "total": page.paginator.count,
                "page": page.number,
                "page_size": page.paginator.per_page,
                "total_pages": page.paginator.num_pages,
                "has_next": page.has_next(),
                "has_previous": page.has_previous()
            }
        else:
            # DRF PageNumberPagination 或普通queryset
            if hasattr(queryset_or_page, 'data'):
                # 已经是分页后的数据
                data = queryset_or_page.data
            else:
                # 普通queryset，直接序列化
                serializer = serializer_class(queryset_or_page, many=True, context=context)
                data = {
                    "list": serializer.data,
                    "total": len(serializer.data)
                }
        
        return StandardResponse.success(
            data=data,
            message=message,
            request_id=request_id
        )
    
    @staticmethod
    def single_success(
        instance,
        serializer_class,
        message: str = "获取数据成功",
        request_id: Optional[str] = None,
        context: Optional[Dict] = None
    ) -> Response:
        """单个对象成功响应"""
        serializer = serializer_class(instance, context=context)
        return StandardResponse.success(
            data=serializer.data,
            message=message,
            request_id=request_id
        )
    
    @staticmethod
    def _build_response(
        code: int,
        message: str,
        data: Any,
        request_id: Optional[str],
        http_status: int
    ) -> Response:
        """构建响应"""
        response_data = {
            "code": code,
            "message": message,
            "data": data,
            "timestamp": datetime.now().isoformat(),
            "request_id": request_id or str(uuid.uuid4())
        }
        return Response(response_data, status=http_status)


class StandardPagination(PageNumberPagination):
    """标准分页器"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
    
    def get_paginated_response(self, data):
        """重写分页响应格式"""
        return StandardResponse.success(
            data={
                "list": data,
                "total": self.page.paginator.count,
                "page": self.page.number,
                "page_size": self.get_page_size(self.request),
                "total_pages": self.page.paginator.num_pages,
                "has_next": self.page.has_next(),
                "has_previous": self.page.has_previous()
            },
            message="获取数据成功"
        )