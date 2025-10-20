"""
Forms para requisição e geração de documentos.
"""
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field, Fieldset
from crispy_forms.bootstrap import FormActions
from .models import DocumentRequest, DocumentTemplate


class DocumentRequestForm(forms.ModelForm):
    """
    Form para requisição de documentos pelos colaboradores.
    """
    
    class Meta:
        model = DocumentRequest
        fields = ['document_type', 'reason']
        
        widgets = {
            'reason': forms.Textarea(attrs={'rows': 4}),
        }
    
    def __init__(self, *args, **kwargs):
        self.employee = kwargs.pop('employee', None)
        super().__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Fieldset(
                'Solicitação de Documento',
                'document_type',
                'reason',
                css_class='mb-4'
            ),
            FormActions(
                Submit('submit', 'Solicitar Documento', css_class='btn btn-primary'),
                css_class='text-center'
            )
        )
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.employee:
            instance.employee = self.employee
        if commit:
            instance.save()
        return instance


class DocumentApprovalForm(forms.ModelForm):
    """
    Form para aprovação/rejeição de documentos pelos administradores.
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
        model = DocumentRequest
        fields = ['admin_notes', 'rejection_reason']
        
        widgets = {
            'admin_notes': forms.Textarea(attrs={'rows': 3}),
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
                'Decisão sobre a Solicitação',
                'action',
                'admin_notes',
                Field('rejection_reason', css_class='rejection-reason-field'),
                css_class='mb-4'
            ),
            FormActions(
                Submit('submit', 'Processar Solicitação', css_class='btn btn-primary'),
                css_class='text-center'
            )
        )
    
    def clean(self):
        cleaned_data = super().clean()
        action = cleaned_data.get('action')
        rejection_reason = cleaned_data.get('rejection_reason')
        
        if action == 'reject' and not rejection_reason:
            raise forms.ValidationError(
                'Motivo da rejeição é obrigatório quando rejeitando uma solicitação.'
            )
        
        return cleaned_data


class DocumentSearchForm(forms.Form):
    """
    Form para busca de requisições de documentos.
    """
    search = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Buscar por colaborador ou tipo de documento...',
            'class': 'form-control'
        }),
        label='Buscar'
    )
    
    status = forms.ChoiceField(
        choices=[('', 'Todos os status')] + DocumentRequest.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Status'
    )
    
    document_type = forms.ChoiceField(
        choices=[('', 'Todos os tipos')] + DocumentRequest.DOCUMENT_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Tipo de Documento'
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label='Data Inicial'
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label='Data Final'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.form_method = 'get'
        self.helper.form_class = 'form-inline'
        self.helper.layout = Layout(
            Row(
                Column('search', css_class='form-group col-md-3 mb-3'),
                Column('status', css_class='form-group col-md-2 mb-3'),
                Column('document_type', css_class='form-group col-md-2 mb-3'),
                Column('date_from', css_class='form-group col-md-2 mb-3'),
                Column('date_to', css_class='form-group col-md-2 mb-3'),
                Column(
                    Submit('submit', 'Buscar', css_class='btn btn-primary'),
                    css_class='form-group col-md-1 mb-3 d-flex align-items-end'
                ),
                css_class='form-row'
            )
        )


class DocumentTemplateForm(forms.ModelForm):
    """
    Form para criação e edição de templates de documentos.
    """
    
    class Meta:
        model = DocumentTemplate
        fields = [
            'name', 'document_type', 'template_type', 'template_file',
            'description', 'is_active', 'variables'
        ]
        
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'variables': forms.Textarea(attrs={
                'rows': 5,
                'placeholder': '{"employee_name": "Nome do colaborador", "salary": "Salário"}'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_enctype = 'multipart/form-data'
        self.helper.layout = Layout(
            Fieldset(
                'Informações do Template',
                Row(
                    Column('name', css_class='form-group col-md-6 mb-3'),
                    Column('document_type', css_class='form-group col-md-6 mb-3'),
                    css_class='form-row'
                ),
                Row(
                    Column('template_type', css_class='form-group col-md-6 mb-3'),
                    Column('is_active', css_class='form-group col-md-6 mb-3'),
                    css_class='form-row'
                ),
                'template_file',
                'description',
                css_class='mb-4'
            ),
            Fieldset(
                'Variáveis do Template',
                Field('variables', css_class='font-monospace'),
                css_class='mb-4'
            ),
            FormActions(
                Submit('submit', 'Salvar Template', css_class='btn btn-primary'),
                css_class='text-center'
            )
        )
    
    def clean_variables(self):
        """
        Valida se as variáveis estão em formato JSON válido.
        """
        variables = self.cleaned_data.get('variables')
        
        if variables:
            import json
            try:
                json.loads(variables)
            except json.JSONDecodeError:
                raise forms.ValidationError(
                    'As variáveis devem estar em formato JSON válido.'
                )
        
        return variables