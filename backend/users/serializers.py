from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth.models import Group
from .models import User, Role


class RoleSerializer(serializers.ModelSerializer):
    """角色序列化器"""
    users_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Role
        fields = ['id', 'code', 'name', 'description', 'is_system', 
                 'created_at', 'updated_at', 'users_count']
        read_only_fields = ['id', 'created_at', 'updated_at', 'users_count']
    
    def get_users_count(self, obj):
        """获取该角色的用户数量"""
        return obj.users.count()
    
    def validate_code(self, value):
        """验证角色代码"""
        if self.instance and self.instance.is_system:
            # 系统角色不能修改代码
            if value != self.instance.code:
                raise serializers.ValidationError("系统角色的代码不能修改")
        return value


class UserSerializer(serializers.ModelSerializer):
    """用户序列化器"""
    user_role_name = serializers.CharField(source='user_role.name', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                 'phone', 'avatar', 'bio', 'user_role', 'user_role_name',
                 'is_active', 'is_staff', 'date_joined', 'last_login',
                 'nickname', 'birthday', 'qq', 'gender', 'country', 'province', 'city', 'district']
        read_only_fields = ['id', 'date_joined', 'last_login', 'user_role_name']


class UserCreateSerializer(serializers.ModelSerializer):
    """用户创建序列化器"""
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 
                 'phone', 'user_role', 'password', 'password_confirm']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("两次输入的密码不一致")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User.objects.create_user(password=password, **validated_data)
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """用户更新序列化器"""
    
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'phone', 'theme',
                 'avatar', 'bio', 'user_role', 'nickname', 
                 'birthday', 'qq', 'gender', 'province', 'city', 'district']


class PasswordChangeSerializer(serializers.Serializer):
    """密码修改序列化器"""
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("两次输入的新密码不一致")
        return attrs
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("原密码错误")
        return value


class LoginSerializer(serializers.Serializer):
    """登录序列化器"""
    username = serializers.CharField()
    password = serializers.CharField()
    
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError("用户名或密码错误")
            if not user.is_active:
                raise serializers.ValidationError("用户账户已被禁用")
            attrs['user'] = user
        else:
            raise serializers.ValidationError("必须提供用户名和密码")
        
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    """用户个人资料序列化器"""
    user_role_name = serializers.CharField(source='user_role.name', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                 'phone', 'avatar', 'bio', 'user_role', 'user_role_name',
                 'nickname', 'birthday', 'qq', 'gender', 'theme',
                 'country', 'province', 'city', 'district', 'address',
                 'date_joined', 'last_login']
        read_only_fields = ['id', 'username', 'date_joined', 'last_login', 'user_role_name']


class UserListSerializer(serializers.ModelSerializer):
    """用户列表序列化器"""
    user_role_name = serializers.CharField(source='user_role.name', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                 'phone', 'user_role', 'user_role_name', 'is_active', 
                 'is_staff', 'date_joined', 'last_login']
        read_only_fields = ['id', 'date_joined', 'last_login', 'user_role_name']


class GroupSerializer(serializers.ModelSerializer):
    """用户组序列化器"""
    from django.contrib.auth.models import Group
    
    class Meta:
        model = Group
        fields = ['id', 'name']


class SendSmsCodeSerializer(serializers.Serializer):
    """发送短信验证码序列化器"""
    phone = serializers.CharField(max_length=15)
    purpose = serializers.ChoiceField(
        choices=[('binding', '绑定手机号'), ('reset', '重置密码')],
        default='binding'
    )
    
    def validate_phone(self, value):
        """验证手机号格式"""
        import re
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError("请输入有效的手机号码")
        return value


class SendEmailCodeSerializer(serializers.Serializer):
    """发送邮箱验证码序列化器"""
    email = serializers.EmailField()
    
    def validate_email(self, value):
        """验证邮箱是否已注册"""
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("该邮箱未注册")
        return value


class ResetPasswordPhoneSerializer(serializers.Serializer):
    """通过手机重置密码序列化器"""
    phone = serializers.CharField(max_length=15)
    code = serializers.CharField(max_length=6)
    newPassword = serializers.CharField(validators=[validate_password])
    
    def validate_phone(self, value):
        """验证手机号格式"""
        import re
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError("请输入有效的手机号码")
        return value
    
    def validate_code(self, value):
        """验证验证码格式"""
        if not value.isdigit() or len(value) != 6:
            raise serializers.ValidationError("验证码必须是6位数字")
        return value


class ResetPasswordEmailSerializer(serializers.Serializer):
    """通过邮箱重置密码序列化器"""
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)
    newPassword = serializers.CharField(validators=[validate_password])
    
    def validate_code(self, value):
        """验证验证码格式"""
        if not value.isdigit() or len(value) != 6:
            raise serializers.ValidationError("验证码必须是6位数字")
        return value


class BindPhoneSerializer(serializers.Serializer):
    """绑定手机号序列化器"""
    phone = serializers.CharField(max_length=15)
    code = serializers.CharField(max_length=6)
    
    def validate_phone(self, value):
        """验证手机号格式"""
        import re
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError("请输入有效的手机号码")
        return value
    
    def validate_code(self, value):
        """验证验证码格式"""
        if not value.isdigit() or len(value) != 6:
            raise serializers.ValidationError("验证码必须是6位数字")
        return value


class BindEmailSerializer(serializers.Serializer):
    """绑定邮箱序列化器"""
    email = serializers.EmailField()
    
    def validate_email(self, value):
        """验证邮箱格式和唯一性"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            # 检查该邮箱是否已被其他用户使用
            if User.objects.filter(email=value).exclude(id=request.user.id).exists():
                raise serializers.ValidationError("该邮箱已被其他账户绑定")
        return value


class ChangePasswordSerializer(serializers.Serializer):
    """修改密码序列化器（兼容版本）"""
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    
    def validate_old_password(self, value):
        """验证旧密码"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("当前密码错误")
        return value
    
    def save(self):
        """保存新密码"""
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user
