"""
Testes do app core.
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User, Group
from django.urls import reverse
from .utils import get_user_permissions, format_currency


class CoreUtilsTestCase(TestCase):
    """
    Testes para os utilitários do core.
    """
    
    def setUp(self):
        """
        Configuração inicial para os testes.
        """
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Criar grupos
        self.admin_group = Group.objects.create(name='Admin')
        self.employee_group = Group.objects.create(name='Colaborador')
    
    def test_format_currency(self):
        """
        Testa formatação de moeda.
        """
        self.assertEqual(format_currency(1000.50), "1.000,50 MT")
        self.assertEqual(format_currency(0), "0,00 MT")
        self.assertEqual(format_currency(None), "0,00 MT")
    
    def test_get_user_permissions_admin(self):
        """
        Testa permissões de usuário administrador.
        """
        self.user.groups.add(self.admin_group)
        permissions = get_user_permissions(self.user)
        
        self.assertTrue(permissions['is_admin'])
        self.assertTrue(permissions['can_manage_employees'])
        self.assertTrue(permissions['can_approve_documents'])
    
    def test_get_user_permissions_employee(self):
        """
        Testa permissões de usuário colaborador.
        """
        self.user.groups.add(self.employee_group)
        permissions = get_user_permissions(self.user)
        
        self.assertTrue(permissions['is_employee'])
        self.assertFalse(permissions['is_admin'])
        self.assertFalse(permissions['can_manage_employees'])
    
    def test_get_user_permissions_superuser(self):
        """
        Testa permissões de superusuário.
        """
        self.user.is_superuser = True
        self.user.save()
        permissions = get_user_permissions(self.user)
        
        # Superuser deve ter todas as permissões
        for permission in permissions.values():
            self.assertTrue(permission)


class DashboardViewTestCase(TestCase):
    """
    Testes para a view do dashboard.
    """
    
    def setUp(self):
        """
        Configuração inicial para os testes.
        """
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.dashboard_url = reverse('core:dashboard')
    
    def test_dashboard_requires_login(self):
        """
        Testa se o dashboard requer login.
        """
        response = self.client.get(self.dashboard_url)
        self.assertRedirects(response, f'/accounts/login/?next={self.dashboard_url}')
    
    def test_dashboard_logged_in_user(self):
        """
        Testa acesso ao dashboard com usuário logado.
        """
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.dashboard_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dashboard')
        self.assertIn('user_permissions', response.context)