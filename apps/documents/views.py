"""
Views para requisição e geração de documentos.
"""
import os
from datetime import datetime
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.http import HttpResponse, Http404
from django.conf import settings
from apps.core.utils import get_user_permissions, generate_word_declaration, generate_pdf_declaration, send_document_email
from apps.employees.models import Employee
from .models import DocumentRequest, DocumentTemplate, DocumentHistory
from .forms import DocumentRequestForm, DocumentApprovalForm, DocumentSearchForm, DocumentTemplateForm


def is_admin(user):
    """
    Verifica se o usuário é administrador.
    """
    return user.is_superuser or user.groups.filter(name='Admin').exists()


@login_required
def document_request_list(request):
    """
    Lista requisições de documentos.
    """
    user_permissions = get_user_permissions(request.user)
    
    # Filtrar requisições baseado nas permissões
    if user_permissions['is_admin']:
        document_requests = DocumentRequest.objects.all()
    else:
        # Colaboradores só veem suas próprias requisições
        try:
            employee = Employee.objects.get(user=request.user)
            document_requests = DocumentRequest.objects.filter(employee=employee)
        except Employee.DoesNotExist:
            document_requests = DocumentRequest.objects.none()
            messages.warning(request, 'Você não está associado a nenhum colaborador.')
    
    # Aplicar filtros de busca
    form = DocumentSearchForm(request.GET)
    if form.is_valid():
        search = form.cleaned_data.get('search')
        status = form.cleaned_data.get('status')
        document_type = form.cleaned_data.get('document_type')
        date_from = form.cleaned_data.get('date_from')
        date_to = form.cleaned_data.get('date_to')
        
        if search:
            document_requests = document_requests.filter(
                Q(employee__full_name__icontains=search) |
                Q(document_type__icontains=search) |
                Q(reason__icontains=search)
            )
        
        if status:
            document_requests = document_requests.filter(status=status)
        
        if document_type:
            document_requests = document_requests.filter(document_type=document_type)
        
        if date_from:
            document_requests = document_requests.filter(created_at__date__gte=date_from)
        
        if date_to:
            document_requests = document_requests.filter(created_at__date__lte=date_to)
    
    # Paginação
    paginator = Paginator(document_requests.order_by('-created_at'), 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'form': form,
        'page_obj': page_obj,
        'title': 'Requisições de Documentos',
        'user_permissions': user_permissions
    }
    
    return render(request, 'documents/document_request_list.html', context)


@login_required
def document_request_detail(request, pk):
    """
    Detalhes de uma requisição de documento.
    """
    document_request = get_object_or_404(DocumentRequest, pk=pk)
    user_permissions = get_user_permissions(request.user)
    
    # Verificar permissões
    if not user_permissions['is_admin']:
        # Colaboradores só podem ver suas próprias requisições
        if not hasattr(request.user, 'employee') or request.user.employee != document_request.employee:
            messages.error(request, 'Você não tem permissão para acessar esta requisição.')
            return redirect('documents:list')
    
    # Buscar histórico
    history = document_request.history.all().order_by('-timestamp')
    
    context = {
        'document_request': document_request,
        'history': history,
        'title': f'Requisição: {document_request.get_document_type_display()}',
        'user_permissions': user_permissions
    }
    
    return render(request, 'documents/document_request_detail.html', context)


@login_required
def document_request_create(request):
    """
    Criar nova requisição de documento.
    """
    try:
        employee = Employee.objects.get(user=request.user)
    except Employee.DoesNotExist:
        messages.error(request, 'Você não está associado a nenhum colaborador.')
        return redirect('core:dashboard')
    
    if request.method == 'POST':
        form = DocumentRequestForm(request.POST, employee=employee)
        if form.is_valid():
            document_request = form.save(commit=False)
            document_request.created_by = request.user
            document_request.save()
            
            # Criar entrada no histórico
            DocumentHistory.objects.create(
                document_request=document_request,
                action='created',
                user=request.user,
                notes=f'Requisição criada pelo colaborador {employee.full_name}'
            )
            
            messages.success(
                request,
                f'Requisição de {document_request.get_document_type_display()} criada com sucesso!'
            )
            return redirect('documents:detail', pk=document_request.pk)
    else:
        form = DocumentRequestForm(employee=employee)
    
    context = {
        'form': form,
        'employee': employee,
        'title': 'Nova Requisição de Documento',
        'user_permissions': get_user_permissions(request.user)
    }
    
    return render(request, 'documents/document_request_form.html', context)


@login_required
@user_passes_test(is_admin)
def document_request_approve(request, pk):
    """
    Aprovar ou rejeitar requisição de documento (apenas admins).
    """
    document_request = get_object_or_404(DocumentRequest, pk=pk)
    
    if not document_request.can_be_approved and not document_request.can_be_rejected:
        messages.error(request, 'Esta requisição não pode ser processada.')
        return redirect('documents:detail', pk=pk)
    
    if request.method == 'POST':
        form = DocumentApprovalForm(request.POST, instance=document_request)
        if form.is_valid():
            action = form.cleaned_data['action']
            old_status = document_request.status
            
            if action == 'approve':
                document_request.status = 'approved'
                document_request.approved_by = request.user
                document_request.approved_at = timezone.now()
                
                # Gerar documento automaticamente
                try:
                    if document_request.document_type == 'declaracao_rendimentos':
                        # Gerar documento Word
                        file_path = generate_word_declaration(document_request.employee)
                        
                        # Salvar caminho relativo no modelo
                        relative_path = os.path.relpath(file_path, settings.MEDIA_ROOT)
                        document_request.document_file.name = relative_path
                        
                        # Enviar por email
                        email_sent = send_document_email(
                            document_request.employee.email,
                            file_path,
                            document_request.employee.full_name,
                            document_request.get_document_type_display()
                        )
                        
                        if email_sent:
                            document_request.email_sent = True
                            document_request.status = 'completed'
                            
                            # Histórico de email enviado
                            DocumentHistory.objects.create(
                                document_request=document_request,
                                action='email_sent',
                                user=request.user,
                                notes='Documento enviado por email'
                            )
                        
                        # Histórico de documento gerado
                        DocumentHistory.objects.create(
                            document_request=document_request,
                            action='document_generated',
                            user=request.user,
                            notes='Documento Word gerado automaticamente'
                        )
                        
                except Exception as e:
                    messages.error(request, f'Erro ao gerar documento: {str(e)}')
                    document_request.status = 'processing'
                
                messages.success(request, 'Requisição aprovada com sucesso!')
                
            else:  # reject
                document_request.status = 'rejected'
                document_request.rejection_reason = form.cleaned_data['rejection_reason']
                messages.success(request, 'Requisição rejeitada.')
            
            form.save()
            
            # Criar entrada no histórico
            DocumentHistory.objects.create(
                document_request=document_request,
                action='approved' if action == 'approve' else 'rejected',
                user=request.user,
                old_status=old_status,
                new_status=document_request.status,
                notes=form.cleaned_data.get('admin_notes', '')
            )
            
            return redirect('documents:detail', pk=pk)
    else:
        form = DocumentApprovalForm(instance=document_request)
    
    context = {
        'form': form,
        'document_request': document_request,
        'title': f'Processar: {document_request.get_document_type_display()}',
        'user_permissions': get_user_permissions(request.user)
    }
    
    return render(request, 'documents/document_request_approve.html', context)


@login_required
def document_download(request, pk):
    """
    Download de documento gerado.
    """
    document_request = get_object_or_404(DocumentRequest, pk=pk)
    user_permissions = get_user_permissions(request.user)
    
    # Verificar permissões
    if not user_permissions['is_admin']:
        if not hasattr(request.user, 'employee') or request.user.employee != document_request.employee:
            messages.error(request, 'Você não tem permissão para baixar este documento.')
            return redirect('documents:list')
    
    if not document_request.document_file:
        messages.error(request, 'Documento não disponível para download.')
        return redirect('documents:detail', pk=pk)
    
    try:
        file_path = document_request.document_file.path
        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                response = HttpResponse(f.read(), content_type='application/octet-stream')
                response['Content-Disposition'] = f'attachment; filename="{document_request.get_file_name()}"'
                return response
        else:
            messages.error(request, 'Arquivo não encontrado.')
            return redirect('documents:detail', pk=pk)
    except Exception as e:
        messages.error(request, f'Erro ao baixar arquivo: {str(e)}')
        return redirect('documents:detail', pk=pk)


# Views para Templates de Documentos

@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(is_admin), name='dispatch')
class DocumentTemplateListView(CreateView):
    """
    Lista templates de documentos (apenas admins).
    """
    model = DocumentTemplate
    template_name = 'documents/template_list.html'
    context_object_name = 'templates'
    
    def get_queryset(self):
        return DocumentTemplate.objects.all().order_by('document_type', 'name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Templates de Documentos'
        context['user_permissions'] = get_user_permissions(self.request.user)
        return context


@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(is_admin), name='dispatch')
class DocumentTemplateCreateView(CreateView):
    """
    Criar novo template de documento (apenas admins).
    """
    model = DocumentTemplate
    form_class = DocumentTemplateForm
    template_name = 'documents/template_form.html'
    success_url = reverse_lazy('documents:template_list')
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        
        messages.success(
            self.request,
            f'Template {self.object.name} criado com sucesso!'
        )
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Novo Template'
        context['user_permissions'] = get_user_permissions(self.request.user)
        return context


@login_required
@user_passes_test(is_admin)
def document_stats(request):
    """
    Estatísticas de documentos (apenas admins).
    """
    from django.db.models import Count
    
    stats = {
        'total_requests': DocumentRequest.objects.count(),
        'pending_requests': DocumentRequest.objects.filter(status='pending').count(),
        'approved_requests': DocumentRequest.objects.filter(status='approved').count(),
        'completed_requests': DocumentRequest.objects.filter(status='completed').count(),
        'rejected_requests': DocumentRequest.objects.filter(status='rejected').count(),
        'requests_by_type': DocumentRequest.objects.values('document_type').annotate(
            count=Count('id')
        ).order_by('-count'),
        'requests_by_status': DocumentRequest.objects.values('status').annotate(
            count=Count('id')
        ).order_by('-count'),
        'recent_requests': DocumentRequest.objects.order_by('-created_at')[:10],
    }
    
    context = {
        'stats': stats,
        'title': 'Estatísticas de Documentos',
        'user_permissions': get_user_permissions(request.user)
    }
    
    return render(request, 'documents/document_stats.html', context)