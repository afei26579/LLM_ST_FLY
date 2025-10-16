"""
AI图像生成URL路由配置
"""

from django.urls import path
from . import views
from .merge_views import merge_images
from .style_repaint_views import style_repaint
from .background_edit_views import change_background
from .prompt_edit_views import edit_by_prompt as prompt_edit

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
    
    # 新增功能
    path('understand/', views.understand_image, name='understand_image'),
    path('detect/', views.detect_objects, name='detect_objects'),
    path('edit/', views.edit_image, name='edit_image'),
    
    # 多图融合
    path('merge/', merge_images, name='merge_images'),
    
    # 风格重绘
    path('style-repaint/', style_repaint, name='style_repaint'),
    
    # 背景更换
    path('background-edit/', change_background, name='change_background'),
    
    # 描述修改
    path('prompt-edit/', prompt_edit, name='prompt_edit'),
]
