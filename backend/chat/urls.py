from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ChatCompletionView, ConversationViewSet

# 创建路由器并注册视图集
router = DefaultRouter()
router.register(r'conversations', ConversationViewSet, basename='conversation')

urlpatterns = [
    path('', include(router.urls)),
    path('completion/', ChatCompletionView.as_view(), name='chat_completion'),
] 