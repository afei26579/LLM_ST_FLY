"""
扩展的客服系统URL配置 - 知识库和助手管理
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views_extended import (
    KnowledgeBaseViewSet,
    KnowledgeDocumentViewSet,
    CustomerServiceAssistantViewSet,
    get_default_assistant,
    search_knowledge,
    chunk_documents,
    vectorize_chunks
)

# 创建路由器
router = DefaultRouter()

# 注册视图集
router.register(r'knowledge-bases', KnowledgeBaseViewSet, basename='knowledge-base')
router.register(r'documents', KnowledgeDocumentViewSet, basename='document')
router.register(r'assistants', CustomerServiceAssistantViewSet, basename='assistant')

# URL模式
urlpatterns = [
    # 额外的API端点（必须在router之前，避免被拦截）
    path('assistants/default/', get_default_assistant, name='default-assistant'),
    path('knowledge/search/', search_knowledge, name='search-knowledge'),
    path('knowledge-bases/chunk-documents/', chunk_documents, name='chunk-documents'),
    path('knowledge-bases/vectorize/', vectorize_chunks, name='vectorize-chunks'),
    
    # 路由器生成的URLs
    path('', include(router.urls)),
]

