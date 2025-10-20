"""
Admin do app accounts.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile


class UserProfileInline(admin.StackedInline):
    """
    Inline para o perfil do usuário.
    """
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Perfil'


class UserAdmin(BaseUserAdmin):
    """
    Admin customizado para User com perfil inline.
    """
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_department')
    list_filter = BaseUserAdmin.list_filter + ('profile__department',)
    
    def get_department(self, obj):
        """Retorna o departamento do usuário."""
        return obj.profile.department if hasattr(obj, 'profile') else '-'
    get_department.short_description = 'Departamento'


# Desregistrar o User admin padrão e registrar o customizado
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    Admin para UserProfile.
    """
    list_display = ('user', 'department', 'phone', 'is_active', 'created_at')
    list_filter = ('department', 'is_active', 'created_at')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'department')
    readonly_fields = ('created_at', 'updated_at')