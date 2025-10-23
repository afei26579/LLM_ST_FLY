"""
旅游助手路由配置
"""

from django.urls import path
from .views import (
    TravelAssistantChatView,
    TravelAssistantHistoryView,
    GaodeMapToolsView
)

urlpatterns = [
    # 聊天接口
    path('chat/', TravelAssistantChatView.as_view(), name='travel-chat'),
    
    # 对话历史
    path('history/', TravelAssistantHistoryView.as_view(), name='travel-history'),
    
    # 工具测试接口
    path('tools/', GaodeMapToolsView.as_view(), name='gaode-tools'),
]

