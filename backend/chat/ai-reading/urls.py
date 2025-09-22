from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_file, name='upload_file'),
    path('analyze/', views.analyze_document, name='analyze_document'),
    path('complete-analysis/', views.complete_analysis, name='complete_analysis'),
    path('ask/', views.ask_question, name='ask_question'),
    path('qa-history/', views.get_qa_history, name='get_qa_history'),
    path('documents/', views.get_user_documents, name='get_user_documents'),
    path('stats/', views.get_user_stats, name='get_user_stats'),
    path('history/', views.get_document_history, name='get_document_history'),
]