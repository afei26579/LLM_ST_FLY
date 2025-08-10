from rest_framework import viewsets, status, permissions, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from django.contrib.auth import login, logout
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.contrib.auth.models import Group
from rest_framework_simplejwt.tokens import RefreshToken

from core.response import StandardResponse
from .models import User, Role
from .serializers import (
    UserSerializer, UserCreateSerializer, UserUpdateSerializer,
    RoleSerializer, PasswordChangeSerializer, LoginSerializer
)

# 临时导入，需要根据实际项目调整
try:
    from .serializers import UserListSerializer, GroupSerializer
except ImportError:
    # 如果没有这些序列化器，使用基础的
    UserListSerializer = UserSerializer
    GroupSerializer = UserSerializer

try:
    from .permissions import IsAdminUser
except ImportError:
    # 如果没有自定义权限类，使用Django内置的
    IsAdminUser = permissions.IsAdminUser


class RoleViewSet(viewsets.ModelViewSet):
    """角色管理视图集"""
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_system']
    search_fields = ['code', 'name', 'description']
    ordering_fields = ['created_at', 'name', 'code']
    ordering = ['created_at']
    
    def get_permissions(self):
        """根据操作类型设置权限"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            # 只有管理员可以修改角色
            permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
        else:
            # 所有认证用户都可以查看角色
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def destroy(self, request, *args, **kwargs):
        """删除角色"""
        role = self.get_object()
        if role.is_system:
            return StandardResponse.error(
                message='系统角色不能删除',
                code=400,
                request_id=getattr(request, 'request_id', None)
            )
        if role.users.exists():
            return StandardResponse.error(
                message='该角色下还有用户，不能删除',
                code=400,
                request_id=getattr(request, 'request_id', None)
            )
        
        # 执行删除操作
        role.delete()
        return StandardResponse.success(
            message='角色删除成功',
            request_id=getattr(request, 'request_id', None)
        )
    
    @action(detail=True, methods=['get'])
    def users(self, request, pk=None):
        """获取角色下的用户列表"""
        role = self.get_object()
        users = role.users.all()
        return StandardResponse.paginated_success(
            users,
            UserSerializer,
            message='获取角色用户列表成功',
            request_id=getattr(request, 'request_id', None),
            context={'request': request}
        )


class UserViewSet(viewsets.ModelViewSet):
    """用户管理视图集"""
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['user_role', 'is_active', 'is_staff']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'phone']
    ordering_fields = ['date_joined', 'username', 'email']
    ordering = ['-date_joined']
    
    def get_serializer_class(self):
        """根据操作类型返回不同的序列化器"""
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserSerializer
    
    def get_permissions(self):
        """根据操作类型设置权限"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            # 只有管理员可以管理用户
            permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
        elif self.action == 'me':
            # 获取当前用户信息只需要认证
            permission_classes = [permissions.IsAuthenticated]
        else:
            # 查看用户列表需要管理员权限
            permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
        return [permission() for permission in permission_classes]
    
    @action(detail=False, methods=['get', 'put', 'patch'])
    def me(self, request):
        """获取或更新当前用户信息"""
        if request.method == 'GET':
            return StandardResponse.single_success(
                request.user,
                UserSerializer,
                message='获取用户信息成功',
                request_id=getattr(request, 'request_id', None),
                context={'request': request}
            )
        else:
            serializer = UserUpdateSerializer(
                request.user, 
                data=request.data, 
                partial=request.method == 'PATCH'
            )
            if serializer.is_valid():
                serializer.save()
                return StandardResponse.single_success(
                    request.user,
                    UserSerializer,
                    message='用户信息更新成功',
                    request_id=getattr(request, 'request_id', None),
                    context={'request': request}
                )
            return StandardResponse.error(
                message='数据验证失败',
                code=400,
                data=serializer.errors,
                request_id=getattr(request, 'request_id', None)
            )
    
    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """修改密码"""
        serializer = PasswordChangeSerializer(
            data=request.data, 
            context={'request': request}
        )
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return StandardResponse.success(
                message='密码修改成功',
                request_id=getattr(request, 'request_id', None)
            )
        return StandardResponse.error(
            message='密码修改失败',
            code=400,
            data=serializer.errors,
            request_id=getattr(request, 'request_id', None)
        )
    
    @action(detail=True, methods=['post'])
    def reset_password(self, request, pk=None):
        """重置用户密码（管理员操作）"""
        user = self.get_object()
        new_password = request.data.get('new_password')
        if not new_password:
            return StandardResponse.error(
                message='请提供新密码',
                code=400,
                request_id=getattr(request, 'request_id', None)
            )
        
        user.set_password(new_password)
        user.save()
        return StandardResponse.success(
            message='密码重置成功',
            request_id=getattr(request, 'request_id', None)
        )
    
    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """切换用户激活状态"""
        user = self.get_object()
        user.is_active = not user.is_active
        user.save()
        
        serializer = self.get_serializer(user)
        return StandardResponse.success(
            data=serializer.data,
            message=f'用户已{"激活" if user.is_active else "禁用"}',
            request_id=getattr(request, 'request_id', None)
        )


class AuthViewSet(viewsets.ViewSet):
    """认证相关视图集"""
    permission_classes = [permissions.AllowAny]
    
    @action(detail=False, methods=['post'])
    def login(self, request):
        """用户登录"""
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            login(request, user)
            
            # 创建或获取token
            token, created = Token.objects.get_or_create(user=user)
            
            return StandardResponse.success(
                data={
                    'token': token.key,
                    'user': UserSerializer(user).data
                },
                message='登录成功',
                request_id=getattr(request, 'request_id', None)
            )
        return StandardResponse.error(
            message='登录失败',
            code=400,
            data=serializer.errors,
            request_id=getattr(request, 'request_id', None)
        )
    
    @action(detail=False, methods=['post'])
    def logout(self, request):
        """用户登出"""
        if request.user.is_authenticated:
            # 删除token
            try:
                token = Token.objects.get(user=request.user)
                token.delete()
            except Token.DoesNotExist:
                pass
            
            logout(request)
            return StandardResponse.success(
                message='登出成功',
                request_id=getattr(request, 'request_id', None)
            )
        return StandardResponse.error(
            message='用户未登录',
            code=400,
            request_id=getattr(request, 'request_id', None)
        )
    
    @action(detail=False, methods=['get'])
    def check(self, request):
        """检查登录状态"""
        if request.user.is_authenticated:
            return StandardResponse.success(
                data={
                    'authenticated': True,
                    'user': UserSerializer(request.user).data
                },
                message='用户已登录',
                request_id=getattr(request, 'request_id', None)
            )
        return StandardResponse.success(
            data={'authenticated': False},
            message='用户未登录',
            request_id=getattr(request, 'request_id', None)
        )


class LoginView(APIView):
    """用户登录视图"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            login(request, user)
            
            # 创建JWT令牌
            refresh = RefreshToken.for_user(user)
            
            return StandardResponse.success(
                data={
                    'user': UserSerializer(user).data,
                    'token': {
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                    }
                },
                message='登录成功',
                request_id=getattr(request, 'request_id', None)
            )
        return StandardResponse.error(
            message='登录失败',
            code=400,
            data=serializer.errors,
            request_id=getattr(request, 'request_id', None)
        )


class RegisterView(generics.CreateAPIView):
    """用户注册视图"""
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # 创建JWT令牌
            refresh = RefreshToken.for_user(user)
            
            return StandardResponse.success(
                data={
                    'user': UserSerializer(user).data,
                    'token': {
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                    }
                },
                message='注册成功',
                code=201,
                request_id=getattr(request, 'request_id', None)
            )
        return StandardResponse.error(
            message='注册失败',
            code=400,
            data=serializer.errors,
            request_id=getattr(request, 'request_id', None)
        )


class UserManagementViewSet(viewsets.ModelViewSet):
    """用户管理视图集"""
    queryset = User.objects.all().order_by('-date_joined')
    permission_classes = [IsAdminUser]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserListSerializer
    
    @action(detail=True, methods=['patch'])
    def status(self, request, pk=None):
        """更新用户状态"""
        user = self.get_object()
        is_active = request.data.get('is_active')
        
        if is_active is None:
            return StandardResponse.error(
                message='请提供is_active字段',
                code=400,
                request_id=getattr(request, 'request_id', None)
            )
        
        user.is_active = is_active
        user.save()
        
        serializer = self.get_serializer(user)
        return StandardResponse.success(
            data=serializer.data,
            message=f'用户已{"激活" if user.is_active else "禁用"}',
            request_id=getattr(request, 'request_id', None)
        )


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    """用户组视图集"""
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsAdminUser]
