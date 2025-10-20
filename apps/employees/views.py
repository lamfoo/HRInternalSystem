"""
Views para o cadastro de colaboradores.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView
from django.utils.decorators import method_decorator
from apps.core.utils import get_user_permissions
from .models import Employee
from .forms import EmployeeForm, EmployeeSearchForm


def is_admin(user):
    """
    Verifica se o usuário é administrador.
    """
    return user.is_superuser or user.groups.filter(name='Admin').exists()


@login_required
def employee_list(request):
    """
    Lista todos os colaboradores com filtros de busca.
    """
    user_permissions = get_user_permissions(request.user)
    
    # Verificar se o usuário pode ver a lista de colaboradores
    if not user_permissions['is_admin']:
        # Colaboradores só podem ver seus próprios dados
        try:
            employee = Employee.objects.get(user=request.user)
            return redirect('employees:detail', pk=employee.pk)
        except Employee.DoesNotExist:
            messages.error(request, 'Você não tem permissão para acessar esta página.')
            return redirect('core:dashboard')
    
    # Busca e filtros
    form = EmployeeSearchForm(request.GET)
    employees = Employee.objects.all().order_by('full_name')
    
    if form.is_valid():
        search = form.cleaned_data.get('search')
        status = form.cleaned_data.get('status')
        department = form.cleaned_data.get('department')
        contract_type = form.cleaned_data.get('contract_type')
        
        if search:
            employees = employees.filter(
                Q(full_name__icontains=search) |
                Q(position__icontains=search) |
                Q(department__icontains=search) |
                Q(email__icontains=search)
            )
        
        if status:
            employees = employees.filter(status=status)
        
        if department:
            employees = employees.filter(department__icontains=department)
        
        if contract_type:
            employees = employees.filter(contract_type=contract_type)
    
    # Paginação
    paginator = Paginator(employees, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'form': form,
        'page_obj': page_obj,
        'title': 'Lista de Colaboradores',
        'user_permissions': user_permissions
    }
    
    return render(request, 'employees/employee_list.html', context)


@login_required
def employee_detail(request, pk):
    """
    Detalhes de um colaborador específico.
    """
    employee = get_object_or_404(Employee, pk=pk)
    user_permissions = get_user_permissions(request.user)
    
    # Verificar permissões
    if not user_permissions['is_admin']:
        # Colaboradores só podem ver seus próprios dados
        if not hasattr(request.user, 'employee') or request.user.employee != employee:
            messages.error(request, 'Você não tem permissão para acessar estes dados.')
            return redirect('core:dashboard')
    
    context = {
        'employee': employee,
        'title': f'Colaborador: {employee.full_name}',
        'user_permissions': user_permissions
    }
    
    return render(request, 'employees/employee_detail.html', context)


@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(is_admin), name='dispatch')
class EmployeeCreateView(CreateView):
    """
    View para criação de novos colaboradores (apenas admins).
    """
    model = Employee
    form_class = EmployeeForm
    template_name = 'employees/employee_form.html'
    success_url = reverse_lazy('employees:list')
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        
        messages.success(
            self.request,
            f'Colaborador {self.object.full_name} criado com sucesso!'
        )
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Novo Colaborador'
        context['user_permissions'] = get_user_permissions(self.request.user)
        return context


@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(is_admin), name='dispatch')
class EmployeeUpdateView(UpdateView):
    """
    View para edição de colaboradores (apenas admins).
    """
    model = Employee
    form_class = EmployeeForm
    template_name = 'employees/employee_form.html'
    success_url = reverse_lazy('employees:list')
    
    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        response = super().form_valid(form)
        
        messages.success(
            self.request,
            f'Colaborador {self.object.full_name} atualizado com sucesso!'
        )
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Editar: {self.object.full_name}'
        context['user_permissions'] = get_user_permissions(self.request.user)
        return context


@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(is_admin), name='dispatch')
class EmployeeDeleteView(DeleteView):
    """
    View para exclusão de colaboradores (apenas admins).
    """
    model = Employee
    template_name = 'employees/employee_confirm_delete.html'
    success_url = reverse_lazy('employees:list')
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        
        messages.success(
            request,
            f'Colaborador {self.object.full_name} removido com sucesso!'
        )
        
        self.object.delete()
        return redirect(success_url)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Remover: {self.object.full_name}'
        context['user_permissions'] = get_user_permissions(self.request.user)
        return context


@login_required
@user_passes_test(is_admin)
def employee_stats(request):
    """
    Estatísticas dos colaboradores (apenas admins).
    """
    from django.db.models import Count, Avg, Sum
    from decimal import Decimal
    
    stats = {
        'total_employees': Employee.objects.count(),
        'active_employees': Employee.objects.filter(status='active').count(),
        'inactive_employees': Employee.objects.filter(status='inactive').count(),
        'employees_by_department': Employee.objects.values('department').annotate(
            count=Count('id')
        ).order_by('-count')[:10],
        'employees_by_contract_type': Employee.objects.values('contract_type').annotate(
            count=Count('id')
        ).order_by('-count'),
        'average_salary': Employee.objects.aggregate(
            avg_salary=Avg('net_salary')
        )['avg_salary'] or Decimal('0'),
        'total_payroll': Employee.objects.filter(status='active').aggregate(
            total=Sum('net_salary')
        )['total'] or Decimal('0'),
    }
    
    context = {
        'stats': stats,
        'title': 'Estatísticas dos Colaboradores',
        'user_permissions': get_user_permissions(request.user)
    }
    
    return render(request, 'employees/employee_stats.html', context)