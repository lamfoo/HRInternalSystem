"""
Signals para o app accounts.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db import transaction


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Cria automaticamente um perfil quando um usuário é criado.
    """
    if created:
        try:
            # Importar aqui para evitar problemas de importação circular
            from .models import UserProfile
            
            # Usar transaction para garantir consistência
            with transaction.atomic():
                UserProfile.objects.get_or_create(user=instance)
        except Exception as e:
            # Log do erro, mas não falha
            print(f"Erro ao criar perfil para usuário {instance.username}: {e}")


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Salva o perfil quando o usuário é salvo.
    """
    try:
        # Importar aqui para evitar problemas de importação circular
        from .models import UserProfile
        
        # Verificar se o perfil existe antes de tentar acessá-lo
        try:
            profile = UserProfile.objects.get(user=instance)
            profile.save()
        except UserProfile.DoesNotExist:
            # Se não existe, criar um novo
            UserProfile.objects.create(user=instance)
    except Exception as e:
        # Log do erro, mas não falha
        print(f"Erro ao salvar perfil para usuário {instance.username}: {e}")