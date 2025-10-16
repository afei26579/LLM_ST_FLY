from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AIChatViewSet, stream_chat_view

# 创建路由器并注册AI Chat视图集
router = DefaultRouter()
router.register(r'conversations', AIChatViewSet, basename='aichat-conversation')

urlpatterns = [
    # AI Chat API路由
    path('', include(router.urls)),
    
    # 流式聊天路由（独立视图，避免DRF内容协商问题）
    path('stream-chat/', stream_chat_view, name='ai-chat-stream'),
    
    # 自定义动作路由（如果需要的话）
    # 这些路由会自动通过ViewSet的action装饰器生成，不需要手动定义
    # path('conversations/<int:pk>/create-message/', AIChatViewSet.as_view({'post': 'create_message'})),
    # path('conversations/list-conversations/', AIChatViewSet.as_view({'get': 'list_conversations'})),
    # path('conversations/<int:pk>/get-messages/', AIChatViewSet.as_view({'get': 'get_messages'})),
]
