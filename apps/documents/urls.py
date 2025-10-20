"""
URLs do app documents.
"""
from django.urls import path
from . import views

app_name = 'documents'

urlpatterns = [
    path('', views.document_request_list, name='list'),
    path('<int:pk>/', views.document_request_detail, name='detail'),
    path('create/', views.document_request_create, name='create'),
    path('<int:pk>/approve/', views.document_request_approve, name='approve'),
    path('<int:pk>/download/', views.document_download, name='download'),
    path('stats/', views.document_stats, name='stats'),
    
    # Templates
    path('templates/', views.DocumentTemplateListView.as_view(), name='template_list'),
    path('templates/create/', views.DocumentTemplateCreateView.as_view(), name='template_create'),
]