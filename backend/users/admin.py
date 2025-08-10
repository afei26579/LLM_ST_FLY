from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User, Role


class CustomUserAdmin(UserAdmin):
    """自定义用户管理界面"""
    list_display = ('username', 'email', 'first_name', 'last_name', 
                    'user_role', 'is_staff', 'is_active')
    list_filter = ('user_role', 'is_staff', 'is_active', 'groups')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone')
    
    # 修改用户编辑界面的字段集
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('个人信息'), {'fields': ('first_name', 'last_name', 'email', 'phone', 'avatar', 'bio')}),
        (_('角色权限'), {'fields': ('user_role', 'is_active', 'is_staff', 'is_superuser',
                                'groups', 'user_permissions')}),
        (_('重要日期'), {'fields': ('last_login', 'date_joined', 'date_modified')}),
    )
    readonly_fields = ('date_modified', 'date_joined', 'last_login')
    
    # 添加用户时的字段集
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'email', 
                       'user_role', 'is_active', 'is_staff', 'is_superuser'),
        }),
    )
    
    ordering = ('username',)


class RoleAdmin(admin.ModelAdmin):
    """角色管理界面"""
    list_display = ('code', 'name', 'description', 'is_system', 'created_at')
    list_filter = ('is_system', 'created_at')
    search_fields = ('code', 'name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    
    def get_readonly_fields(self, request, obj=None):
        """系统角色的代码不能修改"""
        readonly_fields = list(self.readonly_fields)
        if obj and obj.is_system:
            readonly_fields.append('code')
        return readonly_fields


# 注册模型和管理类
admin.site.register(User, CustomUserAdmin)
admin.site.register(Role, RoleAdmin)