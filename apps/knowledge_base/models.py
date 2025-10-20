"""
Models para a base de conhecimento.
"""
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from apps.core.models import UserTrackingModel


def knowledge_attachment_path(instance, filename):
    """
    Define o caminho para upload de anexos da base de conhecimento.
    """
    return f'knowledge_base/{instance.entry.id}/{filename}'


class KnowledgeCategory(UserTrackingModel):
    """
    Categorias para organizar entradas da base de conhecimento.
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Nome da Categoria'
    )
    
    description = models.TextField(
        blank=True,
        verbose_name='Descrição'
    )
    
    color = models.CharField(
        max_length=7,
        default='#007bff',
        verbose_name='Cor (Hex)',
        help_text='Cor em formato hexadecimal (ex: #007bff)'
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='Ativa'
    )
    
    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_entries_count(self):
        """
        Retorna o número de entradas nesta categoria.
        """
        return self.entries.filter(status='published').count()


class KnowledgeEntry(UserTrackingModel):
    """
    Entradas da base de conhecimento.
    """
    
    STATUS_CHOICES = [
        ('draft', 'Rascunho'),
        ('review', 'Em Revisão'),
        ('published', 'Publicado'),
        ('archived', 'Arquivado'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Baixa'),
        ('medium', 'Média'),
        ('high', 'Alta'),
        ('urgent', 'Urgente'),
    ]
    
    title = models.CharField(
        max_length=200,
        verbose_name='Título'
    )
    
    problem_description = models.TextField(
        verbose_name='Descrição do Problema'
    )
    
    solution = models.TextField(
        verbose_name='Solução'
    )
    
    category = models.ForeignKey(
        KnowledgeCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='entries',
        verbose_name='Categoria'
    )
    
    tags = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Tags',
        help_text='Separe as tags com vírgulas'
    )
    
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='knowledge_entries',
        verbose_name='Autor'
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name='Status'
    )
    
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='medium',
        verbose_name='Prioridade'
    )
    
    views_count = models.PositiveIntegerField(
        default=0,
        verbose_name='Visualizações'
    )
    
    is_featured = models.BooleanField(
        default=False,
        verbose_name='Destacado'
    )
    
    published_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Publicado em'
    )
    
    class Meta:
        verbose_name = 'Entrada de Conhecimento'
        verbose_name_plural = 'Entradas de Conhecimento'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        """
        Retorna a URL absoluta da entrada.
        """
        return reverse('knowledge_base:detail', kwargs={'pk': self.pk})
    
    @property
    def is_published(self):
        """
        Verifica se a entrada está publicada.
        """
        return self.status == 'published'
    
    def get_tags_list(self):
        """
        Retorna as tags como uma lista.
        """
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
        return []
    
    def increment_views(self):
        """
        Incrementa o contador de visualizações.
        """
        self.views_count += 1
        self.save(update_fields=['views_count'])
    
    def get_comments_count(self):
        """
        Retorna o número de comentários.
        """
        return self.comments.count()
    
    def get_attachments_count(self):
        """
        Retorna o número de anexos.
        """
        return self.attachments.count()


class KnowledgeAttachment(models.Model):
    """
    Anexos para entradas da base de conhecimento.
    """
    entry = models.ForeignKey(
        KnowledgeEntry,
        on_delete=models.CASCADE,
        related_name='attachments',
        verbose_name='Entrada'
    )
    
    file = models.FileField(
        upload_to=knowledge_attachment_path,
        verbose_name='Arquivo'
    )
    
    name = models.CharField(
        max_length=255,
        verbose_name='Nome do Arquivo'
    )
    
    description = models.CharField(
        max_length=500,
        blank=True,
        verbose_name='Descrição'
    )
    
    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Enviado em'
    )
    
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Enviado por'
    )
    
    class Meta:
        verbose_name = 'Anexo'
        verbose_name_plural = 'Anexos'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_file_size(self):
        """
        Retorna o tamanho do arquivo em formato legível.
        """
        try:
            size = self.file.size
            for unit in ['bytes', 'KB', 'MB', 'GB']:
                if size < 1024.0:
                    return f"{size:.1f} {unit}"
                size /= 1024.0
            return f"{size:.1f} TB"
        except:
            return "Tamanho desconhecido"
    
    def get_file_extension(self):
        """
        Retorna a extensão do arquivo.
        """
        import os
        return os.path.splitext(self.file.name)[1].lower()


class KnowledgeComment(UserTrackingModel):
    """
    Comentários nas entradas da base de conhecimento.
    """
    entry = models.ForeignKey(
        KnowledgeEntry,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Entrada'
    )
    
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Autor'
    )
    
    content = models.TextField(
        verbose_name='Comentário'
    )
    
    is_solution = models.BooleanField(
        default=False,
        verbose_name='É uma solução?',
        help_text='Marque se este comentário resolve o problema'
    )
    
    is_approved = models.BooleanField(
        default=True,
        verbose_name='Aprovado'
    )
    
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies',
        verbose_name='Comentário Pai'
    )
    
    class Meta:
        verbose_name = 'Comentário'
        verbose_name_plural = 'Comentários'
        ordering = ['created_at']
    
    def __str__(self):
        return f'Comentário de {self.author.username} em {self.entry.title}'
    
    @property
    def is_reply(self):
        """
        Verifica se é uma resposta a outro comentário.
        """
        return self.parent is not None
    
    def get_replies(self):
        """
        Retorna as respostas a este comentário.
        """
        return self.replies.filter(is_approved=True).order_by('created_at')


class KnowledgeRating(models.Model):
    """
    Avaliações das entradas da base de conhecimento.
    """
    RATING_CHOICES = [
        (1, 'Muito Ruim'),
        (2, 'Ruim'),
        (3, 'Regular'),
        (4, 'Bom'),
        (5, 'Muito Bom'),
    ]
    
    entry = models.ForeignKey(
        KnowledgeEntry,
        on_delete=models.CASCADE,
        related_name='ratings',
        verbose_name='Entrada'
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Usuário'
    )
    
    rating = models.PositiveSmallIntegerField(
        choices=RATING_CHOICES,
        verbose_name='Avaliação'
    )
    
    comment = models.TextField(
        blank=True,
        verbose_name='Comentário da Avaliação'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Criado em'
    )
    
    class Meta:
        verbose_name = 'Avaliação'
        verbose_name_plural = 'Avaliações'
        unique_together = ['entry', 'user']
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.user.username} - {self.rating} estrelas para {self.entry.title}'