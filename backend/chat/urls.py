from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ConversationViewSet

# 创建路由器并注册视图集
router = DefaultRouter()
router.register(r'conversations', ConversationViewSet, basename='conversation')

urlpatterns = [
    path('', include(router.urls)),
    path('send/', ConversationViewSet.as_view({'post': 'send_message'}), name='send-message'),
    
    # AI Chat 专用路由
    path('ai-chat/', include('chat.ai-chat.urls')),
    
    # AI 音频处理
    path('ai-audio/', include('chat.ai-audio.urls')),
    
    # AI 视频生成  
    path('ai-video/', include('chat.ai-video.urls')),
]
