from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.utils.translation import gettext_lazy as _


class Role(models.Model):
    """
    用户角色模型
    """
    code = models.CharField(_('角色代码'), max_length=20, unique=True)
    name = models.CharField(_('角色名称'), max_length=50)
    description = models.TextField(_('角色描述'), blank=True)
    is_system = models.BooleanField(_('是否系统角色'), default=False)
    permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('角色权限'),
        blank=True,
    )
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    
    class Meta:
        verbose_name = _('角色')
        verbose_name_plural = _('角色')
        ordering = ['code']
    
    def __str__(self):
        return self.name


class User(AbstractUser):
    """
    自定义用户模型
    """
    # 性别选项
    class Gender(models.TextChoices):
        MALE = 'male', _('男')
        FEMALE = 'female', _('女')
        OTHER = 'other', _('其他')
        UNKNOWN = 'unknown', _('未知')

    # 额外用户信息字段
    phone = models.CharField(_('电话号码'), max_length=15, blank=True)
    nickname = models.CharField(_('昵称'), max_length=7, blank=True)
    avatar = models.ImageField(_('头像'), upload_to='avatars/', blank=True, null=True)
    # 临时保留原来的角色字段
    # 保留原来的角色字段，重命名为 role_str
    role_str = models.CharField(
        _('用户角色'), 
        max_length=10, 
        choices=[
            ('admin', _('管理员')),
            ('staff', _('工作人员')),
            ('user', _('普通用户')),
        ],
        default='user'
    )
    # 新的角色外键字段
    user_role = models.ForeignKey(
        Role,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('用户角色对象'),
        related_name='users'
    )
    bio = models.TextField(_('个人简介'), blank=True)
    
    # 新增用户信息字段
    birthday = models.DateField(_('生日'), blank=True, null=True)
    gender = models.CharField(
        _('性别'),
        max_length=10,
        choices=Gender.choices,
        default=Gender.UNKNOWN
    )
    qq = models.CharField(_('QQ'), max_length=20, blank=True)
    
    # 地址相关字段
    country = models.CharField(_('国家'), max_length=50, blank=True, default='中国')
    province = models.CharField(_('省份'), max_length=50, blank=True)
    city = models.CharField(_('城市'), max_length=50, blank=True)
    district = models.CharField(_('区县'), max_length=50, blank=True)
    address = models.CharField(_('详细地址'), max_length=200, blank=True)
    
    # 登录相关信息
    last_login_ip = models.GenericIPAddressField(_('上次登录IP'), blank=True, null=True)
    date_modified = models.DateTimeField(_('修改日期'), auto_now=True)
    
    # 用于权限管理的groups和user_permissions字段
    groups = models.ManyToManyField(
        Group,
        verbose_name=_('用户组'),
        blank=True,
        related_name='custom_user_set',
        related_query_name='custom_user',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('用户权限'),
        blank=True,
        related_name='custom_user_set',
        related_query_name='custom_user',
    )

    class Meta:
        verbose_name = _('用户')
        verbose_name_plural = _('用户')
        ordering = ['-date_joined']

    def __str__(self):
        return self.username
        
    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = f"{self.first_name} {self.last_name}"
        return full_name.strip()
    
    @property
    @property
    def role(self):
        """获取用户角色，优先返回 user_role，如果没有则返回 role_str"""
        if self.user_role:
            return self.user_role
        # 如果没有 user_role，根据 role_str 创建一个临时的角色对象用于兼容性
        return None
    
    @property
    def is_admin(self):
        """是否为管理员"""
        if self.user_role:
            return self.user_role.code == 'admin'
        return self.role_str == 'admin'
    
    @property
    def is_staff_member(self):
        """是否为工作人员"""
        if self.user_role:
            return self.user_role.code == 'staff'
        return self.role_str == 'staff'
        
    def has_permission(self, permission_name):
        """
        检查用户是否拥有特定权限
        根据角色或用户权限检查
        """
        # 管理员拥有所有权限
        if self.is_admin:
            return True
            
        # 检查角色权限
        if self.user_role and self.user_role.permissions.filter(codename=permission_name).exists():
            return True
            
        # 检查用户权限
        if self.user_permissions.filter(codename=permission_name).exists():
            return True
            
        # 检查用户组权限
        for group in self.groups.all():
            if group.permissions.filter(codename=permission_name).exists():
                return True
                
        return False
