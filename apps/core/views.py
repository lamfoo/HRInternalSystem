"""
Views do app core.
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count
from django.utils import timezone
from .utils import get_user_permissions


@login_required
def dashboard(request):
    """
    Dashboard principal do sistema após login.
    """
    user_permissions = get_user_permissions(request.user)
    
    # Estatísticas para o dashboard
    stats = {}
    
    # Estatísticas básicas (serão expandidas quando os outros apps estiverem prontos)
    stats = {
        'total_users': User.objects.count(),
        'current_user': request.user.username,
    }
    
    context = {
        'user_permissions': user_permissions,
        'stats': stats,
    }
    
    return render(request, 'core/dashboard.html', context)