from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from .views import UserViewSet, LoginView, RegisterView

# 创建路由器并注册ViewSets
router = DefaultRouter()
router.register(r'users', UserViewSet)

urlpatterns = [
    # JWT令牌视图
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # 自定义登录和注册视图
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    
    # 视图集路由
    path('', include(router.urls)),
] 