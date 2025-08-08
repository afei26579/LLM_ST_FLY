from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import Group

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """用户序列化器"""
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'first_name', 
                 'last_name', 'phone', 'nickname', 'avatar', 'role', 'bio', 
                 'birthday', 'gender', 'qq', 'country', 'province', 'city',
                 'district', 'address', 'last_login_ip',
                 'date_joined', 'is_active', 'groups']
        read_only_fields = ['date_joined', 'is_active', 'last_login_ip']
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def create(self, validated_data):
        """创建用户时对密码进行加密"""
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance
    
    def update(self, instance, validated_data):
        """更新用户时对密码进行加密"""
        password = validated_data.pop('password', None)
        if password is not None:
            instance.set_password(password)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance


class UserProfileSerializer(serializers.ModelSerializer):
    """用户资料序列化器（简化版）"""
    avatar = serializers.FileField(required=False, allow_null=True, allow_empty_file=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 
                 'last_name', 'phone', 'nickname', 'avatar', 'role', 'bio',
                 'birthday', 'gender', 'qq', 'country', 'province', 'city',
                 'district', 'address', 'last_login_ip']
        read_only_fields = ['role', 'last_login_ip']  # 普通用户不能修改自己的角色和登录IP
        
    def validate_avatar(self, value):
        """
        验证头像字段，支持文件对象和字符串URL
        """
        # 如果值为None，直接返回None表示不更新头像
        print(value, 'value')
        if value is None:
            return None
            
        # 如果是文件对象，直接返回
        if hasattr(value, 'read'):
            return value
            
        # 如果是字符串（可能是URL）
        if isinstance(value, str):
            # 如果是空字符串，返回None表示不更新
            if value.strip() == '':
                return None
                
            # 如果是URL路径，表示不需要更新，返回None
            if value.startswith('/media/'):
                return None
                    
        return value
    
    def update(self, instance, validated_data):
        """
        更新用户时特殊处理头像字段
        """
        # 如果avatar在validated_data中是None，表示不需要更新头像
        if 'avatar' in validated_data and validated_data['avatar'] is None:
            validated_data.pop('avatar')
            
        return super().update(instance, validated_data)


class LoginSerializer(serializers.Serializer):
    """登录序列化器"""
    username = serializers.CharField(max_length=255)
    password = serializers.CharField(
        label=_("密码"),
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True
    )
    
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        
        # 检查是否提供了用户名和密码
        if not username or not password:
            msg = _('必须包含"username"和"password"字段')
            raise serializers.ValidationError(
                {'param_error': msg}, 
                code='invalid_parameters'
            )
        
        # 尝试认证用户
        user = authenticate(request=self.context.get('request'),
                            username=username, password=password)
        
        # 认证失败的情况
        if not user:
            msg = _('账号或密码错误')
            raise serializers.ValidationError(
                {'auth_error': msg}, 
                code='authentication_failed'
            )
        
        attrs['user'] = user
        return attrs


class GroupSerializer(serializers.ModelSerializer):
    """用户组序列化器"""
    
    class Meta:
        model = Group
        fields = ['id', 'name']


class UserGroupSerializer(serializers.ModelSerializer):
    """带用户组详情的用户序列化器"""
    groups = GroupSerializer(many=True, read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 
                 'last_name', 'nickname', 'role', 'is_active', 'groups']


class ChangePasswordSerializer(serializers.Serializer):
    """密码修改序列化器"""
    oldPassword = serializers.CharField(required=True, write_only=True)
    newPassword = serializers.CharField(required=True, write_only=True)
    
    def validate_oldPassword(self, value):
        """验证旧密码是否正确"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError(_("当前密码不正确"), code="password_incorrect")
        return value
    
    def validate_newPassword(self, value):
        """验证新密码规则"""
        if len(value) < 6:
            raise serializers.ValidationError(_("密码长度至少为6位"), code="password_too_short")
        return value
    
    def validate(self, attrs):
        """验证新密码与旧密码不能相同"""
        if attrs.get('oldPassword') == attrs.get('newPassword'):
            raise serializers.ValidationError(
                {"newPassword": _("新密码不能与当前密码相同")}, 
                code="password_same"
            )
        return attrs
    
    def save(self):
        """保存新密码"""
        user = self.context['request'].user
        user.set_password(self.validated_data['newPassword'])
        user.save(update_fields=['password'])
        return user


class SendSmsCodeSerializer(serializers.Serializer):
    """发送手机验证码序列化器"""
    phone = serializers.CharField(max_length=15, required=True)
    purpose = serializers.ChoiceField(
        choices=['binding', 'reset'], 
        default='binding',
        required=False,
        help_text="验证码用途：binding-绑定手机号，reset-重置密码"
    )
    
    def validate_phone(self, value):
        """验证手机号格式"""
        # 只验证手机号格式，不验证是否已注册
        # TODO: 可以在这里添加手机号格式验证逻辑
        return value


class SendEmailCodeSerializer(serializers.Serializer):
    """发送邮箱验证码序列化器"""
    email = serializers.EmailField(required=True)
    
    def validate_email(self, value):
        """验证邮箱是否已注册"""
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError(_("该邮箱未注册"), code="email_not_found")
        return value


class ResetPasswordPhoneSerializer(serializers.Serializer):
    """通过手机号重置密码序列化器"""
    phone = serializers.CharField(max_length=15, required=True)
    code = serializers.CharField(required=True)
    newPassword = serializers.CharField(required=True, write_only=True)
    
    def validate_phone(self, value):
        """验证手机号是否已注册"""
        if not User.objects.filter(phone=value).exists():
            raise serializers.ValidationError(_("该手机号未注册"), code="phone_not_found")
        return value
    
    def validate_code(self, value):
        """验证手机验证码是否正确"""
        # TODO: 实际验证码验证逻辑
        return value
    
    def validate_newPassword(self, value):
        """验证新密码规则"""
        if len(value) < 6:
            raise serializers.ValidationError(_("密码长度至少为6位"), code="password_too_short")
        return value


class ResetPasswordEmailSerializer(serializers.Serializer):
    """通过邮箱重置密码序列化器"""
    email = serializers.EmailField(required=True)
    code = serializers.CharField(required=True)
    newPassword = serializers.CharField(required=True, write_only=True)
    
    def validate_email(self, value):
        """验证邮箱是否已注册"""
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError(_("该邮箱未注册"), code="email_not_found")
        return value
    
    def validate_code(self, value):
        """验证邮箱验证码是否正确"""
        # TODO: 实际验证码验证逻辑
        return value
    
    def validate_newPassword(self, value):
        """验证新密码规则"""
        if len(value) < 6:
            raise serializers.ValidationError(_("密码长度至少为6位"), code="password_too_short")
        return value


class BindPhoneSerializer(serializers.Serializer):
    """绑定手机号序列化器"""
    phone = serializers.CharField(max_length=15, required=True)
    code = serializers.CharField(required=True)
    
    def validate_phone(self, value):
        """验证手机号格式"""
        # 验证手机号格式，例如中国大陆手机号
        import re
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError(_("请输入有效的手机号码"), code="invalid_phone")
        return value


class BindEmailSerializer(serializers.Serializer):
    """绑定邮箱序列化器"""
    email = serializers.EmailField(required=True)
    
    def validate_email(self, value):
        """验证邮箱格式"""
        # EmailField已经验证了基本格式，这里可以添加额外的验证逻辑
        return value


class UserListSerializer(serializers.ModelSerializer):
    """用户列表序列化器"""
    role = serializers.SerializerMethodField()
    createdAt = serializers.DateTimeField(source='date_joined', read_only=True, format='%Y-%m-%dT%H:%M:%S')
    isActive = serializers.BooleanField(source='is_active')
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'isActive', 'createdAt']
        
    def get_role(self, obj):
        """获取用户角色信息"""
        try:
            group = obj.groups.first()
            if group:
                return {
                    'id': group.id,
                    'name': group.name
                }
            return None
        except Exception:
            return None


class UserCreateSerializer(serializers.ModelSerializer):
    """用户创建序列化器"""
    roleId = serializers.IntegerField(required=False, write_only=True, allow_null=True)
    password = serializers.CharField(write_only=True, required=True)
    isActive = serializers.BooleanField(source='is_active', default=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'roleId', 'isActive']
        
    def validate_email(self, value):
        """验证邮箱唯一性"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(_("该邮箱已被注册"))
        return value
        
    def validate_username(self, value):
        """验证用户名唯一性"""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(_("该用户名已被使用"))
        return value
        
    def create(self, validated_data):
        role_id = validated_data.pop('roleId', None)
        user = User.objects.create_user(**validated_data)
        
        # 分配用户组
        if role_id:
            try:
                group = Group.objects.get(id=role_id)
                user.groups.add(group)
            except Group.DoesNotExist:
                pass
        
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """用户更新序列化器"""
    roleId = serializers.IntegerField(required=False, write_only=True, allow_null=True)
    isActive = serializers.BooleanField(source='is_active', required=False)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'roleId', 'isActive']
        
    def validate_email(self, value):
        """验证邮箱唯一性"""
        instance = self.instance
        if User.objects.exclude(id=instance.id).filter(email=value).exists():
            raise serializers.ValidationError(_("该邮箱已被注册"))
        return value
        
    def validate_username(self, value):
        """验证用户名唯一性"""
        instance = self.instance
        if User.objects.exclude(id=instance.id).filter(username=value).exists():
            raise serializers.ValidationError(_("该用户名已被使用"))
        return value
        
    def update(self, instance, validated_data):
        role_id = validated_data.pop('roleId', None)
        
        # 更新用户基本信息
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # 更新用户组
        if role_id is not None:
            # 清除现有用户组
            instance.groups.clear()
            
            # 分配新用户组
            if role_id:
                try:
                    group = Group.objects.get(id=role_id)
                    instance.groups.add(group)
                except Group.DoesNotExist:
                    pass
        
        return instance 