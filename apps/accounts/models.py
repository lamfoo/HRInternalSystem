"""
Models para o sistema de autenticação e perfis.
"""
from django.db import models
from django.contrib.auth.models import User
from apps.core.models import TimeStampedModel


class UserProfile(TimeStampedModel):
    """
    Perfil estendido para usuários do sistema.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name='Usuário'
    )
    
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Telefone'
    )
    
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        verbose_name='Avatar'
    )
    
    department = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Departamento'
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='Ativo'
    )
    
    class Meta:
        verbose_name = 'Perfil do Usuário'
        verbose_name_plural = 'Perfis dos Usuários'
    
    def __str__(self):
        return f'Perfil de {self.user.get_full_name() or self.user.username}'
    
    @property
    def full_name(self):
        """Retorna o nome completo do usuário."""
        return self.user.get_full_name() or self.user.username