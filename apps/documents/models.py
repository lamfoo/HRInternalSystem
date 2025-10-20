"""
Models para requisição e geração de documentos.
"""
import os
from django.db import models
from django.contrib.auth.models import User
from apps.core.models import UserTrackingModel
from apps.employees.models import Employee


def document_upload_path(instance, filename):
    """
    Define o caminho para upload de documentos gerados.
    """
    return f'documents/{instance.document_type}/{instance.employee.id}/{filename}'


class DocumentRequest(UserTrackingModel):
    """
    Modelo para requisições de documentos pelos colaboradores.
    """
    
    DOCUMENT_TYPE_CHOICES = [
        ('declaracao_rendimentos', 'Declaração de Rendimentos'),
        ('comprovante_trabalho', 'Comprovante de Trabalho'),
        ('carta_recomendacao', 'Carta de Recomendação'),
        ('certificado_tempo_servico', 'Certificado de Tempo de Serviço'),
        ('declaracao_salario', 'Declaração de Salário'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('approved', 'Aprovado'),
        ('rejected', 'Rejeitado'),
        ('processing', 'Em Processamento'),
        ('completed', 'Concluído'),
    ]
    
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='document_requests',
        verbose_name='Colaborador'
    )
    
    document_type = models.CharField(
        max_length=50,
        choices=DOCUMENT_TYPE_CHOICES,
        verbose_name='Tipo de Documento'
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Status'
    )
    
    reason = models.TextField(
        blank=True,
        verbose_name='Motivo da Solicitação'
    )
    
    admin_notes = models.TextField(
        blank=True,
        verbose_name='Observações do Administrador'
    )
    
    document_file = models.FileField(
        upload_to=document_upload_path,
        blank=True,
        null=True,
        verbose_name='Arquivo do Documento'
    )
    
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_documents',
        verbose_name='Aprovado por'
    )
    
    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Aprovado em'
    )
    
    rejection_reason = models.TextField(
        blank=True,
        verbose_name='Motivo da Rejeição'
    )
    
    email_sent = models.BooleanField(
        default=False,
        verbose_name='Email Enviado'
    )
    
    class Meta:
        verbose_name = 'Requisição de Documento'
        verbose_name_plural = 'Requisições de Documentos'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.get_document_type_display()} - {self.employee.full_name} ({self.get_status_display()})'
    
    @property
    def can_be_approved(self):
        """
        Verifica se a requisição pode ser aprovada.
        """
        return self.status == 'pending'
    
    @property
    def can_be_rejected(self):
        """
        Verifica se a requisição pode ser rejeitada.
        """
        return self.status in ['pending', 'processing']
    
    @property
    def is_completed(self):
        """
        Verifica se a requisição foi concluída.
        """
        return self.status == 'completed'
    
    def get_file_name(self):
        """
        Retorna o nome do arquivo sem o caminho.
        """
        if self.document_file:
            return os.path.basename(self.document_file.name)
        return None
    
    def get_file_extension(self):
        """
        Retorna a extensão do arquivo.
        """
        if self.document_file:
            return os.path.splitext(self.document_file.name)[1]
        return None


class DocumentTemplate(UserTrackingModel):
    """
    Modelo para templates de documentos.
    """
    
    TEMPLATE_TYPE_CHOICES = [
        ('word', 'Microsoft Word (.docx)'),
        ('pdf', 'PDF'),
        ('html', 'HTML'),
    ]
    
    name = models.CharField(
        max_length=100,
        verbose_name='Nome do Template'
    )
    
    document_type = models.CharField(
        max_length=50,
        choices=DocumentRequest.DOCUMENT_TYPE_CHOICES,
        verbose_name='Tipo de Documento'
    )
    
    template_type = models.CharField(
        max_length=10,
        choices=TEMPLATE_TYPE_CHOICES,
        default='word',
        verbose_name='Tipo de Template'
    )
    
    template_file = models.FileField(
        upload_to='templates/',
        verbose_name='Arquivo do Template'
    )
    
    description = models.TextField(
        blank=True,
        verbose_name='Descrição'
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='Ativo'
    )
    
    variables = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Variáveis do Template',
        help_text='Variáveis disponíveis no template (formato JSON)'
    )
    
    class Meta:
        verbose_name = 'Template de Documento'
        verbose_name_plural = 'Templates de Documentos'
        ordering = ['document_type', 'name']
    
    def __str__(self):
        return f'{self.name} ({self.get_document_type_display()})'


class DocumentHistory(models.Model):
    """
    Histórico de ações realizadas em requisições de documentos.
    """
    
    ACTION_CHOICES = [
        ('created', 'Criado'),
        ('approved', 'Aprovado'),
        ('rejected', 'Rejeitado'),
        ('document_generated', 'Documento Gerado'),
        ('email_sent', 'Email Enviado'),
        ('status_changed', 'Status Alterado'),
    ]
    
    document_request = models.ForeignKey(
        DocumentRequest,
        on_delete=models.CASCADE,
        related_name='history',
        verbose_name='Requisição'
    )
    
    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
        verbose_name='Ação'
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Usuário'
    )
    
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data/Hora'
    )
    
    notes = models.TextField(
        blank=True,
        verbose_name='Observações'
    )
    
    old_status = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Status Anterior'
    )
    
    new_status = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Novo Status'
    )
    
    class Meta:
        verbose_name = 'Histórico de Documento'
        verbose_name_plural = 'Históricos de Documentos'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f'{self.get_action_display()} - {self.document_request} ({self.timestamp})'