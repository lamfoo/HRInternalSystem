"""
Views para o calendário interno.
"""
import json
from datetime import datetime, timedelta
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView
from django.utils.decorators import method_decorator
from django.utils import timezone
from apps.core.utils import get_user_permissions
from apps.employees.models import Employee
from .models import CalendarEvent, CalendarAttachment, CalendarSettings, CalendarNotification
from .forms import (
    CalendarEventForm, CalendarEventApprovalForm, CalendarAttachmentForm,
    CalendarSettingsForm, CalendarFilterForm, QuickEventForm
)


def is_admin(user):
    """
    Verifica se o usuário é administrador.
    """
    return user.is_superuser or user.groups.filter(name='Admin').exists()


@login_required
def calendar_home(request):
    """
    Página principal do calendário.
    """
    user_permissions = get_user_permissions(request.user)
    
    # Obter configurações do usuário
    settings, created = CalendarSettings.objects.get_or_create(
        user=request.user,
        defaults={
            'default_view': 'month',
            'show_weekends': True,
        }
    )
    
    # Form para filtros
    filter_form = CalendarFilterForm()
    
    # Form para criação rápida
    quick_form = QuickEventForm(user=request.user)
    
    # Estatísticas
    stats = {}
    if user_permissions['is_admin']:
        stats = {
            'total_events': CalendarEvent.objects.count(),
            'pending_events': CalendarEvent.objects.filter(status='pending').count(),
            'approved_events': CalendarEvent.objects.filter(status='approved').count(),
            'upcoming_events': CalendarEvent.objects.filter(
                status='approved',
                start_date__gte=timezone.now()
            ).count(),
        }
    else:
        # Estatísticas para colaboradores
        try:
            employee = Employee.objects.get(user=request.user)
            stats = {
                'my_events': CalendarEvent.objects.filter(employee=employee).count(),
                'my_pending': CalendarEvent.objects.filter(
                    employee=employee, status='pending'
                ).count(),
                'my_approved': CalendarEvent.objects.filter(
                    employee=employee, status='approved'
                ).count(),
                'my_upcoming': CalendarEvent.objects.filter(
                    employee=employee,
                    status='approved',
                    start_date__gte=timezone.now()
                ).count(),
            }
        except Employee.DoesNotExist:
            stats = {}
    
    context = {
        'settings': settings,
        'filter_form': filter_form,
        'quick_form': quick_form,
        'stats': stats,
        'title': 'Calendário Interno',
        'user_permissions': user_permissions
    }
    
    return render(request, 'calendar/calendar_home.html', context)


@login_required
def calendar_events_json(request):
    """
    API JSON para eventos do calendário (FullCalendar).
    """
    user_permissions = get_user_permissions(request.user)
    
    # Filtrar eventos baseado nas permissões
    if user_permissions['is_admin']:
        events = CalendarEvent.objects.all()
    else:
        # Colaboradores só veem seus próprios eventos e eventos públicos
        try:
            employee = Employee.objects.get(user=request.user)
            events = CalendarEvent.objects.filter(
                Q(employee=employee) | Q(is_private=False)
            )
        except Employee.DoesNotExist:
            events = CalendarEvent.objects.filter(is_private=False)
    
    # Aplicar filtros de data (FullCalendar envia start e end)
    start = request.GET.get('start')
    end = request.GET.get('end')
    
    if start:
        start_date = datetime.fromisoformat(start.replace('Z', '+00:00'))
        events = events.filter(end_date__gte=start_date)
    
    if end:
        end_date = datetime.fromisoformat(end.replace('Z', '+00:00'))
        events = events.filter(start_date__lte=end_date)
    
    # Aplicar outros filtros
    event_types = request.GET.getlist('event_type')
    if event_types:
        events = events.filter(event_type__in=event_types)
    
    statuses = request.GET.getlist('status')
    if statuses:
        events = events.filter(status__in=statuses)
    
    employees = request.GET.getlist('employee')
    if employees:
        events = events.filter(employee__id__in=employees)
    
    # Converter para formato FullCalendar
    events_data = []
    for event in events:
        events_data.append(event.to_fullcalendar_dict())
    
    return JsonResponse(events_data, safe=False)


@login_required
def calendar_event_detail(request, pk):
    """
    Detalhes de um evento do calendário.
    """
    event = get_object_or_404(CalendarEvent, pk=pk)
    user_permissions = get_user_permissions(request.user)
    
    # Verificar permissões
    if not user_permissions['is_admin']:
        # Colaboradores só podem ver seus próprios eventos ou eventos públicos
        if event.is_private and (not hasattr(request.user, 'employee') or request.user.employee != event.employee):
            messages.error(request, 'Você não tem permissão para acessar este evento.')
            return redirect('calendar:home')
    
    # Forms para anexos (se permitido)
    attachment_form = None
    if user_permissions['is_admin'] or (hasattr(request.user, 'employee') and request.user.employee == event.employee):
        attachment_form = CalendarAttachmentForm(user=request.user, event=event)
    
    context = {
        'event': event,
        'attachment_form': attachment_form,
        'title': event.title,
        'user_permissions': user_permissions
    }
    
    return render(request, 'calendar/event_detail.html', context)


@login_required
def calendar_event_create(request):
    """
    Criar novo evento do calendário.
    """
    if request.method == 'POST':
        form = CalendarEventForm(request.POST, user=request.user)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user
            event.save()
            form.save_m2m()  # Salvar participantes
            
            messages.success(request, f'Evento "{event.title}" criado com sucesso!')
            return redirect('calendar:event_detail', pk=event.pk)
    else:
        form = CalendarEventForm(user=request.user)
    
    context = {
        'form': form,
        'title': 'Novo Evento',
        'user_permissions': get_user_permissions(request.user)
    }
    
    return render(request, 'calendar/event_form.html', context)


@login_required
def calendar_event_edit(request, pk):
    """
    Editar evento do calendário.
    """
    event = get_object_or_404(CalendarEvent, pk=pk)
    user_permissions = get_user_permissions(request.user)
    
    # Verificar permissões
    if not user_permissions['is_admin'] and (not hasattr(request.user, 'employee') or request.user.employee != event.employee):
        messages.error(request, 'Você não tem permissão para editar este evento.')
        return redirect('calendar:event_detail', pk=pk)
    
    if request.method == 'POST':
        form = CalendarEventForm(request.POST, instance=event, user=request.user)
        if form.is_valid():
            event = form.save(commit=False)
            event.updated_by = request.user
            event.save()
            form.save_m2m()
            
            messages.success(request, f'Evento "{event.title}" atualizado com sucesso!')
            return redirect('calendar:event_detail', pk=event.pk)
    else:
        form = CalendarEventForm(instance=event, user=request.user)
    
    context = {
        'form': form,
        'event': event,
        'title': f'Editar: {event.title}',
        'user_permissions': user_permissions
    }
    
    return render(request, 'calendar/event_form.html', context)


@login_required
@user_passes_test(is_admin)
def calendar_event_approve(request, pk):
    """
    Aprovar ou rejeitar evento do calendário (apenas admins).
    """
    event = get_object_or_404(CalendarEvent, pk=pk)
    
    if not event.can_be_approved:
        messages.error(request, 'Este evento não pode ser processado.')
        return redirect('calendar:event_detail', pk=pk)
    
    if request.method == 'POST':
        form = CalendarEventApprovalForm(request.POST, instance=event)
        if form.is_valid():
            action = form.cleaned_data['action']
            
            if action == 'approve':
                event.status = 'approved'
                event.approved_by = request.user
                event.approved_at = timezone.now()
                messages.success(request, 'Evento aprovado com sucesso!')
                
                # Criar notificação
                CalendarNotification.objects.create(
                    event=event,
                    user=event.employee.user if event.employee.user else event.created_by,
                    notification_type='event_approved',
                    title=f'Evento Aprovado: {event.title}',
                    message=f'Seu evento "{event.title}" foi aprovado.'
                )
                
            else:  # reject
                event.status = 'rejected'
                event.rejection_reason = form.cleaned_data['rejection_reason']
                messages.success(request, 'Evento rejeitado.')
                
                # Criar notificação
                CalendarNotification.objects.create(
                    event=event,
                    user=event.employee.user if event.employee.user else event.created_by,
                    notification_type='event_rejected',
                    title=f'Evento Rejeitado: {event.title}',
                    message=f'Seu evento "{event.title}" foi rejeitado. Motivo: {event.rejection_reason}'
                )
            
            form.save()
            return redirect('calendar:event_detail', pk=pk)
    else:
        form = CalendarEventApprovalForm(instance=event)
    
    context = {
        'form': form,
        'event': event,
        'title': f'Processar: {event.title}',
        'user_permissions': get_user_permissions(request.user)
    }
    
    return render(request, 'calendar/event_approve.html', context)


@login_required
def calendar_event_quick_create(request):
    """
    Criação rápida de evento via AJAX.
    """
    if request.method == 'POST':
        form = QuickEventForm(request.POST, user=request.user)
        if form.is_valid():
            # Criar evento com dados básicos
            try:
                employee = Employee.objects.get(user=request.user)
            except Employee.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Usuário não associado a colaborador'})
            
            event = CalendarEvent.objects.create(
                title=form.cleaned_data['title'],
                start_date=form.cleaned_data['start_date'],
                end_date=form.cleaned_data['end_date'],
                event_type=form.cleaned_data['event_type'],
                employee=employee,
                status='pending',
                created_by=request.user
            )
            
            return JsonResponse({
                'success': True,
                'event': event.to_fullcalendar_dict(),
                'message': 'Evento criado com sucesso!'
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            })
    
    return JsonResponse({'success': False, 'error': 'Método não permitido'})


@login_required
def add_attachment(request, pk):
    """
    Adicionar anexo a um evento.
    """
    event = get_object_or_404(CalendarEvent, pk=pk)
    user_permissions = get_user_permissions(request.user)
    
    # Verificar permissões
    if not user_permissions['is_admin'] and (not hasattr(request.user, 'employee') or request.user.employee != event.employee):
        messages.error(request, 'Você não tem permissão para adicionar anexos a este evento.')
        return redirect('calendar:event_detail', pk=pk)
    
    if request.method == 'POST':
        form = CalendarAttachmentForm(
            request.POST, 
            request.FILES, 
            user=request.user, 
            event=event
        )
        if form.is_valid():
            attachment = form.save()
            messages.success(request, f'Anexo "{attachment.name}" adicionado com sucesso!')
        else:
            messages.error(request, 'Erro ao adicionar anexo.')
    
    return redirect('calendar:event_detail', pk=pk)


@login_required
def calendar_settings(request):
    """
    Configurações do calendário do usuário.
    """
    settings, created = CalendarSettings.objects.get_or_create(
        user=request.user,
        defaults={
            'default_view': 'month',
            'show_weekends': True,
        }
    )
    
    if request.method == 'POST':
        form = CalendarSettingsForm(request.POST, instance=settings)
        if form.is_valid():
            form.save()
            messages.success(request, 'Configurações salvas com sucesso!')
            return redirect('calendar:settings')
    else:
        form = CalendarSettingsForm(instance=settings)
    
    context = {
        'form': form,
        'settings': settings,
        'title': 'Configurações do Calendário',
        'user_permissions': get_user_permissions(request.user)
    }
    
    return render(request, 'calendar/settings.html', context)


@login_required
def calendar_notifications(request):
    """
    Lista de notificações do calendário.
    """
    notifications = CalendarNotification.objects.filter(
        user=request.user
    ).order_by('-created_at')
    
    # Marcar como lidas se solicitado
    if request.GET.get('mark_read'):
        notifications.filter(is_read=False).update(is_read=True, read_at=timezone.now())
        messages.success(request, 'Notificações marcadas como lidas.')
        return redirect('calendar:notifications')
    
    # Paginação
    paginator = Paginator(notifications, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'unread_count': notifications.filter(is_read=False).count(),
        'title': 'Notificações do Calendário',
        'user_permissions': get_user_permissions(request.user)
    }
    
    return render(request, 'calendar/notifications.html', context)


@login_required
@user_passes_test(is_admin)
def calendar_stats(request):
    """
    Estatísticas do calendário (apenas admins).
    """
    from django.db.models import Avg, Sum
    
    stats = {
        'total_events': CalendarEvent.objects.count(),
        'pending_events': CalendarEvent.objects.filter(status='pending').count(),
        'approved_events': CalendarEvent.objects.filter(status='approved').count(),
        'rejected_events': CalendarEvent.objects.filter(status='rejected').count(),
        'cancelled_events': CalendarEvent.objects.filter(status='cancelled').count(),
        'events_by_type': CalendarEvent.objects.values('event_type').annotate(
            count=Count('id')
        ).order_by('-count'),
        'events_by_status': CalendarEvent.objects.values('status').annotate(
            count=Count('id')
        ).order_by('-count'),
        'events_by_employee': CalendarEvent.objects.values(
            'employee__full_name'
        ).annotate(count=Count('id')).order_by('-count')[:10],
        'upcoming_events': CalendarEvent.objects.filter(
            status='approved',
            start_date__gte=timezone.now()
        ).order_by('start_date')[:10],
        'recent_events': CalendarEvent.objects.order_by('-created_at')[:10],
        'average_duration': 0,  # Será implementado posteriormente
    }
    
    context = {
        'stats': stats,
        'title': 'Estatísticas do Calendário',
        'user_permissions': get_user_permissions(request.user)
    }
    
    return render(request, 'calendar/stats.html', context)


@login_required
def calendar_event_move(request):
    """
    Mover evento via drag-and-drop (AJAX).
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            event_id = data.get('id')
            new_start = data.get('start')
            new_end = data.get('end')
            
            event = get_object_or_404(CalendarEvent, pk=event_id)
            user_permissions = get_user_permissions(request.user)
            
            # Verificar permissões
            if not user_permissions['is_admin'] and (not hasattr(request.user, 'employee') or request.user.employee != event.employee):
                return JsonResponse({'success': False, 'error': 'Sem permissão'})
            
            # Atualizar datas
            event.start_date = datetime.fromisoformat(new_start.replace('Z', '+00:00'))
            event.end_date = datetime.fromisoformat(new_end.replace('Z', '+00:00'))
            event.updated_by = request.user
            event.save()
            
            return JsonResponse({'success': True})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método não permitido'})