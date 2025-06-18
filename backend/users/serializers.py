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
                 'date_joined', 'is_active', 'groups']
        read_only_fields = ['date_joined', 'is_active']
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
                 'last_name', 'phone', 'nickname', 'avatar', 'role', 'bio']
        read_only_fields = ['role']  # 普通用户不能修改自己的角色
        
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