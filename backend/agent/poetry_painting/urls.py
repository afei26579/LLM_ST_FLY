"""
诗词绘画智能体路由配置
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PoetryPaintingViewSet, create_work_stream

router = DefaultRouter()
router.register(r'', PoetryPaintingViewSet, basename='poetry-painting')

urlpatterns = [
    path('create-work-stream/', create_work_stream, name='create-work-stream'),
    path('', include(router.urls)),
]

