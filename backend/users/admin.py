from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User


class CustomUserAdmin(UserAdmin):
    """自定义用户管理界面"""
    list_display = ('username', 'email', 'first_name', 'last_name', 
                    'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active', 'groups')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone')
    
    # 修改用户编辑界面的字段集
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('个人信息'), {'fields': ('first_name', 'last_name', 'email', 'phone', 'avatar', 'bio')}),
        (_('角色权限'), {'fields': ('role', 'is_active', 'is_staff', 'is_superuser',
                                'groups', 'user_permissions')}),
        (_('重要日期'), {'fields': ('last_login', 'date_joined', 'date_modified')}),
    )
    readonly_fields = ('date_modified', 'date_joined', 'last_login')
    
    # 添加用户时的字段集
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'email', 
                       'role', 'is_active', 'is_staff', 'is_superuser'),
        }),
    )
    
    ordering = ('username',)


# 注册模型和管理类
admin.site.register(User, CustomUserAdmin)
