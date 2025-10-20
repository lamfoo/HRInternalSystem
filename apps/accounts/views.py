"""
Views para o sistema de autenticação.
"""
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.utils.decorators import method_decorator
from apps.core.utils import get_user_permissions
from .forms import CustomLoginForm, UserRegistrationForm, UserProfileForm
from .models import UserProfile


def custom_login(request):
    """
    View customizada para login.
    """
    if request.user.is_authenticated:
        return redirect('core:dashboard')
    
    form = CustomLoginForm()
    
    if request.method == 'POST':
        form = CustomLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Bem-vindo, {user.get_full_name() or user.username}!')
            
            # Redirecionar para próxima página ou dashboard
            next_url = request.GET.get('next', 'core:dashboard')
            return redirect(next_url)
        else:
            messages.error(request, 'Nome de usuário ou senha inválidos.')
    
    context = {
        'form': form,
        'title': 'Login - HR Internal System'
    }
    return render(request, 'accounts/login.html', context)


@login_required
def custom_logout(request):
    """
    View customizada para logout.
    """
    logout(request)
    messages.info(request, 'Você foi desconectado com sucesso.')
    return redirect('accounts:login')


def is_admin(user):
    """
    Verifica se o usuário é administrador.
    """
    return user.is_superuser or user.groups.filter(name='Admin').exists()


@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(is_admin), name='dispatch')
class UserCreateView(CreateView):
    """
    View para criação de novos usuários (apenas admins).
    """
    form_class = UserRegistrationForm
    template_name = 'accounts/user_create.html'
    success_url = reverse_lazy('core:dashboard')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Adicionar usuário ao grupo Colaborador por padrão
        colaborador_group, created = Group.objects.get_or_create(name='Colaborador')
        self.object.groups.add(colaborador_group)
        
        messages.success(
            self.request,
            f'Usuário {self.object.username} criado com sucesso!'
        )
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Criar Novo Usuário'
        context['user_permissions'] = get_user_permissions(self.request.user)
        return context


@login_required
def profile_view(request):
    """
    View para visualizar e editar perfil do usuário.
    """
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(
            request.POST,
            request.FILES,
            instance=profile,
            user=request.user
        )
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil atualizado com sucesso!')
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=profile, user=request.user)
    
    context = {
        'form': form,
        'profile': profile,
        'title': 'Meu Perfil',
        'user_permissions': get_user_permissions(request.user)
    }
    return render(request, 'accounts/profile.html', context)


@login_required
@user_passes_test(is_admin)
def manage_users(request):
    """
    View para gerenciar usuários (apenas admins).
    """
    from django.contrib.auth.models import User
    from django.core.paginator import Paginator
    
    users = User.objects.select_related('profile').order_by('-date_joined')
    
    # Paginação
    paginator = Paginator(users, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'title': 'Gerenciar Usuários',
        'user_permissions': get_user_permissions(request.user)
    }
    return render(request, 'accounts/manage_users.html', context)