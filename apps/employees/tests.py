"""
Testes do app employees.
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User, Group
from django.urls import reverse
from decimal import Decimal
from datetime import date
from .models import Employee
from .forms import EmployeeForm, EmployeeSearchForm


class EmployeeModelTestCase(TestCase):
    """
    Testes para o modelo Employee.
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
        
        self.employee = Employee.objects.create(
            full_name='João Silva',
            address='Rua das Flores, 123',
            id_document='123456789',
            birth_date=date(1990, 1, 1),
            email='joao@example.com',
            phone='+258 84 123 4567',
            position='Desenvolvedor',
            contract_type='clt',
            start_date=date(2020, 1, 1),
            department='TI',
            net_salary=Decimal('50000.00'),
            daily_allowance=Decimal('500.00'),
            additional_remuneration=Decimal('5000.00'),
            nuit='123456789',
            status='active',
            user=self.user
        )
    
    def test_employee_creation(self):
        """
        Testa a criação de um colaborador.
        """
        self.assertEqual(self.employee.full_name, 'João Silva')
        self.assertEqual(self.employee.position, 'Desenvolvedor')
        self.assertEqual(self.employee.status, 'active')
        self.assertTrue(self.employee.is_active)
    
    def test_employee_str(self):
        """
        Testa a representação string do colaborador.
        """
        expected = 'João Silva - Desenvolvedor'
        self.assertEqual(str(self.employee), expected)
    
    def test_total_monthly_income(self):
        """
        Testa o cálculo da renda mensal total.
        """
        # Salário + (subsídio * 22 dias) + remuneração adicional
        expected = Decimal('50000.00') + (Decimal('500.00') * 22) + Decimal('5000.00')
        self.assertEqual(self.employee.total_monthly_income, expected)
    
    def test_years_of_service(self):
        """
        Testa o cálculo dos anos de serviço.
        """
        # Considerando que o teste roda em 2024 e o funcionário começou em 2020
        expected_years = date.today().year - 2020
        if (date.today().month, date.today().day) < (1, 1):
            expected_years -= 1
        
        self.assertEqual(self.employee.years_of_service, expected_years)
    
    def test_unique_id_document(self):
        """
        Testa se o documento de identificação é único.
        """
        with self.assertRaises(Exception):
            Employee.objects.create(
                full_name='Maria Santos',
                address='Rua das Palmeiras, 456',
                id_document='123456789',  # Mesmo documento
                email='maria@example.com',
                position='Analista',
                contract_type='clt',
                start_date=date(2021, 1, 1),
                net_salary=Decimal('40000.00'),
                status='active'
            )


class EmployeeFormTestCase(TestCase):
    """
    Testes para os forms de Employee.
    """
    
    def setUp(self):
        """
        Configuração inicial para os testes.
        """
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_valid_employee_form(self):
        """
        Testa form válido de colaborador.
        """
        form_data = {
            'full_name': 'João Silva',
            'address': 'Rua das Flores, 123',
            'id_document': '123456789',
            'birth_date': '1990-01-01',
            'email': 'joao@example.com',
            'phone': '+258 84 123 4567',
            'position': 'Desenvolvedor',
            'contract_type': 'clt',
            'start_date': '2020-01-01',
            'department': 'TI',
            'net_salary': '50000.00',
            'daily_allowance': '500.00',
            'additional_remuneration': '5000.00',
            'nuit': '123456789',
            'status': 'active',
            'user': self.user.id
        }
        
        form = EmployeeForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_duplicate_id_document_validation(self):
        """
        Testa validação de documento duplicado.
        """
        # Criar primeiro colaborador
        Employee.objects.create(
            full_name='João Silva',
            address='Rua das Flores, 123',
            id_document='123456789',
            email='joao@example.com',
            position='Desenvolvedor',
            contract_type='clt',
            start_date=date(2020, 1, 1),
            net_salary=Decimal('50000.00'),
            status='active'
        )
        
        # Tentar criar segundo com mesmo documento
        form_data = {
            'full_name': 'Maria Santos',
            'address': 'Rua das Palmeiras, 456',
            'id_document': '123456789',  # Documento duplicado
            'email': 'maria@example.com',
            'position': 'Analista',
            'contract_type': 'clt',
            'start_date': '2021-01-01',
            'net_salary': '40000.00',
            'status': 'active'
        }
        
        form = EmployeeForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('id_document', form.errors)
    
    def test_employee_search_form(self):
        """
        Testa o form de busca de colaboradores.
        """
        form_data = {
            'search': 'João',
            'status': 'active',
            'department': 'TI',
            'contract_type': 'clt'
        }
        
        form = EmployeeSearchForm(data=form_data)
        self.assertTrue(form.is_valid())


class EmployeeViewsTestCase(TestCase):
    """
    Testes para as views de Employee.
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
            start_date=date(2020, 1, 1),
            net_salary=Decimal('50000.00'),
            status='active',
            user=self.employee_user
        )
    
    def test_employee_list_requires_login(self):
        """
        Testa se a lista de colaboradores requer login.
        """
        response = self.client.get(reverse('employees:list'))
        self.assertRedirects(response, f'/accounts/login/?next={reverse("employees:list")}')
    
    def test_employee_list_admin_access(self):
        """
        Testa acesso à lista de colaboradores com admin.
        """
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(reverse('employees:list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Lista de Colaboradores')
    
    def test_employee_list_employee_redirect(self):
        """
        Testa redirecionamento de colaborador para seus próprios dados.
        """
        self.client.login(username='employee', password='employeepass123')
        response = self.client.get(reverse('employees:list'))
        self.assertRedirects(response, reverse('employees:detail', kwargs={'pk': self.employee.pk}))
    
    def test_employee_detail_view(self):
        """
        Testa visualização de detalhes do colaborador.
        """
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(reverse('employees:detail', kwargs={'pk': self.employee.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'João Silva')
    
    def test_employee_create_requires_admin(self):
        """
        Testa se a criação de colaborador requer permissão de admin.
        """
        self.client.login(username='employee', password='employeepass123')
        response = self.client.get(reverse('employees:create'))
        self.assertIn(response.status_code, [302, 403])
    
    def test_employee_create_admin_access(self):
        """
        Testa acesso à criação de colaborador com admin.
        """
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(reverse('employees:create'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Novo Colaborador')