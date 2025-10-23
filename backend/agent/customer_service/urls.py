"""
客服系统 URL 配置
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'sessions', views.CustomerServiceSessionViewSet, basename='cs-session')
router.register(r'knowledge', views.CustomerServiceKnowledgeBaseViewSet, basename='cs-knowledge')

urlpatterns = [
    # 核心对话接口
    path('chat/', views.customer_service_chat, name='cs-chat'),
    
    # 满意度反馈
    path('feedback/', views.submit_satisfaction, name='cs-feedback'),
    
    # 统计信息
    path('stats/', views.get_user_stats, name='cs-stats'),
    
    # 欢迎语
    path('greeting/', views.get_greeting, name='cs-greeting'),
    
    # ViewSet 路由
    path('', include(router.urls)),
    
    # 扩展的知识库和助手管理API
    path('', include('agent.customer_service.urls_extended')),
]

