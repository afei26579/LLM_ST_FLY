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
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, OpenApiResponse
import random
import string
from django.core.mail import send_mail
from django.conf import settings
from django.core.cache import cache
from django.template.loader import render_to_string

from core.response import StandardResponse
from .models import User, Role
from .serializers import (
    UserSerializer, UserCreateSerializer, UserUpdateSerializer,
    RoleSerializer, PasswordChangeSerializer, LoginSerializer,
    SendSmsCodeSerializer, BindPhoneSerializer, BindEmailSerializer,
    ResetPasswordPhoneSerializer
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
                    message="邮件发送失败，请稍后重试",
                    code=500,
                    request_id=getattr(request, 'request_id', None)
                )
        
        return StandardResponse.error(
            message="邮件发送失败",
            code=400,
            data=serializer.errors,
            request_id=getattr(request, 'request_id', None)
        )
    
    @extend_schema(
        summary="验证邮箱绑定",
        description="验证邮箱绑定激活链接",
        responses={
            200: OpenApiResponse(description="邮箱绑定成功"),
            400: OpenApiResponse(description="验证失败，链接无效或已过期")
        }
    )
    @action(detail=False, methods=['get'], url_path='verify-email', permission_classes=[permissions.AllowAny])
    def verify_email_bind(self, request):
        """验证邮箱绑定"""
        token = request.query_params.get('token')
        email = request.query_params.get('email')
        
        if not token or not email:
            return StandardResponse.error(
                message="无效的验证链接",
                code=400,
                request_id=getattr(request, 'request_id', None)
            )
        
        # 从缓存获取绑定信息
        cache_key = f"email_bind_{email}"
        cache_data = cache.get(cache_key)
        
        if not cache_data:
            return StandardResponse.error(
                message="验证链接已过期或无效",
                code=400,
                request_id=getattr(request, 'request_id', None)
            )
        
        try:
            # 获取用户
            user = User.objects.get(id=cache_data['user_id'])
            
            # 更新邮箱
            user.email = email
            user.save(update_fields=['email'])
            
            # 清除缓存
            cache.delete(cache_key)
            
            return StandardResponse.success(
                message="邮箱绑定成功",
                request_id=getattr(request, 'request_id', None)
            )
        except User.DoesNotExist:
            return StandardResponse.error(
                message="用户不存在",
                code=404,
                request_id=getattr(request, 'request_id', None)
            )
        except Exception as e:
            print(f"邮箱绑定失败: {str(e)}")
            return StandardResponse.error(
                message="邮箱绑定失败，请稍后重试",
                code=500,
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
                message="验证码发送失败",
                code=400,
                data=serializer.errors,
                request_id=getattr(request, 'request_id', None)
            )

    def _generate_code(self, length=6):
        """生成数字验证码"""
        return ''.join(random.choices(string.digits, k=length))

    @extend_schema(
        summary="发送手机验证码",
        description="发送手机验证码用于绑定手机号或重置密码",
        responses={
            200: OpenApiResponse(description="验证码发送成功"),
            400: OpenApiResponse(description="验证码发送失败，提供的信息无效")
        }
    )
    @action(detail=False, methods=['post'], url_path='send-sms-code', permission_classes=[permissions.AllowAny])
    def send_sms_code(self, request):
        """
        发送手机验证码
        """
        serializer = SendSmsCodeSerializer(data=request.data)
        
        if serializer.is_valid():
            phone = serializer.validated_data['phone']
            # 获取验证码用途，默认为绑定手机号
            purpose = serializer.validated_data.get('purpose', 'binding')
            print(purpose, "="*50)
            # 如果是重置密码，需要检查手机号是否已注册
            if purpose == 'reset':
                user_exists = User.objects.filter(phone=phone).exists()
                if not user_exists:
                    return StandardResponse.error(
                        "该手机号未注册", 
                        code=404,
                        data={
                            'field': 'phone',
                            'message': "该手机号未注册，无法重置密码"
                        },
                        request_id=getattr(request, 'request_id', None)
                    )
            # 如果是绑定手机号，则不需要检查手机号是否已注册
            # 管理员账号可以自由绑定任何手机号，普通账号需要验证该手机号没被其他账号使用
            elif purpose == 'binding' and not request.user.is_staff:
                # 检查该手机号是否已被其他账户绑定
                if User.objects.filter(phone=phone).exclude(id=request.user.id if request.user.is_authenticated else -1).exists():
                    return StandardResponse.error(
                        "该手机号已被其他账户绑定", 
                        code=400,
                        data={
                            'field': 'phone',
                            'message': "该手机号已被其他账户绑定，请使用其他手机号"
                        },
                        request_id=getattr(request, 'request_id', None)
                    )
            
            # 生成验证码
            code = self._generate_code()
            
            # 将验证码存入缓存(使用Django缓存系统)
            # 设置过期时间为10分钟
            cache_key = f"sms_code_{phone}"
            cache.set(cache_key, code, 60 * 10)
            
            # TODO: 实际发送短信的代码
            # t_client = Twilio_client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
            # SMS_LABEL = "【白杨】"
            # message = t_client.messages.create(
            #     body=f"{SMS_LABEL}你好，验证码是：{code}。用于{purpose}，请勿泄露给他人。",  # 短信内容
            #     from_=TWILIO_PHONE_NUMBER,     # 你的 Twilio 号码
            #     to=phone                       # 接收方手机号
            # )
            # 这里模拟发送短信，实际项目中应该调用短信发送API
            print(f"向 {phone} 发送验证码: {code}, 用途: {purpose}")
            code_data = {"sms_code": code, "purpose": purpose}
            return StandardResponse.success(code_data, "验证码发送成功，有效期10分钟")
        
        return StandardResponse.error(
            "验证码发送失败", 
            status_code=status.HTTP_400_BAD_REQUEST,
            data={
                'field': 'phone',
                'message': serializer.errors['phone'][0] if 'phone' in serializer.errors else "手机号验证失败"
            }
        )

    @extend_schema(
        summary="发送邮箱验证码",
        description="发送邮箱验证码用于重置密码",
        responses={
            200: OpenApiResponse(description="验证码发送成功"),
            400: OpenApiResponse(description="验证码发送失败，提供的信息无效")
        }
    )
    @action(detail=False, methods=['post'], url_path='send-email-code', permission_classes=[permissions.AllowAny])
    def send_email_code(self, request):
        """发送邮箱验证码"""
        if not SendEmailCodeSerializer:
            return StandardResponse.error(
                message='邮箱验证功能未启用',
                code=501,
                request_id=getattr(request, 'request_id', None)
            )
            
        serializer = SendEmailCodeSerializer(data=request.data)
        
        if serializer.is_valid():
            email = serializer.validated_data['email']
            
            # 生成验证码
            code = self._generate_code()
            
            # 将验证码存入缓存，设置过期时间为10分钟
            cache_key = f"email_code_{email}"
            cache.set(cache_key, code, 60 * 10)
            
            # 发送邮件
            try:
                send_mail(
                    subject='密码重置验证码',
                    message=f'您的密码重置验证码是：{code}，有效期10分钟。',
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[email],
                    fail_silently=False,
                )
                return StandardResponse.success(
                    message="验证码已发送到您的邮箱，有效期10分钟",
                    request_id=getattr(request, 'request_id', None)
                )
            except Exception as e:
                print(f"邮件发送失败: {str(e)}")
                return StandardResponse.error(
                    message="验证码发送失败，请稍后重试",
                    code=500,
                    request_id=getattr(request, 'request_id', None)
                )
        
        return StandardResponse.error(
            message="验证码发送失败",
            code=400,
            data=serializer.errors,
            request_id=getattr(request, 'request_id', None)
        )
    
    @extend_schema(
        summary="通过手机重置密码",
        description="通过手机号和验证码重置密码",
        responses={
            200: OpenApiResponse(description="密码重置成功"),
            400: OpenApiResponse(description="密码重置失败，提供的信息无效")
        }
    )
    @action(detail=False, methods=['post'], url_path='reset-password-phone', permission_classes=[permissions.AllowAny])
    def reset_password_phone(self, request):
        """通过手机重置密码"""
        if not ResetPasswordPhoneSerializer:
            return StandardResponse.error(
                message='手机重置密码功能未启用',
                code=501,
                request_id=getattr(request, 'request_id', None)
            )
            
        serializer = ResetPasswordPhoneSerializer(data=request.data)
        
        if serializer.is_valid():
           
            phone = serializer.validated_data['phone']
            code = serializer.validated_data['code']
            new_password = serializer.validated_data['newPassword']
            
            # 验证码校验
            cache_key = f"sms_code_{phone}"
            cached_code = cache.get(cache_key)
            
            if not cached_code or cached_code != code:
                return StandardResponse.error(
                    message="验证码错误或已过期",
                    code=400,
                    data={
                        'field': 'phoneCode',
                        'message': "验证码错误或已过期"
                    },
                    request_id=getattr(request, 'request_id', None)
                )
            
            # 更新密码
            try:
                user = User.objects.get(phone=phone)
                try:
                    user.set_password(new_password)
                except Exception as e:
                    print(e)
                    return StandardResponse.error(
                        message="用户不存在",
                        code=404,
                        request_id=getattr(request, 'request_id', None)
                    )
                user.save(update_fields=['password'])
                
                # 清除缓存中的验证码
                cache.delete(cache_key)
                
                return StandardResponse.success(
                    message="密码重置成功",
                    request_id=getattr(request, 'request_id', None)
                )
            except User.DoesNotExist:
                return StandardResponse.error(
                    message="用户不存在",
                    code=404,
                    request_id=getattr(request, 'request_id', None)
                )
        
        return StandardResponse.error(
            message="密码重置失败",
            code=400,
            data=serializer.errors,
            request_id=getattr(request, 'request_id', None)
        )
    

    @extend_schema(
        summary="发送邮箱绑定链接",
        description="发送邮箱绑定激活链接",
        responses={
            200: OpenApiResponse(description="激活链接发送成功"),
            400: OpenApiResponse(description="发送失败，提供的信息无效")
        }
    )
    @action(detail=False, methods=['post'], url_path='send-email-bind', permission_classes=[permissions.AllowAny])
    def send_email_bind(self, request):
        """
        发送邮箱绑定激活链接
        """
        serializer = BindEmailSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            email = serializer.validated_data['email']
            
            # 检查该邮箱是否已被其他账户绑定
            if User.objects.filter(email=email).exclude(id=request.user.id).exists():
                return StandardResponse.error(
                    "该邮箱已被其他账户绑定", 
                    status_code=status.HTTP_400_BAD_REQUEST,
                    data={
                        'field': 'email',
                        'message': "该邮箱已被其他账户绑定，请使用其他邮箱"
                    }
                )
            
            # 生成验证令牌（简单实现，实际项目中应该使用更安全的方法）
            # 例如使用Django内置的default_token_generator
            import uuid
            import base64
            token = base64.urlsafe_b64encode(uuid.uuid4().bytes).decode('utf-8').rstrip('=')
            
            # 将令牌存入缓存，设置过期时间为24小时
            cache_key = f"email_bind_{email}"
            cache_data = {
                'user_id': request.user.id,
                'email': email
            }
            cache.set(cache_key, cache_data, 60 * 60 * 24)
            
            # 构建激活链接
            # 实际项目中，这个URL应该是前端页面的URL，处理验证逻辑
            frontend_url = settings.FRONTEND_URL or 'http://localhost:5173'
            activate_url = f"{frontend_url}/verify-email?token={token}&email={email}&type=bind"
            
            # 发送邮件
            try:
                # 准备模板上下文
                context = {
                    'activate_url': activate_url
                }
                
                # 渲染HTML邮件内容
                html_message = render_to_string('emails/email_binding.html', context)
                
                # 纯文本邮件内容
                plain_message = f'请点击以下链接完成邮箱绑定：{activate_url}\n链接有效期为24小时。\n如果打不开链接，请复制链接在浏览器打开。'
                
                send_mail(
                    subject='绑定邮箱',
                    message=plain_message,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[email],
                    fail_silently=False,
                    html_message=html_message
                )
                return StandardResponse.success({
                    'activate_url': activate_url, # 仅开发环境返回，生产环境应该移除
                    'email': email,
                    'expires_in': '24小时'
                }, "激活链接已发送到您的邮箱，请查收并点击链接完成绑定")
            except Exception as e:
                print(f"邮件发送失败: {str(e)}")
                return StandardResponse.error(
                    "邮件发送失败，请稍后重试", 
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        # 序列化器验证失败
        field = next(iter(serializer.errors)) if serializer.errors else 'email'
        message = next(iter(serializer.errors.values()))[0] if serializer.errors else "邮箱验证失败"
        
        return StandardResponse.error(
            "邮件发送失败", 
            status_code=status.HTTP_400_BAD_REQUEST,
            data={
                'field': field,
                'message': message
            }
        )
    
    @extend_schema(
        summary="通过邮箱重置密码",
        description="通过邮箱和验证码重置密码",
        responses={
            200: OpenApiResponse(description="密码重置成功"),
            400: OpenApiResponse(description="密码重置失败，提供的信息无效")
        }
    )
    @action(detail=False, methods=['post'], url_path='reset-password-email', permission_classes=[permissions.AllowAny])
    def reset_password_email(self, request):
        """通过邮箱重置密码"""
        if not ResetPasswordEmailSerializer:
            return StandardResponse.error(
                message='邮箱重置密码功能未启用',
                code=501,
                request_id=getattr(request, 'request_id', None)
            )
            
        serializer = ResetPasswordEmailSerializer(data=request.data)
        
        if serializer.is_valid():
            email = serializer.validated_data['email']
            code = serializer.validated_data['code']
            new_password = serializer.validated_data['newPassword']
            
            # 验证码校验
            cache_key = f"email_code_{email}"
            cached_code = cache.get(cache_key)
            
            if not cached_code or cached_code != code:
                return StandardResponse.error(
                    message="验证码错误或已过期",
                    code=400,
                    data={
                        'field': 'emailCode',
                        'message': "验证码错误或已过期"
                    },
                    request_id=getattr(request, 'request_id', None)
                )
            
            # 更新密码
            try:
                user = User.objects.get(email=email)
                user.set_password(new_password)
                user.save(update_fields=['password'])
                
                # 清除缓存中的验证码
                cache.delete(cache_key)
                
                return StandardResponse.success(
                    message="密码重置成功",
                    request_id=getattr(request, 'request_id', None)
                )
            except User.DoesNotExist:
                return StandardResponse.error(
                    message="用户不存在",
                    code=404,
                    request_id=getattr(request, 'request_id', None)
                )
        
        return StandardResponse.error(
            message="密码重置失败",
            code=400,
            data=serializer.errors,
            request_id=getattr(request, 'request_id', None)
        )
    
    @extend_schema(
        summary="绑定手机号",
        description="通过验证码绑定或更换手机号",
        responses={
            200: OpenApiResponse(description="手机号绑定成功"),
            400: OpenApiResponse(description="绑定失败，提供的信息无效")
        }
    )
    @action(detail=False, methods=['post'], url_path='bind-phone')
    def bind_phone(self, request):
        """绑定手机号"""
        if not BindPhoneSerializer:
            return StandardResponse.error(
                message='手机号绑定功能未启用',
                code=501,
                request_id=getattr(request, 'request_id', None)
            )
            
        serializer = BindPhoneSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            phone = serializer.validated_data['phone']
            code = serializer.validated_data['code']
            
            # 验证码校验
            cache_key = f"sms_code_{phone}"
            cached_code = cache.get(cache_key)
            
            if not cached_code or cached_code != code:
                return StandardResponse.error(
                    message="验证码错误或已过期",
                    code=400,
                    data={
                        'field': 'code',
                        'message': "验证码错误或已过期"
                    },
                    request_id=getattr(request, 'request_id', None)
                )
            
            # 检查该手机号是否已被其他账户绑定
            if User.objects.filter(phone=phone).exclude(id=request.user.id).exists():
                return StandardResponse.error(
                    message="该手机号已被其他账户绑定",
                    code=400,
                    data={
                        'field': 'phone',
                        'message': "该手机号已被其他账户绑定，请使用其他手机号"
                    },
                    request_id=getattr(request, 'request_id', None)
                )
            
            # 绑定手机号
            request.user.phone = phone
            request.user.save(update_fields=['phone'])
            
            # 清除缓存中的验证码
            cache.delete(cache_key)
            
            # 返回更新后的用户信息
            return StandardResponse.single_success(
                request.user,
                UserSerializer,
                message="手机号绑定成功",
                request_id=getattr(request, 'request_id', None),
                context={'request': request}
            )
        
        return StandardResponse.error(
            message="手机号绑定失败",
            code=400,
            data=serializer.errors,
            request_id=getattr(request, 'request_id', None)
        )
    

    
    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """修改密码"""
        print("="*100, request.data)
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
