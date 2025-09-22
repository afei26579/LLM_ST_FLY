"""
智能体URL配置
"""

from django.urls import path
from . import views

app_name = 'agent'

urlpatterns = [
    # 智能体管理
    path('agents/', views.list_agents, name='list_agents'),
    
    # 聊天功能
    path('chat/', views.chat, name='chat'),
    
    # 对话管理
    path('conversations/', views.list_conversations, name='list_conversations'),
    path('conversations/create/', views.create_conversation, name='create_conversation'),
    path('conversations/<str:conversation_id>/', views.get_conversation_detail, name='get_conversation_detail'),
    path('conversations/<str:conversation_id>/delete/', views.delete_conversation, name='delete_conversation'),
    
    # 用户统计
    path('stats/', views.get_user_stats, name='get_user_stats'),
]
