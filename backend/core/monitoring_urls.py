"""
响应格式监控相关URL配置
"""
from django.urls import path
from .monitoring_views import (
    ResponseStatsAPIView,
    ResponseHealthAPIView,
    ResponseValidationAPIView
)

app_name = 'monitoring'

urlpatterns = [
    path('stats/', ResponseStatsAPIView.as_view(), name='response-stats'),
    path('health/', ResponseHealthAPIView.as_view(), name='response-health'),
    path('validate/', ResponseValidationAPIView.as_view(), name='response-validate'),
]