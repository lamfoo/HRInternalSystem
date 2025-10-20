"""
URLs do app calendar.
"""
from django.urls import path
from . import views

app_name = 'calendar'

urlpatterns = [
    path('', views.calendar_home, name='home'),
    path('events.json', views.calendar_events_json, name='events_json'),
    path('event/<int:pk>/', views.calendar_event_detail, name='event_detail'),
    path('event/create/', views.calendar_event_create, name='event_create'),
    path('event/<int:pk>/edit/', views.calendar_event_edit, name='event_edit'),
    path('event/<int:pk>/approve/', views.calendar_event_approve, name='event_approve'),
    path('event/quick-create/', views.calendar_event_quick_create, name='event_quick_create'),
    path('event/<int:pk>/attachment/', views.add_attachment, name='add_attachment'),
    path('event/move/', views.calendar_event_move, name='event_move'),
    path('settings/', views.calendar_settings, name='settings'),
    path('notifications/', views.calendar_notifications, name='notifications'),
    path('stats/', views.calendar_stats, name='stats'),
]