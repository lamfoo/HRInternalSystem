"""
Admin do app documents.
"""
from django.contrib import admin
from .models import DocumentRequest, DocumentTemplate, DocumentHistory


@admin.register(DocumentRequest)
class DocumentRequestAdmin(admin.ModelAdmin):
    """
    Admin para DocumentRequest.
    """
    list_display = (
        'employee', 'document_type', 'status', 'created_at', 
        'approved_by', 'email_sent'
    )
    
    list_filter = (
        'status', 'document_type', 'email_sent', 'created_at', 'approved_at'
    )
    
    search_fields = (
        'employee__full_name', 'employee__email', 'reason', 'admin_notes'
    )
    
    readonly_fields = (
        'created_at', 'updated_at', 'created_by', 'updated_by', 'approved_at'
    )
    
    fieldsets = (
        ('Informações da Requisição', {
            'fields': (
                'employee', 'document_type', 'status', 'reason'
            )
        }),
        ('Processamento', {
            'fields': (
                'admin_notes', 'approved_by', 'approved_at', 
                'rejection_reason', 'document_file', 'email_sent'
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
        super().save_model(request, obj, form, change)


@admin.register(DocumentTemplate)
class DocumentTemplateAdmin(admin.ModelAdmin):
    """
    Admin para DocumentTemplate.
    """
    list_display = (
        'name', 'document_type', 'template_type', 'is_active', 'created_at'
    )
    
    list_filter = (
        'document_type', 'template_type', 'is_active', 'created_at'
    )
    
    search_fields = (
        'name', 'description'
    )
    
    readonly_fields = (
        'created_at', 'updated_at', 'created_by', 'updated_by'
    )
    
    fieldsets = (
        ('Informações do Template', {
            'fields': (
                'name', 'document_type', 'template_type', 
                'template_file', 'description', 'is_active'
            )
        }),
        ('Variáveis', {
            'fields': ('variables',),
            'classes': ('collapse',)
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
        super().save_model(request, obj, form, change)


@admin.register(DocumentHistory)
class DocumentHistoryAdmin(admin.ModelAdmin):
    """
    Admin para DocumentHistory.
    """
    list_display = (
        'document_request', 'action', 'user', 'timestamp'
    )
    
    list_filter = (
        'action', 'timestamp'
    )
    
    search_fields = (
        'document_request__employee__full_name', 'notes', 'user__username'
    )
    
    readonly_fields = (
        'document_request', 'action', 'user', 'timestamp', 
        'notes', 'old_status', 'new_status'
    )
    
    def has_add_permission(self, request):
        """
        Não permite adicionar histórico manualmente.
        """
        return False
    
    def has_change_permission(self, request, obj=None):
        """
        Não permite editar histórico.
        """
        return False