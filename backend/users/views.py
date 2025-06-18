from django.shortcuts import render
from django.contrib.auth import get_user_model
from rest_framework import status, viewsets, generics, permissions

from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, OpenApiResponse
from rest_framework import serializers

from .serializers import (
    UserSerializer, UserProfileSerializer, LoginSerializer,
    GroupSerializer, UserGroupSerializer
)
from .permissions import IsAdminUser, IsStaffOrAdmin, IsSelfOrAdmin

User = get_user_model()


# 自定义API响应类
class ApiResponse:
    """
    标准化API响应格式
    """
    @staticmethod
    def success(data=None, message="Success", status_code=200):
        """
        成功响应
        """
        return Response({
            "code": status_code,
            "message": message,
            "data": data
        }, status=status_code)
    
    @staticmethod
    def error(message="Error", status_code=400, data=None):
        """
        错误响应
        """
        return Response({
            "code": status_code,
            "message": message,
            "data": data
        }, status=status_code)


@extend_schema(
    tags=['认证'],
    description='用户登录API',
    responses={
        200: OpenApiResponse(description='登录成功，返回用户信息和JWT令牌'),
        400: OpenApiResponse(description='请求参数错误，缺少必要字段'),
        401: OpenApiResponse(description='认证失败，账号或密码错误'),
    },
    examples=[
        OpenApiExample(
            'Login Example',
            value={
                'username': 'admin',
                'password': 'password123'
            },
            request_only=True,
        ),
        OpenApiExample(
            'Success Response Example',
            value={
                'user': {
                    'id': 1,
                    'username': 'admin',
                    'email': 'admin@example.com',
                    'role': 'admin'
                },
                'token': {
                    'refresh': 'eyJ0eXAiO...', 
                    'access': 'eyJ0eXAiO...'
                }
            },
            response_only=True,
        )
    ]
)
class LoginView(APIView):
    """
    用户登录视图
    """
    permission_classes = [permissions.AllowAny]  # 登录不需要认证
    serializer_class = LoginSerializer
    
    def post(self, request, *args, **kwargs):
        try:
            serializer = self.serializer_class(data=request.data,
                                            context={'request': request})
            serializer.is_valid(raise_exception=True)
            user = serializer.validated_data['user']
            
            # 创建JWT令牌
            refresh = RefreshToken.for_user(user)
            
            return ApiResponse.success({
                'user': UserSerializer(user).data,
                'token': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, "登录成功")
        except serializers.ValidationError as e:
            # 区分不同类型的错误
            if 'param_error' in e.detail:
                # 参数错误返回400
                return ApiResponse.error(
                    e.detail['param_error'], 
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            elif 'auth_error' in e.detail:
                # 认证错误返回401
                return ApiResponse.error(
                    e.detail['auth_error'], 
                    status_code=status.HTTP_401_UNAUTHORIZED
                )
            # 其他验证错误
            return ApiResponse.error(
                '登录失败', 
                status_code=status.HTTP_400_BAD_REQUEST,
                data={'errors': e.detail}
            )


@extend_schema(tags=['用户管理'])
class UserViewSet(viewsets.ModelViewSet):
    """
    用户管理视图集
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def get_permissions(self):
        """
        根据不同的操作返回不同的权限
        """
      
        if self.action == 'create':
            permission_classes = [IsAdminUser]  # 只有管理员可以创建用户
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser|IsSelfOrAdmin]  # 管理员或自己可以修改/删除
        elif self.action in ['list']:
            permission_classes = [IsStaffOrAdmin]  # 管理员或工作人员可以查看用户列表
        else:
            permission_classes = [permissions.IsAuthenticated]
        
        return [permission() for permission in permission_classes]
    
    def get_serializer_class(self):
        """
        根据不同的操作返回不同的序列化器
        """
        if self.action == 'me':
            return UserProfileSerializer
        return self.serializer_class
    
    @extend_schema(
        summary="获取或更新当前用户信息",
        description="GET: 返回当前登录用户的详细信息; PUT/PATCH: 更新当前用户信息",
        responses={
            200: UserProfileSerializer,
            400: OpenApiResponse(description="更新失败，提供的信息无效")
        }
    )
    @action(detail=False, methods=['get', 'put', 'patch'], url_path='me')
    def me(self, request):
        """
        获取或更新当前用户信息
        """
        print("="*50)
        print(f"请求方法: {request.method}")
        print(f"请求用户: {request.user}")
        print(f"请求路径: {request.path}")
        
        if request.method == 'GET':
            # 获取用户信息
            serializer = self.get_serializer(request.user)
            return ApiResponse.success(serializer.data)
        
        elif request.method in ['PUT', 'PATCH']:
            # 更新用户信息
            print(f"请求数据: {request.data}")
            print(f"请求文件: {request.FILES}")
            serializer = UserProfileSerializer(
                request.user,
                data=request.data,
                partial=request.method == 'PATCH',
                context={'request': request}
            )
            if serializer.is_valid():
                serializer.save()
                return ApiResponse.success(serializer.data, "用户信息更新成功")
            print(f"序列化器错误: {serializer.errors}")
            return ApiResponse.error("用户信息更新失败", status_code=status.HTTP_400_BAD_REQUEST, data=serializer.errors)
        
        print("="*50)
    
    @extend_schema(
        summary="上传用户头像",
        description="上传用户头像图片",
        responses={
            200: UserProfileSerializer,
            400: OpenApiResponse(description="上传失败，提供的文件无效")
        }
    )
    @action(detail=False, methods=['post'], url_path='me/avatar')
    def upload_avatar(self, request):
        """
        上传用户头像
        """
        print("="*50)
        print(f"请求方法: {request.method}")
        print(f"请求用户: {request.user}")
        print(f"请求路径: {request.path}")
        print(f"请求文件: {request.FILES}")
        
        if 'avatar' not in request.FILES:
            return ApiResponse.error(
                '没有提供头像文件', 
                status_code=status.HTTP_400_BAD_REQUEST
            )
            
        # 获取上传的文件
        avatar_file = request.FILES['avatar']
        
        # 更新用户头像
        request.user.avatar = avatar_file
        request.user.save(update_fields=['avatar'])  # 只更新avatar字段
        
        # 返回更新后的用户信息
        serializer = UserProfileSerializer(request.user)
        return ApiResponse.success(serializer.data, "头像上传成功")


@extend_schema(
    tags=['认证'],
    description='用户注册API',
    responses={
        201: OpenApiResponse(description='注册成功，返回用户信息和JWT令牌'),
        400: OpenApiResponse(description='注册失败，提供的信息无效'),
    }
)
class RegisterView(generics.CreateAPIView):
    """
    用户注册视图
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]  # 注册不需要认证
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # 创建JWT令牌
        refresh = RefreshToken.for_user(user)
        
        return ApiResponse.success({
            'user': UserSerializer(user).data,
            'token': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, "注册成功", status_code=status.HTTP_201_CREATED)
