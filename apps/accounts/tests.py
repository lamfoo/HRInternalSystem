"""
Testes do app accounts.
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User, Group
from django.urls import reverse
from .models import UserProfile
from .forms import CustomLoginForm, UserRegistrationForm, UserProfileForm


class UserProfileModelTestCase(TestCase):
    """
    Testes para o modelo UserProfile.
    """
    
    def setUp(self):
        """
        Configuração inicial para os testes.
        """
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
    
    def test_user_profile_creation(self):
        """
        Testa se o perfil é criado automaticamente via signal.
        """
        self.assertTrue(hasattr(self.user, 'profile'))
        self.assertIsInstance(self.user.profile, UserProfile)
    
    def test_user_profile_str(self):
        """
        Testa a representação string do perfil.
        """
        expected = 'Perfil de Test User'
        self.assertEqual(str(self.user.profile), expected)
    
    def test_full_name_property(self):
        """
        Testa a propriedade full_name.
        """
        self.assertEqual(self.user.profile.full_name, 'Test User')
        
        # Teste com usuário sem nome completo
        user_no_name = User.objects.create_user(
            username='noname',
            password='testpass123'
        )
        self.assertEqual(user_no_name.profile.full_name, 'noname')


class CustomLoginFormTestCase(TestCase):
    """
    Testes para o form de login customizado.
    """
    
    def setUp(self):
        """
        Configuração inicial para os testes.
        """
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_valid_login_form(self):
        """
        Testa form de login válido.
        """
        form_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        form = CustomLoginForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_invalid_login_form(self):
        """
        Testa form de login inválido.
        """
        form_data = {
            'username': 'testuser',
            'password': 'wrongpass'
        }
        form = CustomLoginForm(data=form_data)
        self.assertFalse(form.is_valid())


class UserRegistrationFormTestCase(TestCase):
    """
    Testes para o form de registro de usuário.
    """
    
    def test_valid_registration_form(self):
        """
        Testa form de registro válido.
        """
        form_data = {
            'username': 'newuser',
            'first_name': 'New',
            'last_name': 'User',
            'email': 'newuser@example.com',
            'password1': 'complexpass123',
            'password2': 'complexpass123'
        }
        form = UserRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_password_mismatch(self):
        """
        Testa form com senhas diferentes.
        """
        form_data = {
            'username': 'newuser',
            'first_name': 'New',
            'last_name': 'User',
            'email': 'newuser@example.com',
            'password1': 'complexpass123',
            'password2': 'differentpass123'
        }
        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())


class AccountsViewsTestCase(TestCase):
    """
    Testes para as views do accounts.
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
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            is_superuser=True
        )
        self.admin_group = Group.objects.create(name='Admin')
    
    def test_login_view_get(self):
        """
        Testa acesso à página de login.
        """
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Login')
    
    def test_login_view_post_valid(self):
        """
        Testa login com credenciais válidas.
        """
        response = self.client.post(reverse('accounts:login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertRedirects(response, reverse('core:dashboard'))
    
    def test_login_view_post_invalid(self):
        """
        Testa login com credenciais inválidas.
        """
        response = self.client.post(reverse('accounts:login'), {
            'username': 'testuser',
            'password': 'wrongpass'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'inválidos')
    
    def test_profile_view_requires_login(self):
        """
        Testa se a view de perfil requer login.
        """
        response = self.client.get(reverse('accounts:profile'))
        self.assertRedirects(response, f'/accounts/login/?next={reverse("accounts:profile")}')
    
    def test_profile_view_logged_in(self):
        """
        Testa acesso à view de perfil com usuário logado.
        """
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Meu Perfil')
    
    def test_create_user_requires_admin(self):
        """
        Testa se a criação de usuário requer permissão de admin.
        """
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('accounts:create_user'))
        # Deve redirecionar ou retornar 403
        self.assertIn(response.status_code, [302, 403])
    
    def test_create_user_admin_access(self):
        """
        Testa acesso à criação de usuário com admin.
        """
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(reverse('accounts:create_user'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Criar Novo Usuário')