"""
Forms para o cadastro de colaboradores.
"""
from django import forms
from django.contrib.auth.models import User
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field, Fieldset
from crispy_forms.bootstrap import FormActions
from .models import Employee


class EmployeeForm(forms.ModelForm):
    """
    Form para cadastro e edição de colaboradores.
    """
    
    class Meta:
        model = Employee
        fields = [
            'full_name', 'address', 'id_document', 'birth_date', 'email', 'phone',
            'position', 'contract_type', 'start_date', 'department',
            'net_salary', 'daily_allowance', 'additional_remuneration',
            'nuit', 'status', 'user'
        ]
        
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 3}),
            'net_salary': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'daily_allowance': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'additional_remuneration': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filtrar usuários disponíveis (sem colaborador associado)
        used_users = Employee.objects.exclude(
            pk=self.instance.pk if self.instance.pk else None
        ).values_list('user_id', flat=True)
        
        self.fields['user'].queryset = User.objects.exclude(
            id__in=used_users
        ).order_by('first_name', 'last_name', 'username')
        
        self.fields['user'].empty_label = "Selecione um usuário (opcional)"
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Fieldset(
                'Informações Pessoais',
                Row(
                    Column('full_name', css_class='form-group col-md-8 mb-3'),
                    Column('birth_date', css_class='form-group col-md-4 mb-3'),
                    css_class='form-row'
                ),
                Row(
                    Column('id_document', css_class='form-group col-md-6 mb-3'),
                    Column('nuit', css_class='form-group col-md-6 mb-3'),
                    css_class='form-row'
                ),
                'address',
                Row(
                    Column('email', css_class='form-group col-md-6 mb-3'),
                    Column('phone', css_class='form-group col-md-6 mb-3'),
                    css_class='form-row'
                ),
                css_class='mb-4'
            ),
            Fieldset(
                'Informações Profissionais',
                Row(
                    Column('position', css_class='form-group col-md-6 mb-3'),
                    Column('department', css_class='form-group col-md-6 mb-3'),
                    css_class='form-row'
                ),
                Row(
                    Column('contract_type', css_class='form-group col-md-6 mb-3'),
                    Column('start_date', css_class='form-group col-md-6 mb-3'),
                    css_class='form-row'
                ),
                Row(
                    Column('status', css_class='form-group col-md-6 mb-3'),
                    Column('user', css_class='form-group col-md-6 mb-3'),
                    css_class='form-row'
                ),
                css_class='mb-4'
            ),
            Fieldset(
                'Informações Salariais',
                Row(
                    Column('net_salary', css_class='form-group col-md-4 mb-3'),
                    Column('daily_allowance', css_class='form-group col-md-4 mb-3'),
                    Column('additional_remuneration', css_class='form-group col-md-4 mb-3'),
                    css_class='form-row'
                ),
                css_class='mb-4'
            ),
            FormActions(
                Submit('submit', 'Salvar Colaborador', css_class='btn btn-primary'),
                css_class='text-center'
            )
        )
    
    def clean_id_document(self):
        """
        Valida se o documento de identificação é único.
        """
        id_document = self.cleaned_data.get('id_document')
        
        if id_document:
            qs = Employee.objects.filter(id_document=id_document)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            
            if qs.exists():
                raise forms.ValidationError(
                    'Já existe um colaborador com este documento de identificação.'
                )
        
        return id_document
    
    def clean_email(self):
        """
        Valida se o email é único.
        """
        email = self.cleaned_data.get('email')
        
        if email:
            qs = Employee.objects.filter(email=email)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            
            if qs.exists():
                raise forms.ValidationError(
                    'Já existe um colaborador com este email.'
                )
        
        return email


class EmployeeSearchForm(forms.Form):
    """
    Form para busca de colaboradores.
    """
    search = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Buscar por nome, cargo ou departamento...',
            'class': 'form-control'
        }),
        label='Buscar'
    )
    
    status = forms.ChoiceField(
        choices=[('', 'Todos os status')] + Employee.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Status'
    )
    
    department = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Departamento...',
            'class': 'form-control'
        }),
        label='Departamento'
    )
    
    contract_type = forms.ChoiceField(
        choices=[('', 'Todos os tipos')] + Employee.CONTRACT_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Tipo de Contrato'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.form_method = 'get'
        self.helper.form_class = 'form-inline'
        self.helper.layout = Layout(
            Row(
                Column('search', css_class='form-group col-md-4 mb-3'),
                Column('status', css_class='form-group col-md-2 mb-3'),
                Column('department', css_class='form-group col-md-3 mb-3'),
                Column('contract_type', css_class='form-group col-md-2 mb-3'),
                Column(
                    Submit('submit', 'Buscar', css_class='btn btn-primary'),
                    css_class='form-group col-md-1 mb-3 d-flex align-items-end'
                ),
                css_class='form-row'
            )
        )