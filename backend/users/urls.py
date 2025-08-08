from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from .views import (
    LoginView, UserViewSet, RegisterView, 
    UserManagementViewSet, GroupViewSet
)

# 创建路由器并注册ViewSets
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')  # 添加UserViewSet，提供/users/me/端点
router.register(r'user-management', UserManagementViewSet, basename='user-management')  # 重命名管理视图集
router.register(r'roles', GroupViewSet, basename='roles')


urlpatterns = [
    # JWT令牌视图
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # 用户认证和管理视图
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    
    # 视图集路由
    path('', include(router.urls)),
] 