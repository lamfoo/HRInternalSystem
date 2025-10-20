"""
Models base para o sistema HR.
"""
from django.db import models
from django.contrib.auth.models import User


class TimeStampedModel(models.Model):
    """
    Modelo abstrato que adiciona campos de timestamp para created_at e updated_at.
    """
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')

    class Meta:
        abstract = True


class UserTrackingModel(TimeStampedModel):
    """
    Modelo abstrato que adiciona rastreamento de usuário que criou/modificou.
    """
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_created',
        verbose_name='Criado por'
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_updated',
        verbose_name='Atualizado por'
    )

    class Meta:
        abstract = True