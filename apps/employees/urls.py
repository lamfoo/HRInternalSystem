"""
URLs do app employees.
"""
from django.urls import path
from . import views

app_name = 'employees'

urlpatterns = [
    path('', views.employee_list, name='list'),
    path('<int:pk>/', views.employee_detail, name='detail'),
    path('create/', views.EmployeeCreateView.as_view(), name='create'),
    path('<int:pk>/edit/', views.EmployeeUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.EmployeeDeleteView.as_view(), name='delete'),
    path('stats/', views.employee_stats, name='stats'),
]