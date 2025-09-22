"""
AI图像生成URL路由配置
"""

from django.urls import path
from . import views

app_name = 'ai_image'

urlpatterns = [
    # 图像生成
    path('generate/', views.generate_image, name='generate_image'),
    
    # 任务状态查询
    path('task/status/', views.get_task_status, name='get_task_status'),
    
    # 图像历史
    path('history/', views.get_image_history, name='get_image_history'),
    
    # 用户统计
    path('stats/', views.get_user_stats, name='get_user_stats'),
    
    # 预设参数
    path('presets/', views.get_presets, name='get_presets'),
]
