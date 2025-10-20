"""
Views para a base de conhecimento.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Avg, Count
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from apps.core.utils import get_user_permissions
from .models import KnowledgeEntry, KnowledgeCategory, KnowledgeComment, KnowledgeAttachment, KnowledgeRating
from .forms import (
    KnowledgeEntryForm, KnowledgeCategoryForm, KnowledgeCommentForm, 
    KnowledgeAttachmentForm, KnowledgeRatingForm, KnowledgeSearchForm
)


def is_admin(user):
    """
    Verifica se o usuário é administrador.
    """
    return user.is_superuser or user.groups.filter(name='Admin').exists()


@login_required
def knowledge_base_home(request):
    """
    Página inicial da base de conhecimento.
    """
    # Busca e filtros
    form = KnowledgeSearchForm(request.GET)
    entries = KnowledgeEntry.objects.filter(status='published')
    
    if form.is_valid():
        search = form.cleaned_data.get('search')
        category = form.cleaned_data.get('category')
        status = form.cleaned_data.get('status')
        priority = form.cleaned_data.get('priority')
        tags = form.cleaned_data.get('tags')
        
        if search:
            entries = entries.filter(
                Q(title__icontains=search) |
                Q(problem_description__icontains=search) |
                Q(solution__icontains=search) |
                Q(tags__icontains=search)
            )
        
        if category:
            entries = entries.filter(category=category)
        
        if status:
            entries = entries.filter(status=status)
        
        if priority:
            entries = entries.filter(priority=priority)
        
        if tags:
            tag_list = [tag.strip() for tag in tags.split(',')]
            for tag in tag_list:
                entries = entries.filter(tags__icontains=tag)
    
    # Ordenação
    sort_by = request.GET.get('sort', '-created_at')
    if sort_by in ['created_at', '-created_at', 'views_count', '-views_count', 'title', '-title']:
        entries = entries.order_by(sort_by)
    else:
        entries = entries.order_by('-created_at')
    
    # Paginação
    paginator = Paginator(entries, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Estatísticas
    stats = {
        'total_entries': KnowledgeEntry.objects.filter(status='published').count(),
        'categories_count': KnowledgeCategory.objects.filter(is_active=True).count(),
        'featured_entries': KnowledgeEntry.objects.filter(status='published', is_featured=True)[:5],
        'popular_entries': KnowledgeEntry.objects.filter(status='published').order_by('-views_count')[:5],
        'recent_entries': KnowledgeEntry.objects.filter(status='published').order_by('-created_at')[:5],
    }
    
    # Categorias para sidebar
    categories = KnowledgeCategory.objects.filter(is_active=True).annotate(
        entries_count=Count('entries', filter=Q(entries__status='published'))
    ).order_by('name')
    
    context = {
        'form': form,
        'page_obj': page_obj,
        'stats': stats,
        'categories': categories,
        'current_sort': sort_by,
        'title': 'Base de Conhecimento',
        'user_permissions': get_user_permissions(request.user)
    }
    
    return render(request, 'knowledge_base/home.html', context)


@login_required
def knowledge_entry_detail(request, pk):
    """
    Detalhes de uma entrada da base de conhecimento.
    """
    entry = get_object_or_404(KnowledgeEntry, pk=pk)
    user_permissions = get_user_permissions(request.user)
    
    # Verificar se o usuário pode ver esta entrada
    if entry.status != 'published' and not user_permissions['is_admin'] and entry.author != request.user:
        messages.error(request, 'Você não tem permissão para acessar esta entrada.')
        return redirect('knowledge_base:home')
    
    # Incrementar visualizações
    if entry.status == 'published':
        entry.increment_views()
    
    # Comentários
    comments = entry.comments.filter(is_approved=True, parent=None).order_by('created_at')
    
    # Forms
    comment_form = KnowledgeCommentForm(user=request.user, entry=entry)
    attachment_form = KnowledgeAttachmentForm(user=request.user, entry=entry)
    
    # Avaliação do usuário atual
    user_rating = None
    if request.user.is_authenticated:
        try:
            user_rating = KnowledgeRating.objects.get(entry=entry, user=request.user)
        except KnowledgeRating.DoesNotExist:
            pass
    
    rating_form = KnowledgeRatingForm(user=request.user, entry=entry, instance=user_rating)
    
    # Estatísticas da entrada
    entry_stats = {
        'average_rating': entry.ratings.aggregate(avg=Avg('rating'))['avg'] or 0,
        'ratings_count': entry.ratings.count(),
        'comments_count': entry.get_comments_count(),
        'attachments_count': entry.get_attachments_count(),
    }
    
    context = {
        'entry': entry,
        'comments': comments,
        'comment_form': comment_form,
        'attachment_form': attachment_form,
        'rating_form': rating_form,
        'user_rating': user_rating,
        'entry_stats': entry_stats,
        'title': entry.title,
        'user_permissions': user_permissions
    }
    
    return render(request, 'knowledge_base/entry_detail.html', context)


@login_required
def knowledge_entry_create(request):
    """
    Criar nova entrada na base de conhecimento.
    """
    if request.method == 'POST':
        form = KnowledgeEntryForm(request.POST, user=request.user)
        if form.is_valid():
            entry = form.save()
            messages.success(request, f'Entrada "{entry.title}" criada com sucesso!')
            return redirect('knowledge_base:detail', pk=entry.pk)
    else:
        form = KnowledgeEntryForm(user=request.user)
    
    context = {
        'form': form,
        'title': 'Nova Entrada',
        'user_permissions': get_user_permissions(request.user)
    }
    
    return render(request, 'knowledge_base/entry_form.html', context)


@login_required
def knowledge_entry_edit(request, pk):
    """
    Editar entrada da base de conhecimento.
    """
    entry = get_object_or_404(KnowledgeEntry, pk=pk)
    user_permissions = get_user_permissions(request.user)
    
    # Verificar permissões
    if not user_permissions['is_admin'] and entry.author != request.user:
        messages.error(request, 'Você não tem permissão para editar esta entrada.')
        return redirect('knowledge_base:detail', pk=pk)
    
    if request.method == 'POST':
        form = KnowledgeEntryForm(request.POST, instance=entry, user=request.user)
        if form.is_valid():
            entry = form.save()
            messages.success(request, f'Entrada "{entry.title}" atualizada com sucesso!')
            return redirect('knowledge_base:detail', pk=entry.pk)
    else:
        form = KnowledgeEntryForm(instance=entry, user=request.user)
    
    context = {
        'form': form,
        'entry': entry,
        'title': f'Editar: {entry.title}',
        'user_permissions': user_permissions
    }
    
    return render(request, 'knowledge_base/entry_form.html', context)


@login_required
def add_comment(request, pk):
    """
    Adicionar comentário a uma entrada.
    """
    entry = get_object_or_404(KnowledgeEntry, pk=pk)
    parent_id = request.POST.get('parent_id')
    parent = None
    
    if parent_id:
        parent = get_object_or_404(KnowledgeComment, pk=parent_id)
    
    if request.method == 'POST':
        form = KnowledgeCommentForm(
            request.POST, 
            user=request.user, 
            entry=entry, 
            parent=parent
        )
        if form.is_valid():
            comment = form.save()
            messages.success(request, 'Comentário adicionado com sucesso!')
        else:
            messages.error(request, 'Erro ao adicionar comentário.')
    
    return redirect('knowledge_base:detail', pk=pk)


@login_required
def add_attachment(request, pk):
    """
    Adicionar anexo a uma entrada.
    """
    entry = get_object_or_404(KnowledgeEntry, pk=pk)
    user_permissions = get_user_permissions(request.user)
    
    # Verificar permissões
    if not user_permissions['is_admin'] and entry.author != request.user:
        messages.error(request, 'Você não tem permissão para adicionar anexos a esta entrada.')
        return redirect('knowledge_base:detail', pk=pk)
    
    if request.method == 'POST':
        form = KnowledgeAttachmentForm(
            request.POST, 
            request.FILES, 
            user=request.user, 
            entry=entry
        )
        if form.is_valid():
            attachment = form.save()
            messages.success(request, f'Anexo "{attachment.name}" adicionado com sucesso!')
        else:
            messages.error(request, 'Erro ao adicionar anexo.')
    
    return redirect('knowledge_base:detail', pk=pk)


@login_required
def add_rating(request, pk):
    """
    Adicionar/atualizar avaliação de uma entrada.
    """
    entry = get_object_or_404(KnowledgeEntry, pk=pk)
    
    # Verificar se já existe avaliação do usuário
    try:
        rating = KnowledgeRating.objects.get(entry=entry, user=request.user)
    except KnowledgeRating.DoesNotExist:
        rating = None
    
    if request.method == 'POST':
        form = KnowledgeRatingForm(
            request.POST, 
            instance=rating,
            user=request.user, 
            entry=entry
        )
        if form.is_valid():
            rating = form.save()
            if rating:
                messages.success(request, 'Avaliação atualizada com sucesso!')
            else:
                messages.success(request, 'Avaliação adicionada com sucesso!')
        else:
            messages.error(request, 'Erro ao salvar avaliação.')
    
    return redirect('knowledge_base:detail', pk=pk)


# Views para Categorias

@login_required
@user_passes_test(is_admin)
def knowledge_category_list(request):
    """
    Lista categorias da base de conhecimento (apenas admins).
    """
    categories = KnowledgeCategory.objects.all().annotate(
        entries_count=Count('entries')
    ).order_by('name')
    
    context = {
        'categories': categories,
        'title': 'Categorias da Base de Conhecimento',
        'user_permissions': get_user_permissions(request.user)
    }
    
    return render(request, 'knowledge_base/category_list.html', context)


@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(is_admin), name='dispatch')
class KnowledgeCategoryCreateView(CreateView):
    """
    Criar nova categoria (apenas admins).
    """
    model = KnowledgeCategory
    form_class = KnowledgeCategoryForm
    template_name = 'knowledge_base/category_form.html'
    success_url = reverse_lazy('knowledge_base:category_list')
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        
        messages.success(
            self.request,
            f'Categoria "{self.object.name}" criada com sucesso!'
        )
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Nova Categoria'
        context['user_permissions'] = get_user_permissions(self.request.user)
        return context


@login_required
def knowledge_category_detail(request, pk):
    """
    Entradas de uma categoria específica.
    """
    category = get_object_or_404(KnowledgeCategory, pk=pk)
    
    entries = KnowledgeEntry.objects.filter(
        category=category, 
        status='published'
    ).order_by('-created_at')
    
    # Paginação
    paginator = Paginator(entries, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'page_obj': page_obj,
        'title': f'Categoria: {category.name}',
        'user_permissions': get_user_permissions(request.user)
    }
    
    return render(request, 'knowledge_base/category_detail.html', context)


@login_required
@user_passes_test(is_admin)
def knowledge_stats(request):
    """
    Estatísticas da base de conhecimento (apenas admins).
    """
    from django.db.models import Avg, Sum
    
    stats = {
        'total_entries': KnowledgeEntry.objects.count(),
        'published_entries': KnowledgeEntry.objects.filter(status='published').count(),
        'draft_entries': KnowledgeEntry.objects.filter(status='draft').count(),
        'review_entries': KnowledgeEntry.objects.filter(status='review').count(),
        'total_categories': KnowledgeCategory.objects.count(),
        'active_categories': KnowledgeCategory.objects.filter(is_active=True).count(),
        'total_comments': KnowledgeComment.objects.count(),
        'total_attachments': KnowledgeAttachment.objects.count(),
        'total_ratings': KnowledgeRating.objects.count(),
        'average_rating': KnowledgeRating.objects.aggregate(avg=Avg('rating'))['avg'] or 0,
        'total_views': KnowledgeEntry.objects.aggregate(sum=Sum('views_count'))['sum'] or 0,
        'entries_by_category': KnowledgeEntry.objects.values('category__name').annotate(
            count=Count('id')
        ).order_by('-count')[:10],
        'entries_by_status': KnowledgeEntry.objects.values('status').annotate(
            count=Count('id')
        ).order_by('-count'),
        'top_authors': KnowledgeEntry.objects.values(
            'author__username', 'author__first_name', 'author__last_name'
        ).annotate(count=Count('id')).order_by('-count')[:10],
        'most_viewed': KnowledgeEntry.objects.filter(status='published').order_by('-views_count')[:10],
        'recent_entries': KnowledgeEntry.objects.order_by('-created_at')[:10],
    }
    
    context = {
        'stats': stats,
        'title': 'Estatísticas da Base de Conhecimento',
        'user_permissions': get_user_permissions(request.user)
    }
    
    return render(request, 'knowledge_base/stats.html', context)


@login_required
def search_ajax(request):
    """
    Busca AJAX para autocomplete.
    """
    query = request.GET.get('q', '')
    
    if len(query) < 3:
        return JsonResponse({'results': []})
    
    entries = KnowledgeEntry.objects.filter(
        Q(title__icontains=query) | Q(tags__icontains=query),
        status='published'
    )[:10]
    
    results = []
    for entry in entries:
        results.append({
            'id': entry.id,
            'title': entry.title,
            'url': entry.get_absolute_url(),
            'category': entry.category.name if entry.category else '',
        })
    
    return JsonResponse({'results': results})