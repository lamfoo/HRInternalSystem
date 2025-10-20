"""
URLs do app knowledge_base.
"""
from django.urls import path
from . import views

app_name = 'knowledge_base'

urlpatterns = [
    path('', views.knowledge_base_home, name='home'),
    path('entry/<int:pk>/', views.knowledge_entry_detail, name='detail'),
    path('entry/create/', views.knowledge_entry_create, name='create'),
    path('entry/<int:pk>/edit/', views.knowledge_entry_edit, name='edit'),
    path('entry/<int:pk>/comment/', views.add_comment, name='add_comment'),
    path('entry/<int:pk>/attachment/', views.add_attachment, name='add_attachment'),
    path('entry/<int:pk>/rating/', views.add_rating, name='add_rating'),
    
    # Categorias
    path('categories/', views.knowledge_category_list, name='category_list'),
    path('categories/create/', views.KnowledgeCategoryCreateView.as_view(), name='category_create'),
    path('category/<int:pk>/', views.knowledge_category_detail, name='category_detail'),
    
    # Estatísticas e AJAX
    path('stats/', views.knowledge_stats, name='stats'),
    path('search-ajax/', views.search_ajax, name='search_ajax'),
]