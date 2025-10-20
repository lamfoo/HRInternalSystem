"""
Testes do app documents.
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User, Group
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from decimal import Decimal
from datetime import date
from apps.employees.models import Employee
from .models import DocumentRequest, DocumentTemplate, DocumentHistory
from .forms import DocumentRequestForm, DocumentApprovalForm


class DocumentRequestModelTestCase(TestCase):
    """
    Testes para o modelo DocumentRequest.
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
            email='joao@example.com',
            position='Desenvolvedor',
            contract_type='clt',
            start_date=date(2020, 1, 1),
            net_salary=Decimal('50000.00'),
            status='active',
            user=self.user
        )
        
        self.document_request = DocumentRequest.objects.create(
            employee=self.employee,
            document_type='declaracao_rendimentos',
            reason='Necessário para financiamento',
            created_by=self.user
        )
    
    def test_document_request_creation(self):
        """
        Testa a criação de uma requisição de documento.
        """
        self.assertEqual(self.document_request.employee, self.employee)
        self.assertEqual(self.document_request.document_type, 'declaracao_rendimentos')
        self.assertEqual(self.document_request.status, 'pending')
        self.assertTrue(self.document_request.can_be_approved)
    
    def test_document_request_str(self):
        """
        Testa a representação string da requisição.
        """
        expected = 'Declaração de Rendimentos - João Silva (Pendente)'
        self.assertEqual(str(self.document_request), expected)
    
    def test_can_be_approved_property(self):
        """
        Testa a propriedade can_be_approved.
        """
        self.assertTrue(self.document_request.can_be_approved)
        
        self.document_request.status = 'approved'
        self.assertFalse(self.document_request.can_be_approved)
    
    def test_can_be_rejected_property(self):
        """
        Testa a propriedade can_be_rejected.
        """
        self.assertTrue(self.document_request.can_be_rejected)
        
        self.document_request.status = 'processing'
        self.assertTrue(self.document_request.can_be_rejected)
        
        self.document_request.status = 'completed'
        self.assertFalse(self.document_request.can_be_rejected)
    
    def test_is_completed_property(self):
        """
        Testa a propriedade is_completed.
        """
        self.assertFalse(self.document_request.is_completed)
        
        self.document_request.status = 'completed'
        self.assertTrue(self.document_request.is_completed)


class DocumentTemplateModelTestCase(TestCase):
    """
    Testes para o modelo DocumentTemplate.
    """
    
    def setUp(self):
        """
        Configuração inicial para os testes.
        """
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Criar arquivo de template simulado
        template_file = SimpleUploadedFile(
            "template.docx",
            b"file_content",
            content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        
        self.template = DocumentTemplate.objects.create(
            name='Template Declaração',
            document_type='declaracao_rendimentos',
            template_type='word',
            template_file=template_file,
            description='Template para declaração de rendimentos',
            variables='{"employee_name": "Nome do colaborador"}',
            created_by=self.user
        )
    
    def test_document_template_creation(self):
        """
        Testa a criação de um template de documento.
        """
        self.assertEqual(self.template.name, 'Template Declaração')
        self.assertEqual(self.template.document_type, 'declaracao_rendimentos')
        self.assertEqual(self.template.template_type, 'word')
        self.assertTrue(self.template.is_active)
    
    def test_document_template_str(self):
        """
        Testa a representação string do template.
        """
        expected = 'Template Declaração (Declaração de Rendimentos)'
        self.assertEqual(str(self.template), expected)


class DocumentHistoryModelTestCase(TestCase):
    """
    Testes para o modelo DocumentHistory.
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
            start_date=date(2020, 1, 1),
            net_salary=Decimal('50000.00'),
            status='active'
        )
        
        self.document_request = DocumentRequest.objects.create(
            employee=self.employee,
            document_type='declaracao_rendimentos',
            created_by=self.user
        )
        
        self.history = DocumentHistory.objects.create(
            document_request=self.document_request,
            action='created',
            user=self.user,
            notes='Requisição criada'
        )
    
    def test_document_history_creation(self):
        """
        Testa a criação de um histórico de documento.
        """
        self.assertEqual(self.history.document_request, self.document_request)
        self.assertEqual(self.history.action, 'created')
        self.assertEqual(self.history.user, self.user)
        self.assertEqual(self.history.notes, 'Requisição criada')


class DocumentRequestFormTestCase(TestCase):
    """
    Testes para os forms de DocumentRequest.
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
            start_date=date(2020, 1, 1),
            net_salary=Decimal('50000.00'),
            status='active',
            user=self.user
        )
    
    def test_valid_document_request_form(self):
        """
        Testa form válido de requisição de documento.
        """
        form_data = {
            'document_type': 'declaracao_rendimentos',
            'reason': 'Necessário para financiamento'
        }
        
        form = DocumentRequestForm(data=form_data, employee=self.employee)
        self.assertTrue(form.is_valid())
    
    def test_document_request_form_save(self):
        """
        Testa salvamento do form de requisição.
        """
        form_data = {
            'document_type': 'declaracao_rendimentos',
            'reason': 'Necessário para financiamento'
        }
        
        form = DocumentRequestForm(data=form_data, employee=self.employee)
        self.assertTrue(form.is_valid())
        
        document_request = form.save()
        self.assertEqual(document_request.employee, self.employee)
        self.assertEqual(document_request.document_type, 'declaracao_rendimentos')


class DocumentApprovalFormTestCase(TestCase):
    """
    Testes para o form de aprovação de documentos.
    """
    
    def test_approval_form_approve(self):
        """
        Testa form de aprovação.
        """
        form_data = {
            'action': 'approve',
            'admin_notes': 'Aprovado conforme solicitado'
        }
        
        form = DocumentApprovalForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_approval_form_reject_without_reason(self):
        """
        Testa form de rejeição sem motivo (deve ser inválido).
        """
        form_data = {
            'action': 'reject',
            'admin_notes': 'Rejeitado'
        }
        
        form = DocumentApprovalForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('rejection_reason', form.errors)
    
    def test_approval_form_reject_with_reason(self):
        """
        Testa form de rejeição com motivo (deve ser válido).
        """
        form_data = {
            'action': 'reject',
            'admin_notes': 'Rejeitado',
            'rejection_reason': 'Documentação incompleta'
        }
        
        form = DocumentApprovalForm(data=form_data)
        self.assertTrue(form.is_valid())


class DocumentViewsTestCase(TestCase):
    """
    Testes para as views de documents.
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
        
        # Criar requisição de documento
        self.document_request = DocumentRequest.objects.create(
            employee=self.employee,
            document_type='declaracao_rendimentos',
            reason='Necessário para financiamento',
            created_by=self.employee_user
        )
    
    def test_document_request_list_requires_login(self):
        """
        Testa se a lista de requisições requer login.
        """
        response = self.client.get(reverse('documents:list'))
        self.assertRedirects(response, f'/accounts/login/?next={reverse("documents:list")}')
    
    def test_document_request_list_admin_access(self):
        """
        Testa acesso à lista de requisições com admin.
        """
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(reverse('documents:list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Requisições de Documentos')
    
    def test_document_request_detail_view(self):
        """
        Testa visualização de detalhes da requisição.
        """
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(reverse('documents:detail', kwargs={'pk': self.document_request.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Declaração de Rendimentos')
    
    def test_document_request_create_view(self):
        """
        Testa criação de requisição de documento.
        """
        self.client.login(username='employee', password='employeepass123')
        response = self.client.get(reverse('documents:create'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Nova Requisição de Documento')
    
    def test_document_request_approve_requires_admin(self):
        """
        Testa se a aprovação requer permissão de admin.
        """
        self.client.login(username='employee', password='employeepass123')
        response = self.client.get(reverse('documents:approve', kwargs={'pk': self.document_request.pk}))
        self.assertIn(response.status_code, [302, 403])
    
    def test_document_request_approve_admin_access(self):
        """
        Testa acesso à aprovação com admin.
        """
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(reverse('documents:approve', kwargs={'pk': self.document_request.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Processar')