"""
Testes do app calendar.
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User, Group
from django.urls import reverse
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
from apps.employees.models import Employee
from .models import CalendarEvent, CalendarAttachment, CalendarNotification, CalendarSettings
from .forms import CalendarEventForm, CalendarEventApprovalForm, QuickEventForm


class CalendarEventModelTestCase(TestCase):
    """
    Testes para o modelo CalendarEvent.
    """
    
    def setUp(self):
        """
        Configuração inicial para os testes.
        """
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        self.employee = Employee.objects.create(
            full_name='João Silva',
            address='Rua das Flores, 123',
            id_document='123456789',
            email='joao@example.com',
            position='Desenvolvedor',
            contract_type='clt',
            start_date=timezone.now().date(),
            net_salary=Decimal('50000.00'),
            status='active',
            user=self.user
        )
        
        self.event = CalendarEvent.objects.create(
            title='Reunião de Equipe',
            description='Reunião semanal da equipe de desenvolvimento',
            event_type='reuniao',
            start_date=timezone.now() + timedelta(days=1),
            end_date=timezone.now() + timedelta(days=1, hours=2),
            employee=self.employee,
            status='pending',
            created_by=self.user
        )
    
    def test_calendar_event_creation(self):
        """
        Testa a criação de um evento.
        """
        self.assertEqual(self.event.title, 'Reunião de Equipe')
        self.assertEqual(self.event.employee, self.employee)
        self.assertEqual(self.event.event_type, 'reuniao')
        self.assertEqual(self.event.status, 'pending')
        self.assertTrue(self.event.is_pending)
        self.assertFalse(self.event.is_approved)
    
    def test_calendar_event_str(self):
        """
        Testa a representação string do evento.
        """
        expected = f'Reunião de Equipe - João Silva ({self.event.start_date.strftime("%d/%m/%Y")})'
        self.assertEqual(str(self.event), expected)
    
    def test_duration_hours_property(self):
        """
        Testa o cálculo da duração em horas.
        """
        self.assertEqual(self.event.duration_hours, 2.0)
    
    def test_can_be_approved_property(self):
        """
        Testa a propriedade can_be_approved.
        """
        self.assertTrue(self.event.can_be_approved)
        
        self.event.status = 'approved'
        self.assertFalse(self.event.can_be_approved)
    
    def test_can_be_cancelled_property(self):
        """
        Testa a propriedade can_be_cancelled.
        """
        self.assertTrue(self.event.can_be_cancelled)
        
        self.event.status = 'cancelled'
        self.assertFalse(self.event.can_be_cancelled)
    
    def test_get_color_by_type(self):
        """
        Testa a cor baseada no tipo de evento.
        """
        self.assertEqual(self.event.get_color_by_type(), '#6f42c1')  # Cor para reunião
    
    def test_to_fullcalendar_dict(self):
        """
        Testa a conversão para formato FullCalendar.
        """
        fc_dict = self.event.to_fullcalendar_dict()
        
        self.assertEqual(fc_dict['id'], self.event.id)
        self.assertEqual(fc_dict['title'], self.event.title)
        self.assertEqual(fc_dict['status'], self.event.status)
        self.assertEqual(fc_dict['eventType'], self.event.event_type)
        self.assertEqual(fc_dict['employee'], self.employee.full_name)
    
    def test_event_validation(self):
        """
        Testa validações do evento.
        """
        # Teste com data de início posterior à data de término
        event = CalendarEvent(
            title='Evento Inválido',
            start_date=timezone.now() + timedelta(days=2),
            end_date=timezone.now() + timedelta(days=1),  # Anterior ao início
            employee=self.employee
        )
        
        with self.assertRaises(Exception):
            event.full_clean()


class CalendarNotificationModelTestCase(TestCase):
    """
    Testes para o modelo CalendarNotification.
    """
    
    def setUp(self):
        """
        Configuração inicial para os testes.
        """
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        self.employee = Employee.objects.create(
            full_name='João Silva',
            address='Rua das Flores, 123',
            id_document='123456789',
            email='joao@example.com',
            position='Desenvolvedor',
            contract_type='clt',
            start_date=timezone.now().date(),
            net_salary=Decimal('50000.00'),
            status='active'
        )
        
        self.event = CalendarEvent.objects.create(
            title='Reunião de Equipe',
            start_date=timezone.now() + timedelta(days=1),
            end_date=timezone.now() + timedelta(days=1, hours=2),
            employee=self.employee,
            created_by=self.user
        )
        
        self.notification = CalendarNotification.objects.create(
            event=self.event,
            user=self.user,
            notification_type='event_created',
            title='Evento Criado',
            message='Seu evento foi criado com sucesso.'
        )
    
    def test_calendar_notification_creation(self):
        """
        Testa a criação de uma notificação.
        """
        self.assertEqual(self.notification.event, self.event)
        self.assertEqual(self.notification.user, self.user)
        self.assertEqual(self.notification.notification_type, 'event_created')
        self.assertFalse(self.notification.is_read)
    
    def test_mark_as_read(self):
        """
        Testa marcar notificação como lida.
        """
        self.assertFalse(self.notification.is_read)
        self.assertIsNone(self.notification.read_at)
        
        self.notification.mark_as_read()
        
        self.assertTrue(self.notification.is_read)
        self.assertIsNotNone(self.notification.read_at)


class CalendarSettingsModelTestCase(TestCase):
    """
    Testes para o modelo CalendarSettings.
    """
    
    def setUp(self):
        """
        Configuração inicial para os testes.
        """
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        self.settings = CalendarSettings.objects.create(
            user=self.user,
            default_view='week',
            show_weekends=False,
            email_notifications=True
        )
    
    def test_calendar_settings_creation(self):
        """
        Testa a criação de configurações do calendário.
        """
        self.assertEqual(self.settings.user, self.user)
        self.assertEqual(self.settings.default_view, 'week')
        self.assertFalse(self.settings.show_weekends)
        self.assertTrue(self.settings.email_notifications)
    
    def test_calendar_settings_str(self):
        """
        Testa a representação string das configurações.
        """
        expected = f'Configurações de {self.user.username}'
        self.assertEqual(str(self.settings), expected)


class CalendarEventFormTestCase(TestCase):
    """
    Testes para os forms de CalendarEvent.
    """
    
    def setUp(self):
        """
        Configuração inicial para os testes.
        """
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        self.employee = Employee.objects.create(
            full_name='João Silva',
            address='Rua das Flores, 123',
            id_document='123456789',
            email='joao@example.com',
            position='Desenvolvedor',
            contract_type='clt',
            start_date=timezone.now().date(),
            net_salary=Decimal('50000.00'),
            status='active',
            user=self.user
        )
    
    def test_valid_calendar_event_form(self):
        """
        Testa form válido de evento do calendário.
        """
        start_date = timezone.now() + timedelta(days=1)
        end_date = start_date + timedelta(hours=2)
        
        form_data = {
            'title': 'Reunião de Equipe',
            'description': 'Reunião semanal da equipe',
            'event_type': 'reuniao',
            'start_date': start_date.strftime('%Y-%m-%dT%H:%M'),
            'end_date': end_date.strftime('%Y-%m-%dT%H:%M'),
            'all_day': False,
            'employee': self.employee.id,
            'status': 'pending',
            'priority': 'medium',
            'location': 'Sala de Reuniões',
            'color': '#007bff',
            'is_private': False
        }
        
        form = CalendarEventForm(data=form_data, user=self.user)
        self.assertTrue(form.is_valid())
    
    def test_invalid_date_range(self):
        """
        Testa form com data de início posterior à data de término.
        """
        start_date = timezone.now() + timedelta(days=2)
        end_date = timezone.now() + timedelta(days=1)  # Anterior ao início
        
        form_data = {
            'title': 'Evento Inválido',
            'event_type': 'outro',
            'start_date': start_date.strftime('%Y-%m-%dT%H:%M'),
            'end_date': end_date.strftime('%Y-%m-%dT%H:%M'),
            'employee': self.employee.id,
            'status': 'pending',
            'priority': 'medium'
        }
        
        form = CalendarEventForm(data=form_data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('A data de início deve ser anterior', str(form.errors))


class QuickEventFormTestCase(TestCase):
    """
    Testes para o form de criação rápida de eventos.
    """
    
    def setUp(self):
        """
        Configuração inicial para os testes.
        """
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_valid_quick_event_form(self):
        """
        Testa form válido de criação rápida.
        """
        start_date = timezone.now() + timedelta(days=1)
        end_date = start_date + timedelta(hours=1)
        
        form_data = {
            'title': 'Evento Rápido',
            'start_date': start_date.strftime('%Y-%m-%dT%H:%M'),
            'end_date': end_date.strftime('%Y-%m-%dT%H:%M'),
            'event_type': 'outro'
        }
        
        form = QuickEventForm(data=form_data, user=self.user)
        self.assertTrue(form.is_valid())


class CalendarViewsTestCase(TestCase):
    """
    Testes para as views do calendar.
    """
    
    def setUp(self):
        """
        Configuração inicial para os testes.
        """
        self.client = Client()
        
        # Criar usuário admin
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            is_superuser=True
        )
        
        # Criar usuário colaborador
        self.employee_user = User.objects.create_user(
            username='employee',
            email='employee@example.com',
            password='employeepass123'
        )
        
        # Criar grupos
        self.admin_group = Group.objects.create(name='Admin')
        self.employee_group = Group.objects.create(name='Colaborador')
        
        # Criar colaborador
        self.employee = Employee.objects.create(
            full_name='João Silva',
            address='Rua das Flores, 123',
            id_document='123456789',
            email='joao@example.com',
            position='Desenvolvedor',
            contract_type='clt',
            start_date=timezone.now().date(),
            net_salary=Decimal('50000.00'),
            status='active',
            user=self.employee_user
        )
        
        # Criar evento
        self.event = CalendarEvent.objects.create(
            title='Reunião de Equipe',
            start_date=timezone.now() + timedelta(days=1),
            end_date=timezone.now() + timedelta(days=1, hours=2),
            employee=self.employee,
            status='pending',
            created_by=self.employee_user
        )
    
    def test_calendar_home_requires_login(self):
        """
        Testa se a home do calendário requer login.
        """
        response = self.client.get(reverse('calendar:home'))
        self.assertRedirects(response, f'/accounts/login/?next={reverse("calendar:home")}')
    
    def test_calendar_home_logged_in(self):
        """
        Testa acesso à home com usuário logado.
        """
        self.client.login(username='employee', password='employeepass123')
        response = self.client.get(reverse('calendar:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Calendário Interno')
    
    def test_calendar_events_json(self):
        """
        Testa API JSON de eventos.
        """
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(reverse('calendar:events_json'))
        self.assertEqual(response.status_code, 200)
        
        # Verificar se retorna JSON válido
        data = response.json()
        self.assertIsInstance(data, list)
    
    def test_calendar_event_detail_view(self):
        """
        Testa visualização de detalhes do evento.
        """
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(reverse('calendar:event_detail', kwargs={'pk': self.event.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.event.title)
    
    def test_calendar_event_create_view(self):
        """
        Testa criação de evento do calendário.
        """
        self.client.login(username='employee', password='employeepass123')
        response = self.client.get(reverse('calendar:event_create'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Novo Evento')
    
    def test_calendar_event_approve_requires_admin(self):
        """
        Testa se a aprovação requer permissão de admin.
        """
        self.client.login(username='employee', password='employeepass123')
        response = self.client.get(reverse('calendar:event_approve', kwargs={'pk': self.event.pk}))
        self.assertIn(response.status_code, [302, 403])
    
    def test_calendar_event_approve_admin_access(self):
        """
        Testa acesso à aprovação com admin.
        """
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(reverse('calendar:event_approve', kwargs={'pk': self.event.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Processar')
    
    def test_calendar_settings_view(self):
        """
        Testa visualização de configurações do calendário.
        """
        self.client.login(username='employee', password='employeepass123')
        response = self.client.get(reverse('calendar:settings'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Configurações do Calendário')
    
    def test_calendar_notifications_view(self):
        """
        Testa visualização de notificações.
        """
        # Criar notificação
        CalendarNotification.objects.create(
            event=self.event,
            user=self.employee_user,
            notification_type='event_created',
            title='Evento Criado',
            message='Seu evento foi criado.'
        )
        
        self.client.login(username='employee', password='employeepass123')
        response = self.client.get(reverse('calendar:notifications'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Notificações do Calendário')