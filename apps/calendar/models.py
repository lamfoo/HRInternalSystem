"""
Models para o calendário interno.
"""
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.exceptions import ValidationError
from apps.core.models import UserTrackingModel
from apps.employees.models import Employee


def calendar_attachment_path(instance, filename):
    """
    Define o caminho para upload de anexos do calendário.
    """
    return f'calendar/{instance.event.id}/{filename}'


class CalendarEvent(UserTrackingModel):
    """
    Eventos do calendário interno.
    """
    
    EVENT_TYPE_CHOICES = [
        ('ferias', 'Férias'),
        ('visita_interna', 'Visita Interna'),
        ('reuniao', 'Reunião'),
        ('treinamento', 'Treinamento'),
        ('evento_empresa', 'Evento da Empresa'),
        ('feriado', 'Feriado'),
        ('licenca', 'Licença'),
        ('viagem_trabalho', 'Viagem de Trabalho'),
        ('avaliacao', 'Avaliação'),
        ('outro', 'Outro'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('approved', 'Aprovado'),
        ('rejected', 'Rejeitado'),
        ('cancelled', 'Cancelado'),
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
    
    description = models.TextField(
        blank=True,
        verbose_name='Descrição'
    )
    
    event_type = models.CharField(
        max_length=20,
        choices=EVENT_TYPE_CHOICES,
        default='outro',
        verbose_name='Tipo de Evento'
    )
    
    start_date = models.DateTimeField(
        verbose_name='Data/Hora de Início'
    )
    
    end_date = models.DateTimeField(
        verbose_name='Data/Hora de Término'
    )
    
    all_day = models.BooleanField(
        default=False,
        verbose_name='Dia Inteiro'
    )
    
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='calendar_events',
        verbose_name='Colaborador'
    )
    
    responsible = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='responsible_events',
        verbose_name='Responsável'
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Status'
    )
    
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='medium',
        verbose_name='Prioridade'
    )
    
    location = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Local'
    )
    
    participants = models.ManyToManyField(
        Employee,
        blank=True,
        related_name='participating_events',
        verbose_name='Participantes'
    )
    
    is_recurring = models.BooleanField(
        default=False,
        verbose_name='Evento Recorrente'
    )
    
    recurrence_rule = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Regra de Recorrência',
        help_text='Ex: FREQ=WEEKLY;BYDAY=MO,WE,FR'
    )
    
    color = models.CharField(
        max_length=7,
        default='#007bff',
        verbose_name='Cor',
        help_text='Cor em formato hexadecimal (ex: #007bff)'
    )
    
    is_private = models.BooleanField(
        default=False,
        verbose_name='Evento Privado'
    )
    
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_events',
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
    
    class Meta:
        verbose_name = 'Evento do Calendário'
        verbose_name_plural = 'Eventos do Calendário'
        ordering = ['start_date']
    
    def __str__(self):
        return f'{self.title} - {self.employee.full_name} ({self.start_date.strftime("%d/%m/%Y")})'
    
    def clean(self):
        """
        Validações customizadas do modelo.
        """
        if self.start_date and self.end_date:
            if self.start_date >= self.end_date:
                raise ValidationError('A data de início deve ser anterior à data de término.')
    
    def get_absolute_url(self):
        """
        Retorna a URL absoluta do evento.
        """
        return reverse('calendar:event_detail', kwargs={'pk': self.pk})
    
    @property
    def duration_hours(self):
        """
        Calcula a duração do evento em horas.
        """
        if self.start_date and self.end_date:
            duration = self.end_date - self.start_date
            return duration.total_seconds() / 3600
        return 0
    
    @property
    def is_approved(self):
        """
        Verifica se o evento está aprovado.
        """
        return self.status == 'approved'
    
    @property
    def is_pending(self):
        """
        Verifica se o evento está pendente.
        """
        return self.status == 'pending'
    
    @property
    def can_be_approved(self):
        """
        Verifica se o evento pode ser aprovado.
        """
        return self.status in ['pending', 'rejected']
    
    @property
    def can_be_cancelled(self):
        """
        Verifica se o evento pode ser cancelado.
        """
        return self.status in ['pending', 'approved']
    
    def get_color_by_type(self):
        """
        Retorna cor baseada no tipo de evento.
        """
        color_map = {
            'ferias': '#28a745',
            'visita_interna': '#17a2b8',
            'reuniao': '#6f42c1',
            'treinamento': '#fd7e14',
            'evento_empresa': '#20c997',
            'feriado': '#dc3545',
            'licenca': '#ffc107',
            'viagem_trabalho': '#6c757d',
            'avaliacao': '#e83e8c',
            'outro': '#007bff',
        }
        return color_map.get(self.event_type, self.color)
    
    def get_participants_list(self):
        """
        Retorna lista de participantes.
        """
        return self.participants.all()
    
    def get_attachments_count(self):
        """
        Retorna o número de anexos.
        """
        return self.attachments.count()
    
    def to_fullcalendar_dict(self):
        """
        Converte o evento para formato FullCalendar.
        """
        return {
            'id': self.id,
            'title': self.title,
            'start': self.start_date.isoformat(),
            'end': self.end_date.isoformat(),
            'allDay': self.all_day,
            'color': self.get_color_by_type(),
            'description': self.description,
            'location': self.location,
            'status': self.status,
            'eventType': self.event_type,
            'priority': self.priority,
            'employee': self.employee.full_name,
            'url': self.get_absolute_url(),
        }


class CalendarAttachment(models.Model):
    """
    Anexos para eventos do calendário.
    """
    event = models.ForeignKey(
        CalendarEvent,
        on_delete=models.CASCADE,
        related_name='attachments',
        verbose_name='Evento'
    )
    
    file = models.FileField(
        upload_to=calendar_attachment_path,
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
        verbose_name = 'Anexo do Evento'
        verbose_name_plural = 'Anexos dos Eventos'
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


class CalendarNotification(models.Model):
    """
    Notificações relacionadas a eventos do calendário.
    """
    
    NOTIFICATION_TYPE_CHOICES = [
        ('event_created', 'Evento Criado'),
        ('event_approved', 'Evento Aprovado'),
        ('event_rejected', 'Evento Rejeitado'),
        ('event_cancelled', 'Evento Cancelado'),
        ('event_reminder', 'Lembrete de Evento'),
        ('event_updated', 'Evento Atualizado'),
    ]
    
    event = models.ForeignKey(
        CalendarEvent,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='Evento'
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Usuário'
    )
    
    notification_type = models.CharField(
        max_length=20,
        choices=NOTIFICATION_TYPE_CHOICES,
        verbose_name='Tipo de Notificação'
    )
    
    title = models.CharField(
        max_length=200,
        verbose_name='Título'
    )
    
    message = models.TextField(
        verbose_name='Mensagem'
    )
    
    is_read = models.BooleanField(
        default=False,
        verbose_name='Lida'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Criada em'
    )
    
    read_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Lida em'
    )
    
    class Meta:
        verbose_name = 'Notificação do Calendário'
        verbose_name_plural = 'Notificações do Calendário'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.title} - {self.user.username}'
    
    def mark_as_read(self):
        """
        Marca a notificação como lida.
        """
        if not self.is_read:
            from django.utils import timezone
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])


class CalendarSettings(models.Model):
    """
    Configurações do calendário por usuário.
    """
    
    VIEW_CHOICES = [
        ('month', 'Mês'),
        ('week', 'Semana'),
        ('day', 'Dia'),
        ('list', 'Lista'),
    ]
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='calendar_settings',
        verbose_name='Usuário'
    )
    
    default_view = models.CharField(
        max_length=10,
        choices=VIEW_CHOICES,
        default='month',
        verbose_name='Visualização Padrão'
    )
    
    show_weekends = models.BooleanField(
        default=True,
        verbose_name='Mostrar Fins de Semana'
    )
    
    start_time = models.TimeField(
        default='08:00',
        verbose_name='Hora de Início'
    )
    
    end_time = models.TimeField(
        default='18:00',
        verbose_name='Hora de Término'
    )
    
    time_zone = models.CharField(
        max_length=50,
        default='Africa/Maputo',
        verbose_name='Fuso Horário'
    )
    
    event_types_filter = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Filtro de Tipos de Evento'
    )
    
    email_notifications = models.BooleanField(
        default=True,
        verbose_name='Notificações por Email'
    )
    
    reminder_minutes = models.PositiveIntegerField(
        default=15,
        verbose_name='Lembrete (minutos antes)'
    )
    
    class Meta:
        verbose_name = 'Configurações do Calendário'
        verbose_name_plural = 'Configurações do Calendário'
    
    def __str__(self):
        return f'Configurações de {self.user.username}'