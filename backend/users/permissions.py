from rest_framework import permissions


class IsAdminUser(permissions.BasePermission):
    """
    只允许管理员访问的权限类
    """
    def has_permission(self, request, view):
        # 检查用户是否为管理员
        return request.user and request.user.is_admin


class IsStaffOrAdmin(permissions.BasePermission):
    """
    允许工作人员或管理员访问的权限类
    """
    def has_permission(self, request, view):
        # 检查用户是否为工作人员或管理员
        if request.user and request.user.is_authenticated:
            return request.user.is_admin or request.user.is_staff_member
        return False


class IsSelfOrAdmin(permissions.BasePermission):
    """
    允许用户修改自己的资料或允许管理员修改任何用户资料的权限类
    """
    def has_object_permission(self, request, view, obj):
        # 管理员可以修改任何用户
        if request.user.is_admin:
            return True
            
        # 普通用户只能修改自己的资料
        return obj.id == request.user.id


class ReadOnly(permissions.BasePermission):
    """
    只允许GET, HEAD, OPTIONS请求的只读权限
    """
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS 