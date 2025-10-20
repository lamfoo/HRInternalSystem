"""
Forms para o calendário interno.
"""
from django import forms
from django.contrib.auth.models import User
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field, Fieldset, HTML
from crispy_forms.bootstrap import FormActions
from apps.employees.models import Employee
from .models import CalendarEvent, CalendarAttachment, CalendarSettings


class CalendarEventForm(forms.ModelForm):
    """
    Form para criação e edição de eventos do calendário.
    """
    
    class Meta:
        model = CalendarEvent
        fields = [
            'title', 'description', 'event_type', 'start_date', 'end_date', 
            'all_day', 'employee', 'responsible', 'status', 'priority', 
            'location', 'participants', 'color', 'is_private'
        ]
        
        widgets = {
            'start_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 4}),
            'color': forms.TextInput(attrs={'type': 'color'}),
            'participants': forms.CheckboxSelectMultiple(),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filtrar colaboradores ativos
        self.fields['employee'].queryset = Employee.objects.filter(status='active')
        self.fields['participants'].queryset = Employee.objects.filter(status='active')
        
        # Verificar permissões
        user_is_admin = (
            self.user and 
            (self.user.is_superuser or self.user.groups.filter(name='Admin').exists())
        )
        
        if not user_is_admin:
            # Colaboradores só podem criar eventos para si mesmos
            if hasattr(self.user, 'employee'):
                self.fields['employee'].initial = self.user.employee
                self.fields['employee'].widget = forms.HiddenInput()
            
            # Limitar status disponíveis
            self.fields['status'].choices = [
                ('pending', 'Pendente'),
            ]
            self.fields['status'].initial = 'pending'
            self.fields['status'].widget = forms.HiddenInput()
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Fieldset(
                'Informações Básicas',
                'title',
                Row(
                    Column('event_type', css_class='form-group col-md-6 mb-3'),
                    Column('priority', css_class='form-group col-md-6 mb-3'),
                    css_class='form-row'
                ),
                'description',
                css_class='mb-4'
            ),
            Fieldset(
                'Data e Hora',
                Row(
                    Column('start_date', css_class='form-group col-md-6 mb-3'),
                    Column('end_date', css_class='form-group col-md-6 mb-3'),
                    css_class='form-row'
                ),
                'all_day',
                'location',
                css_class='mb-4'
            ),
            Fieldset(
                'Participantes',
                Row(
                    Column('employee', css_class='form-group col-md-6 mb-3'),
                    Column('responsible', css_class='form-group col-md-6 mb-3'),
                    css_class='form-row'
                ),
                'participants',
                css_class='mb-4'
            ),
            Fieldset(
                'Configurações',
                Row(
                    Column('status', css_class='form-group col-md-4 mb-3'),
                    Column('color', css_class='form-group col-md-4 mb-3'),
                    Column('is_private', css_class='form-group col-md-4 mb-3'),
                    css_class='form-row'
                ),
                css_class='mb-4'
            ),
            FormActions(
                Submit('submit', 'Salvar Evento', css_class='btn btn-primary'),
                css_class='text-center'
            )
        )
    
    def clean(self):
        """
        Validações customizadas do form.
        """
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date:
            if start_date >= end_date:
                raise forms.ValidationError(
                    'A data de início deve ser anterior à data de término.'
                )
        
        return cleaned_data


class CalendarEventApprovalForm(forms.ModelForm):
    """
    Form para aprovação/rejeição de eventos pelos administradores.
    """
    
    ACTION_CHOICES = [
        ('approve', 'Aprovar'),
        ('reject', 'Rejeitar'),
    ]
    
    action = forms.ChoiceField(
        choices=ACTION_CHOICES,
        widget=forms.RadioSelect,
        label='Ação'
    )
    
    class Meta:
        model = CalendarEvent
        fields = ['rejection_reason']
        
        widgets = {
            'rejection_reason': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Tornar rejection_reason obrigatório apenas se rejeitando
        self.fields['rejection_reason'].required = False
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Fieldset(
                'Decisão sobre o Evento',
                'action',
                Field('rejection_reason', css_class='rejection-reason-field'),
                css_class='mb-4'
            ),
            FormActions(
                Submit('submit', 'Processar Evento', css_class='btn btn-primary'),
                css_class='text-center'
            )
        )
    
    def clean(self):
        cleaned_data = super().clean()
        action = cleaned_data.get('action')
        rejection_reason = cleaned_data.get('rejection_reason')
        
        if action == 'reject' and not rejection_reason:
            raise forms.ValidationError(
                'Motivo da rejeição é obrigatório quando rejeitando um evento.'
            )
        
        return cleaned_data


class CalendarAttachmentForm(forms.ModelForm):
    """
    Form para upload de anexos em eventos.
    """
    
    class Meta:
        model = CalendarAttachment
        fields = ['file', 'name', 'description']
        
        widgets = {
            'description': forms.TextInput(attrs={'placeholder': 'Descrição opcional do arquivo'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.event = kwargs.pop('event', None)
        super().__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_enctype = 'multipart/form-data'
        self.helper.layout = Layout(
            'file',
            'name',
            'description',
            FormActions(
                Submit('submit', 'Enviar Anexo', css_class='btn btn-primary'),
                css_class='text-center'
            )
        )
    
    def clean_file(self):
        """
        Valida o arquivo enviado.
        """
        file = self.cleaned_data.get('file')
        
        if file:
            # Verificar tamanho (máximo 10MB)
            if file.size > 10 * 1024 * 1024:
                raise forms.ValidationError('O arquivo deve ter no máximo 10MB.')
            
            # Verificar extensões permitidas
            allowed_extensions = [
                '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
                '.txt', '.jpg', '.jpeg', '.png', '.gif', '.zip', '.rar'
            ]
            
            import os
            ext = os.path.splitext(file.name)[1].lower()
            if ext not in allowed_extensions:
                raise forms.ValidationError(
                    f'Tipo de arquivo não permitido. Extensões permitidas: {", ".join(allowed_extensions)}'
                )
        
        return file
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user:
            instance.uploaded_by = self.user
        if self.event:
            instance.event = self.event
        
        # Se nome não foi fornecido, usar nome do arquivo
        if not instance.name and instance.file:
            instance.name = instance.file.name
        
        if commit:
            instance.save()
        return instance


class CalendarSettingsForm(forms.ModelForm):
    """
    Form para configurações do calendário.
    """
    
    class Meta:
        model = CalendarSettings
        fields = [
            'default_view', 'show_weekends', 'start_time', 'end_time',
            'time_zone', 'email_notifications', 'reminder_minutes'
        ]
        
        widgets = {
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Fieldset(
                'Visualização',
                Row(
                    Column('default_view', css_class='form-group col-md-6 mb-3'),
                    Column('show_weekends', css_class='form-group col-md-6 mb-3'),
                    css_class='form-row'
                ),
                Row(
                    Column('start_time', css_class='form-group col-md-6 mb-3'),
                    Column('end_time', css_class='form-group col-md-6 mb-3'),
                    css_class='form-row'
                ),
                'time_zone',
                css_class='mb-4'
            ),
            Fieldset(
                'Notificações',
                Row(
                    Column('email_notifications', css_class='form-group col-md-6 mb-3'),
                    Column('reminder_minutes', css_class='form-group col-md-6 mb-3'),
                    css_class='form-row'
                ),
                css_class='mb-4'
            ),
            FormActions(
                Submit('submit', 'Salvar Configurações', css_class='btn btn-primary'),
                css_class='text-center'
            )
        )


class CalendarFilterForm(forms.Form):
    """
    Form para filtros do calendário.
    """
    event_type = forms.MultipleChoiceField(
        choices=CalendarEvent.EVENT_TYPE_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label='Tipos de Evento'
    )
    
    status = forms.MultipleChoiceField(
        choices=CalendarEvent.STATUS_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label='Status'
    )
    
    employee = forms.ModelMultipleChoiceField(
        queryset=Employee.objects.filter(status='active'),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label='Colaboradores'
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        label='Data Inicial'
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        label='Data Final'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.form_method = 'get'
        self.helper.layout = Layout(
            HTML('<h5>Filtros do Calendário</h5>'),
            'event_type',
            'status',
            'employee',
            Row(
                Column('date_from', css_class='form-group col-md-6 mb-3'),
                Column('date_to', css_class='form-group col-md-6 mb-3'),
                css_class='form-row'
            ),
            FormActions(
                Submit('submit', 'Aplicar Filtros', css_class='btn btn-primary btn-sm'),
                css_class='text-center'
            )
        )


class QuickEventForm(forms.Form):
    """
    Form simplificado para criação rápida de eventos.
    """
    title = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'placeholder': 'Título do evento'}),
        label='Título'
    )
    
    start_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        label='Data/Hora de Início'
    )
    
    end_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        label='Data/Hora de Término'
    )
    
    event_type = forms.ChoiceField(
        choices=CalendarEvent.EVENT_TYPE_CHOICES,
        initial='outro',
        label='Tipo'
    )
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            'title',
            Row(
                Column('start_date', css_class='form-group col-md-6 mb-3'),
                Column('end_date', css_class='form-group col-md-6 mb-3'),
                css_class='form-row'
            ),
            'event_type',
            FormActions(
                Submit('submit', 'Criar Evento', css_class='btn btn-primary'),
                css_class='text-center'
            )
        )
    
    def clean(self):
        """
        Validações customizadas do form.
        """
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date:
            if start_date >= end_date:
                raise forms.ValidationError(
                    'A data de início deve ser anterior à data de término.'
                )
        
        return cleaned_data