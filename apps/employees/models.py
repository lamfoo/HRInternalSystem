"""
Models para o cadastro de colaboradores.
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal
from apps.core.models import UserTrackingModel


class Employee(UserTrackingModel):
    """
    Modelo para colaboradores da empresa.
    """
    
    CONTRACT_TYPE_CHOICES = [
        ('clt', 'CLT - Consolidação das Leis do Trabalho'),
        ('temporario', 'Contrato Temporário'),
        ('terceirizado', 'Terceirizado'),
        ('estagio', 'Estágio'),
        ('consultoria', 'Consultoria'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Ativo'),
        ('inactive', 'Inativo'),
        ('suspended', 'Suspenso'),
        ('vacation', 'Férias'),
    ]
    
    # Informações pessoais
    full_name = models.CharField(
        max_length=200,
        verbose_name='Nome Completo'
    )
    
    address = models.TextField(
        verbose_name='Endereço'
    )
    
    id_document = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Documento de Identificação'
    )
    
    birth_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Data de Nascimento'
    )
    
    email = models.EmailField(
        verbose_name='Email'
    )
    
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Telefone'
    )
    
    # Informações profissionais
    position = models.CharField(
        max_length=100,
        verbose_name='Cargo'
    )
    
    contract_type = models.CharField(
        max_length=20,
        choices=CONTRACT_TYPE_CHOICES,
        default='clt',
        verbose_name='Tipo de Contrato'
    )
    
    start_date = models.DateField(
        verbose_name='Data de Início'
    )
    
    department = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Departamento'
    )
    
    # Informações salariais
    net_salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='Salário Líquido'
    )
    
    daily_allowance = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Subsídio de Alimentação'
    )
    
    additional_remuneration = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Remuneração Adicional'
    )
    
    # Informações fiscais
    nuit = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='NUIT (Número Único de Identificação Tributária)'
    )
    
    # Status e relacionamentos
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name='Status'
    )
    
    user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employee',
        verbose_name='Usuário do Sistema'
    )
    
    class Meta:
        verbose_name = 'Colaborador'
        verbose_name_plural = 'Colaboradores'
        ordering = ['full_name']
    
    def __str__(self):
        return f'{self.full_name} - {self.position}'
    
    @property
    def total_monthly_income(self):
        """
        Calcula a renda mensal total do colaborador.
        """
        total = self.net_salary
        
        if self.daily_allowance:
            # Assumindo 22 dias úteis por mês
            total += self.daily_allowance * 22
        
        if self.additional_remuneration:
            total += self.additional_remuneration
        
        return total
    
    @property
    def is_active(self):
        """
        Verifica se o colaborador está ativo.
        """
        return self.status == 'active'
    
    @property
    def years_of_service(self):
        """
        Calcula os anos de serviço do colaborador.
        """
        from datetime import date
        today = date.today()
        return today.year - self.start_date.year - (
            (today.month, today.day) < (self.start_date.month, self.start_date.day)
        )
    
    def get_documents(self):
        """
        Retorna todos os documentos solicitados pelo colaborador.
        """
        return self.document_requests.all().order_by('-created_at')
    
    def get_calendar_events(self):
        """
        Retorna todos os eventos de calendário do colaborador.
        """
        return self.calendar_events.all().order_by('-start_date')