"""
Admin do app employees.
"""
from django.contrib import admin
from .models import Employee


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    """
    Admin para Employee.
    """
    list_display = (
        'full_name', 'position', 'department', 'contract_type', 
        'status', 'start_date', 'net_salary'
    )
    
    list_filter = (
        'status', 'contract_type', 'department', 'start_date', 'created_at'
    )
    
    search_fields = (
        'full_name', 'email', 'position', 'department', 'id_document', 'nuit'
    )
    
    readonly_fields = ('created_at', 'updated_at', 'created_by', 'updated_by')
    
    fieldsets = (
        ('Informações Pessoais', {
            'fields': (
                'full_name', 'address', 'id_document', 'birth_date', 
                'email', 'phone', 'nuit'
            )
        }),
        ('Informações Profissionais', {
            'fields': (
                'position', 'contract_type', 'start_date', 'department', 
                'status', 'user'
            )
        }),
        ('Informações Salariais', {
            'fields': (
                'net_salary', 'daily_allowance', 'additional_remuneration'
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