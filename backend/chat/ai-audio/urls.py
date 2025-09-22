"""
AI音频处理URL配置
"""

from django.urls import path
from . import views

app_name = 'ai_audio'

urlpatterns = [
    # 语音转文字
    path('speech-to-text/', views.speech_to_text, name='speech_to_text'),
    
    # 文字转语音
    path('text-to-speech/', views.text_to_speech, name='text_to_speech'),
    
    # 语音克隆
    path('voice-clone/', views.voice_clone, name='voice_clone'),
    
    # 任务状态查询
    path('task/<str:task_id>/status/', views.get_task_status, name='get_task_status'),
    
    # 历史记录
    path('history/', views.get_audio_history, name='get_audio_history'),
    
    # 用户统计
    path('stats/', views.get_user_stats, name='get_user_stats'),
]
