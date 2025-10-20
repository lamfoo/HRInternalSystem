"""
URLs do app accounts.
"""
from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.custom_login, name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('create-user/', views.UserCreateView.as_view(), name='create_user'),
    path('manage-users/', views.manage_users, name='manage_users'),
]