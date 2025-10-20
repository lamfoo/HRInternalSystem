"""
Testes do app knowledge_base.
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User, Group
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import KnowledgeEntry, KnowledgeCategory, KnowledgeComment, KnowledgeAttachment, KnowledgeRating
from .forms import KnowledgeEntryForm, KnowledgeCategoryForm, KnowledgeCommentForm


class KnowledgeCategoryModelTestCase(TestCase):
    """
    Testes para o modelo KnowledgeCategory.
    """
    
    def setUp(self):
        """
        Configuração inicial para os testes.
        """
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        self.category = KnowledgeCategory.objects.create(
            name='Tecnologia',
            description='Categoria para assuntos de tecnologia',
            color='#007bff',
            created_by=self.user
        )
    
    def test_knowledge_category_creation(self):
        """
        Testa a criação de uma categoria.
        """
        self.assertEqual(self.category.name, 'Tecnologia')
        self.assertEqual(self.category.color, '#007bff')
        self.assertTrue(self.category.is_active)
    
    def test_knowledge_category_str(self):
        """
        Testa a representação string da categoria.
        """
        self.assertEqual(str(self.category), 'Tecnologia')
    
    def test_get_entries_count(self):
        """
        Testa o contador de entradas da categoria.
        """
        # Inicialmente deve ser 0
        self.assertEqual(self.category.get_entries_count(), 0)
        
        # Criar entrada publicada
        KnowledgeEntry.objects.create(
            title='Teste',
            problem_description='Problema teste',
            solution='Solução teste',
            category=self.category,
            author=self.user,
            status='published'
        )
        
        # Agora deve ser 1
        self.assertEqual(self.category.get_entries_count(), 1)


class KnowledgeEntryModelTestCase(TestCase):
    """
    Testes para o modelo KnowledgeEntry.
    """
    
    def setUp(self):
        """
        Configuração inicial para os testes.
        """
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        self.category = KnowledgeCategory.objects.create(
            name='Tecnologia',
            created_by=self.user
        )
        
        self.entry = KnowledgeEntry.objects.create(
            title='Como resolver problema X',
            problem_description='Descrição do problema X',
            solution='Solução para o problema X',
            category=self.category,
            tags='python, django, web',
            author=self.user,
            status='published'
        )
    
    def test_knowledge_entry_creation(self):
        """
        Testa a criação de uma entrada.
        """
        self.assertEqual(self.entry.title, 'Como resolver problema X')
        self.assertEqual(self.entry.author, self.user)
        self.assertEqual(self.entry.category, self.category)
        self.assertEqual(self.entry.status, 'published')
        self.assertTrue(self.entry.is_published)
    
    def test_knowledge_entry_str(self):
        """
        Testa a representação string da entrada.
        """
        self.assertEqual(str(self.entry), 'Como resolver problema X')
    
    def test_get_tags_list(self):
        """
        Testa a conversão de tags em lista.
        """
        expected_tags = ['python', 'django', 'web']
        self.assertEqual(self.entry.get_tags_list(), expected_tags)
    
    def test_increment_views(self):
        """
        Testa o incremento de visualizações.
        """
        initial_views = self.entry.views_count
        self.entry.increment_views()
        self.assertEqual(self.entry.views_count, initial_views + 1)
    
    def test_get_absolute_url(self):
        """
        Testa a URL absoluta da entrada.
        """
        expected_url = reverse('knowledge_base:detail', kwargs={'pk': self.entry.pk})
        self.assertEqual(self.entry.get_absolute_url(), expected_url)


class KnowledgeCommentModelTestCase(TestCase):
    """
    Testes para o modelo KnowledgeComment.
    """
    
    def setUp(self):
        """
        Configuração inicial para os testes.
        """
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        self.entry = KnowledgeEntry.objects.create(
            title='Teste',
            problem_description='Problema teste',
            solution='Solução teste',
            author=self.user,
            status='published'
        )
        
        self.comment = KnowledgeComment.objects.create(
            entry=self.entry,
            author=self.user,
            content='Este é um comentário de teste',
            created_by=self.user
        )
    
    def test_knowledge_comment_creation(self):
        """
        Testa a criação de um comentário.
        """
        self.assertEqual(self.comment.entry, self.entry)
        self.assertEqual(self.comment.author, self.user)
        self.assertEqual(self.comment.content, 'Este é um comentário de teste')
        self.assertTrue(self.comment.is_approved)
        self.assertFalse(self.comment.is_reply)
    
    def test_knowledge_comment_str(self):
        """
        Testa a representação string do comentário.
        """
        expected = f'Comentário de {self.user.username} em {self.entry.title}'
        self.assertEqual(str(self.comment), expected)
    
    def test_comment_reply(self):
        """
        Testa resposta a comentário.
        """
        reply = KnowledgeComment.objects.create(
            entry=self.entry,
            author=self.user,
            content='Esta é uma resposta',
            parent=self.comment,
            created_by=self.user
        )
        
        self.assertTrue(reply.is_reply)
        self.assertEqual(reply.parent, self.comment)
        self.assertIn(reply, self.comment.get_replies())


class KnowledgeRatingModelTestCase(TestCase):
    """
    Testes para o modelo KnowledgeRating.
    """
    
    def setUp(self):
        """
        Configuração inicial para os testes.
        """
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        self.entry = KnowledgeEntry.objects.create(
            title='Teste',
            problem_description='Problema teste',
            solution='Solução teste',
            author=self.user,
            status='published'
        )
        
        self.rating = KnowledgeRating.objects.create(
            entry=self.entry,
            user=self.user,
            rating=5,
            comment='Excelente entrada!'
        )
    
    def test_knowledge_rating_creation(self):
        """
        Testa a criação de uma avaliação.
        """
        self.assertEqual(self.rating.entry, self.entry)
        self.assertEqual(self.rating.user, self.user)
        self.assertEqual(self.rating.rating, 5)
        self.assertEqual(self.rating.comment, 'Excelente entrada!')
    
    def test_knowledge_rating_str(self):
        """
        Testa a representação string da avaliação.
        """
        expected = f'{self.user.username} - 5 estrelas para {self.entry.title}'
        self.assertEqual(str(self.rating), expected)


class KnowledgeEntryFormTestCase(TestCase):
    """
    Testes para os forms de KnowledgeEntry.
    """
    
    def setUp(self):
        """
        Configuração inicial para os testes.
        """
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        self.category = KnowledgeCategory.objects.create(
            name='Tecnologia',
            created_by=self.user
        )
    
    def test_valid_knowledge_entry_form(self):
        """
        Testa form válido de entrada de conhecimento.
        """
        form_data = {
            'title': 'Como resolver problema X',
            'problem_description': 'Descrição detalhada do problema',
            'solution': 'Solução detalhada para o problema',
            'category': self.category.id,
            'tags': 'python, django, web',
            'status': 'draft',
            'priority': 'medium',
            'is_featured': False
        }
        
        form = KnowledgeEntryForm(data=form_data, user=self.user)
        self.assertTrue(form.is_valid())
    
    def test_knowledge_entry_form_save(self):
        """
        Testa salvamento do form de entrada.
        """
        form_data = {
            'title': 'Como resolver problema X',
            'problem_description': 'Descrição detalhada do problema',
            'solution': 'Solução detalhada para o problema',
            'category': self.category.id,
            'tags': 'python, django, web',
            'status': 'draft',
            'priority': 'medium',
            'is_featured': False
        }
        
        form = KnowledgeEntryForm(data=form_data, user=self.user)
        self.assertTrue(form.is_valid())
        
        entry = form.save()
        self.assertEqual(entry.title, 'Como resolver problema X')
        self.assertEqual(entry.author, self.user)
        self.assertEqual(entry.category, self.category)


class KnowledgeCategoryFormTestCase(TestCase):
    """
    Testes para o form de KnowledgeCategory.
    """
    
    def test_valid_knowledge_category_form(self):
        """
        Testa form válido de categoria.
        """
        form_data = {
            'name': 'Nova Categoria',
            'description': 'Descrição da nova categoria',
            'color': '#ff0000',
            'is_active': True
        }
        
        form = KnowledgeCategoryForm(data=form_data)
        self.assertTrue(form.is_valid())


class KnowledgeViewsTestCase(TestCase):
    """
    Testes para as views de knowledge_base.
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
        self.user = User.objects.create_user(
            username='user',
            email='user@example.com',
            password='userpass123'
        )
        
        # Criar grupos
        self.admin_group = Group.objects.create(name='Admin')
        self.employee_group = Group.objects.create(name='Colaborador')
        
        # Criar categoria
        self.category = KnowledgeCategory.objects.create(
            name='Tecnologia',
            created_by=self.admin_user
        )
        
        # Criar entrada
        self.entry = KnowledgeEntry.objects.create(
            title='Como resolver problema X',
            problem_description='Descrição do problema X',
            solution='Solução para o problema X',
            category=self.category,
            author=self.user,
            status='published'
        )
    
    def test_knowledge_base_home_requires_login(self):
        """
        Testa se a home da base de conhecimento requer login.
        """
        response = self.client.get(reverse('knowledge_base:home'))
        self.assertRedirects(response, f'/accounts/login/?next={reverse("knowledge_base:home")}')
    
    def test_knowledge_base_home_logged_in(self):
        """
        Testa acesso à home com usuário logado.
        """
        self.client.login(username='user', password='userpass123')
        response = self.client.get(reverse('knowledge_base:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Base de Conhecimento')
    
    def test_knowledge_entry_detail_view(self):
        """
        Testa visualização de detalhes da entrada.
        """
        self.client.login(username='user', password='userpass123')
        response = self.client.get(reverse('knowledge_base:detail', kwargs={'pk': self.entry.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.entry.title)
    
    def test_knowledge_entry_create_view(self):
        """
        Testa criação de entrada de conhecimento.
        """
        self.client.login(username='user', password='userpass123')
        response = self.client.get(reverse('knowledge_base:create'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Nova Entrada')
    
    def test_knowledge_entry_edit_author_access(self):
        """
        Testa edição de entrada pelo autor.
        """
        self.client.login(username='user', password='userpass123')
        response = self.client.get(reverse('knowledge_base:edit', kwargs={'pk': self.entry.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Editar')
    
    def test_knowledge_category_create_requires_admin(self):
        """
        Testa se a criação de categoria requer permissão de admin.
        """
        self.client.login(username='user', password='userpass123')
        response = self.client.get(reverse('knowledge_base:category_create'))
        self.assertIn(response.status_code, [302, 403])
    
    def test_knowledge_category_create_admin_access(self):
        """
        Testa acesso à criação de categoria com admin.
        """
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(reverse('knowledge_base:category_create'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Nova Categoria')