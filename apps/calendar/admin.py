"""
Admin do app calendar.
"""
from django.contrib import admin
from .models import CalendarEvent, CalendarAttachment, CalendarNotification, CalendarSettings


class CalendarAttachmentInline(admin.TabularInline):
    """
    Inline para anexos do evento.
    """
    model = CalendarAttachment
    extra = 0
    readonly_fields = ('uploaded_at', 'uploaded_by')


@admin.register(CalendarEvent)
class CalendarEventAdmin(admin.ModelAdmin):
    """
    Admin para CalendarEvent.
    """
    list_display = (
        'title', 'employee', 'event_type', 'start_date', 'end_date',
        'status', 'priority', 'approved_by'
    )
    
    list_filter = (
        'event_type', 'status', 'priority', 'all_day', 'is_private',
        'start_date', 'created_at'
    )
    
    search_fields = (
        'title', 'description', 'location', 'employee__full_name'
    )
    
    readonly_fields = (
        'created_at', 'updated_at', 'created_by', 'updated_by',
        'approved_at', 'duration_hours'
    )
    
    inlines = [CalendarAttachmentInline]
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': (
                'title', 'description', 'event_type', 'priority', 'color'
            )
        }),
        ('Data e Hora', {
            'fields': (
                'start_date', 'end_date', 'all_day', 'location'
            )
        }),
        ('Participantes', {
            'fields': (
                'employee', 'responsible', 'participants'
            )
        }),
        ('Status e Aprovação', {
            'fields': (
                'status', 'approved_by', 'approved_at', 'rejection_reason'
            )
        }),
        ('Configurações', {
            'fields': (
                'is_private', 'is_recurring', 'recurrence_rule'
            )
        }),
        ('Metadados', {
            'fields': (
                'created_at', 'updated_at', 'created_by', 'updated_by'
            ),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """
        Salva o modelo definindo o usuário que criou/modificou.
        """
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        
        # Definir approved_at quando status muda para approved
        if obj.status == 'approved' and not obj.approved_at:
            from django.utils import timezone
            obj.approved_at = timezone.now()
            if not obj.approved_by:
                obj.approved_by = request.user
        
        super().save_model(request, obj, form, change)


@admin.register(CalendarAttachment)
class CalendarAttachmentAdmin(admin.ModelAdmin):
    """
    Admin para CalendarAttachment.
    """
    list_display = (
        'name', 'event', 'uploaded_by', 'uploaded_at'
    )
    
    list_filter = ('uploaded_at',)
    
    search_fields = (
        'name', 'description', 'event__title', 'uploaded_by__username'
    )
    
    readonly_fields = ('uploaded_at',)


@admin.register(CalendarNotification)
class CalendarNotificationAdmin(admin.ModelAdmin):
    """
    Admin para CalendarNotification.
    """
    list_display = (
        'title', 'user', 'notification_type', 'is_read', 'created_at'
    )
    
    list_filter = (
        'notification_type', 'is_read', 'created_at'
    )
    
    search_fields = (
        'title', 'message', 'user__username', 'event__title'
    )
    
    readonly_fields = ('created_at', 'read_at')


@admin.register(CalendarSettings)
class CalendarSettingsAdmin(admin.ModelAdmin):
    """
    Admin para CalendarSettings.
    """
    list_display = (
        'user', 'default_view', 'show_weekends', 'email_notifications'
    )
    
    list_filter = (
        'default_view', 'show_weekends', 'email_notifications'
    )
    
    search_fields = (
        'user__username', 'user__first_name', 'user__last_name'
    )