"""
AI视频生成URL配置
"""

from django.urls import path
from . import views

app_name = 'ai-video'

urlpatterns = [
    # 文生视频
    path('text-to-video/', views.text_to_video, name='text_to_video'),
    
    # 图生视频
    path('image-to-video/', views.image_to_video, name='image_to_video'),
    
    # 任务状态查询
    path('task/<str:task_id>/status/', views.get_video_task_status, name='get_video_task_status'),
    
    # 历史记录
    path('history/', views.get_video_history, name='get_video_history'),
    
    # 用户统计
    path('stats/', views.get_user_video_stats, name='get_user_video_stats'),
    
    # 风格预设
    path('style-presets/', views.get_video_style_presets, name='get_video_style_presets'),
]
