"""
Forms para a base de conhecimento.
"""
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field, Fieldset, HTML
from crispy_forms.bootstrap import FormActions
from .models import KnowledgeEntry, KnowledgeCategory, KnowledgeComment, KnowledgeAttachment, KnowledgeRating


class KnowledgeEntryForm(forms.ModelForm):
    """
    Form para criação e edição de entradas da base de conhecimento.
    """
    
    class Meta:
        model = KnowledgeEntry
        fields = [
            'title', 'problem_description', 'solution', 'category', 
            'tags', 'status', 'priority', 'is_featured'
        ]
        
        widgets = {
            'problem_description': forms.Textarea(attrs={'rows': 5}),
            'solution': forms.Textarea(attrs={'rows': 8}),
            'tags': forms.TextInput(attrs={'placeholder': 'Separe as tags com vírgulas'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filtrar categorias ativas
        self.fields['category'].queryset = KnowledgeCategory.objects.filter(is_active=True)
        
        # Verificar permissões para campos específicos
        if self.user and not self.user.is_superuser and not self.user.groups.filter(name='Admin').exists():
            # Colaboradores não podem marcar como destacado
            self.fields['is_featured'].widget = forms.HiddenInput()
            self.fields['is_featured'].initial = False
            
            # Limitar status disponíveis para colaboradores
            self.fields['status'].choices = [
                ('draft', 'Rascunho'),
                ('review', 'Em Revisão'),
            ]
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Fieldset(
                'Informações Principais',
                'title',
                Row(
                    Column('category', css_class='form-group col-md-6 mb-3'),
                    Column('priority', css_class='form-group col-md-6 mb-3'),
                    css_class='form-row'
                ),
                'tags',
                css_class='mb-4'
            ),
            Fieldset(
                'Conteúdo',
                'problem_description',
                'solution',
                css_class='mb-4'
            ),
            Fieldset(
                'Configurações',
                Row(
                    Column('status', css_class='form-group col-md-6 mb-3'),
                    Column('is_featured', css_class='form-group col-md-6 mb-3'),
                    css_class='form-row'
                ),
                css_class='mb-4'
            ),
            FormActions(
                Submit('submit', 'Salvar Entrada', css_class='btn btn-primary'),
                css_class='text-center'
            )
        )
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user and not instance.author_id:
            instance.author = self.user
        if commit:
            instance.save()
        return instance


class KnowledgeCategoryForm(forms.ModelForm):
    """
    Form para criação e edição de categorias.
    """
    
    class Meta:
        model = KnowledgeCategory
        fields = ['name', 'description', 'color', 'is_active']
        
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'color': forms.TextInput(attrs={'type': 'color'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Fieldset(
                'Informações da Categoria',
                Row(
                    Column('name', css_class='form-group col-md-8 mb-3'),
                    Column('color', css_class='form-group col-md-4 mb-3'),
                    css_class='form-row'
                ),
                'description',
                'is_active',
                css_class='mb-4'
            ),
            FormActions(
                Submit('submit', 'Salvar Categoria', css_class='btn btn-primary'),
                css_class='text-center'
            )
        )


class KnowledgeCommentForm(forms.ModelForm):
    """
    Form para comentários nas entradas.
    """
    
    class Meta:
        model = KnowledgeComment
        fields = ['content', 'is_solution']
        
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Escreva seu comentário...'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.entry = kwargs.pop('entry', None)
        self.parent = kwargs.pop('parent', None)
        super().__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            'content',
            'is_solution',
            FormActions(
                Submit('submit', 'Adicionar Comentário', css_class='btn btn-primary'),
                css_class='text-end'
            )
        )
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user:
            instance.author = self.user
        if self.entry:
            instance.entry = self.entry
        if self.parent:
            instance.parent = self.parent
        if commit:
            instance.save()
        return instance


class KnowledgeAttachmentForm(forms.ModelForm):
    """
    Form para upload de anexos.
    """
    
    class Meta:
        model = KnowledgeAttachment
        fields = ['file', 'name', 'description']
        
        widgets = {
            'description': forms.TextInput(attrs={'placeholder': 'Descrição opcional do arquivo'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.entry = kwargs.pop('entry', None)
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
        if self.entry:
            instance.entry = self.entry
        
        # Se nome não foi fornecido, usar nome do arquivo
        if not instance.name and instance.file:
            instance.name = instance.file.name
        
        if commit:
            instance.save()
        return instance


class KnowledgeRatingForm(forms.ModelForm):
    """
    Form para avaliação de entradas.
    """
    
    class Meta:
        model = KnowledgeRating
        fields = ['rating', 'comment']
        
        widgets = {
            'rating': forms.RadioSelect(),
            'comment': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Comentário opcional sobre sua avaliação'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.entry = kwargs.pop('entry', None)
        super().__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            HTML('<h5>Avalie esta entrada:</h5>'),
            'rating',
            'comment',
            FormActions(
                Submit('submit', 'Enviar Avaliação', css_class='btn btn-primary'),
                css_class='text-center'
            )
        )
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user:
            instance.user = self.user
        if self.entry:
            instance.entry = self.entry
        if commit:
            instance.save()
        return instance


class KnowledgeSearchForm(forms.Form):
    """
    Form para busca na base de conhecimento.
    """
    search = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Buscar por título, problema ou solução...',
            'class': 'form-control'
        }),
        label='Buscar'
    )
    
    category = forms.ModelChoiceField(
        queryset=KnowledgeCategory.objects.filter(is_active=True),
        required=False,
        empty_label='Todas as categorias',
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Categoria'
    )
    
    status = forms.ChoiceField(
        choices=[('', 'Todos os status')] + KnowledgeEntry.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Status'
    )
    
    priority = forms.ChoiceField(
        choices=[('', 'Todas as prioridades')] + KnowledgeEntry.PRIORITY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Prioridade'
    )
    
    tags = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Tags separadas por vírgula...',
            'class': 'form-control'
        }),
        label='Tags'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.form_method = 'get'
        self.helper.form_class = 'form-inline'
        self.helper.layout = Layout(
            Row(
                Column('search', css_class='form-group col-md-4 mb-3'),
                Column('category', css_class='form-group col-md-2 mb-3'),
                Column('status', css_class='form-group col-md-2 mb-3'),
                Column('priority', css_class='form-group col-md-2 mb-3'),
                Column('tags', css_class='form-group col-md-1 mb-3'),
                Column(
                    Submit('submit', 'Buscar', css_class='btn btn-primary'),
                    css_class='form-group col-md-1 mb-3 d-flex align-items-end'
                ),
                css_class='form-row'
            )
        )