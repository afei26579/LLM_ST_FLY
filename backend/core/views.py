from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .response import StandardResponse, StandardPagination


class StandardAPIView(APIView):
    """标准化的APIView基类"""
    
    def get_request_id(self):
        """获取请求ID"""
        return getattr(self.request, 'request_id', None)
    
    def handle_exception(self, exc):
        """统一异常处理"""
        response = super().handle_exception(exc)
        return response


class StandardModelViewSet(ModelViewSet):
    """标准化的ModelViewSet"""
    pagination_class = StandardPagination
    
    def get_request_id(self):
        """获取请求ID"""
        return getattr(self.request, 'request_id', None)
    
    def list(self, request, *args, **kwargs):
        """列表视图"""
        queryset = self.filter_queryset(self.get_queryset())
        
        # 检查是否需要分页
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        # 不分页的情况
        serializer = self.get_serializer(queryset, many=True)
        return StandardResponse.success(
            data={
                "list": serializer.data,
                "total": len(serializer.data)
            },
            message="获取列表成功",
            request_id=self.get_request_id()
        )
    
    def retrieve(self, request, *args, **kwargs):
        """详情视图"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return StandardResponse.success(
            data=serializer.data,
            message="获取详情成功",
            request_id=self.get_request_id()
        )
    
    def create(self, request, *args, **kwargs):
        """创建视图"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        
        return StandardResponse.success(
            data=self.get_serializer(instance).data,
            message="创建成功",
            code=201,
            request_id=self.get_request_id()
        )
    
    def update(self, request, *args, **kwargs):
        """更新视图"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        
        return StandardResponse.success(
            data=serializer.data,
            message="更新成功",
            request_id=self.get_request_id()
        )
    
    def destroy(self, request, *args, **kwargs):
        """删除视图"""
        instance = self.get_object()
        instance.delete()
        return StandardResponse.success(
            data=None,
            message="删除成功",
            request_id=self.get_request_id()
        )


class StandardListAPIView(generics.ListAPIView):
    """标准化的列表视图"""
    pagination_class = StandardPagination
    
    def get_request_id(self):
        return getattr(self.request, 'request_id', None)
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return StandardResponse.success(
            data={
                "list": serializer.data,
                "total": len(serializer.data)
            },
            message="获取列表成功",
            request_id=self.get_request_id()
        )


class StandardRetrieveAPIView(generics.RetrieveAPIView):
    """标准化的详情视图"""
    
    def get_request_id(self):
        return getattr(self.request, 'request_id', None)
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return StandardResponse.success(
            data=serializer.data,
            message="获取详情成功",
            request_id=self.get_request_id()
        )


class StandardCreateAPIView(generics.CreateAPIView):
    """标准化的创建视图"""
    
    def get_request_id(self):
        return getattr(self.request, 'request_id', None)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        
        return StandardResponse.success(
            data=self.get_serializer(instance).data,
            message="创建成功",
            code=201,
            request_id=self.get_request_id()
        )


class StandardUpdateAPIView(generics.UpdateAPIView):
    """标准化的更新视图"""
    
    def get_request_id(self):
        return getattr(self.request, 'request_id', None)
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        
        return StandardResponse.success(
            data=serializer.data,
            message="更新成功",
            request_id=self.get_request_id()
        )


class StandardDestroyAPIView(generics.DestroyAPIView):
    """标准化的删除视图"""
    
    def get_request_id(self):
        return getattr(self.request, 'request_id', None)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return StandardResponse.success(
            data=None,
            message="删除成功",
            request_id=self.get_request_id()
        )