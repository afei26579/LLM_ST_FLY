from django.shortcuts import render
from django.contrib.auth import get_user_model
from rest_framework import status, viewsets, generics, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView

from .serializers import (
    UserSerializer, UserProfileSerializer, LoginSerializer,
    GroupSerializer, UserGroupSerializer
)
from .permissions import IsAdminUser, IsStaffOrAdmin, IsSelfOrAdmin

User = get_user_model()


class LoginView(APIView):
    """
    用户登录视图
    """
    permission_classes = [permissions.AllowAny]  # 登录不需要认证
    serializer_class = LoginSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                          context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        
        # 创建JWT令牌
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'token': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        })


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
    
    @action(detail=False, methods=['get'], url_path='me')
    def me(self, request):
        """
        获取当前用户信息
        """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['put', 'patch'], url_path='me')
    def update_me(self, request):
        """
        更新当前用户资料
        """
        serializer = UserProfileSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
        
        return Response({
            'user': UserSerializer(user).data,
            'token': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)
