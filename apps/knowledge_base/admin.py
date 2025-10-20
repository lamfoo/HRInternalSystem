"""
Admin do app knowledge_base.
"""
from django.contrib import admin
from .models import KnowledgeEntry, KnowledgeCategory, KnowledgeComment, KnowledgeAttachment, KnowledgeRating


@admin.register(KnowledgeCategory)
class KnowledgeCategoryAdmin(admin.ModelAdmin):
    """
    Admin para KnowledgeCategory.
    """
    list_display = ('name', 'is_active', 'get_entries_count', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at', 'created_by', 'updated_by')
    
    def save_model(self, request, obj, form, change):
        """
        Salva o modelo definindo o usuário que criou/modificou.
        """
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


class KnowledgeAttachmentInline(admin.TabularInline):
    """
    Inline para anexos da entrada.
    """
    model = KnowledgeAttachment
    extra = 0
    readonly_fields = ('uploaded_at', 'uploaded_by')


class KnowledgeCommentInline(admin.TabularInline):
    """
    Inline para comentários da entrada.
    """
    model = KnowledgeComment
    extra = 0
    readonly_fields = ('created_at', 'updated_at', 'created_by', 'updated_by')


@admin.register(KnowledgeEntry)
class KnowledgeEntryAdmin(admin.ModelAdmin):
    """
    Admin para KnowledgeEntry.
    """
    list_display = (
        'title', 'author', 'category', 'status', 'priority', 
        'views_count', 'is_featured', 'created_at'
    )
    
    list_filter = (
        'status', 'priority', 'category', 'is_featured', 
        'created_at', 'published_at'
    )
    
    search_fields = (
        'title', 'problem_description', 'solution', 'tags', 
        'author__username', 'author__first_name', 'author__last_name'
    )
    
    readonly_fields = (
        'views_count', 'created_at', 'updated_at', 
        'created_by', 'updated_by', 'published_at'
    )
    
    inlines = [KnowledgeAttachmentInline, KnowledgeCommentInline]
    
    fieldsets = (
        ('Informações Principais', {
            'fields': (
                'title', 'author', 'category', 'tags'
            )
        }),
        ('Conteúdo', {
            'fields': (
                'problem_description', 'solution'
            )
        }),
        ('Configurações', {
            'fields': (
                'status', 'priority', 'is_featured'
            )
        }),
        ('Estatísticas', {
            'fields': (
                'views_count', 'published_at'
            ),
            'classes': ('collapse',)
        }),
        ('Metadados', {
            'fields': (
                'created_at', 'updated_at', 'created_by', 'updated_by'
            ),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """
        Salva o modelo definindo o usuário que criou/modificou.
        """
        if not change:
            obj.created_by = request.user
            if not obj.author:
                obj.author = request.user
        obj.updated_by = request.user
        
        # Definir published_at quando status muda para published
        if obj.status == 'published' and not obj.published_at:
            from django.utils import timezone
            obj.published_at = timezone.now()
        
        super().save_model(request, obj, form, change)


@admin.register(KnowledgeComment)
class KnowledgeCommentAdmin(admin.ModelAdmin):
    """
    Admin para KnowledgeComment.
    """
    list_display = (
        'entry', 'author', 'is_solution', 'is_approved', 
        'parent', 'created_at'
    )
    
    list_filter = (
        'is_solution', 'is_approved', 'created_at'
    )
    
    search_fields = (
        'entry__title', 'author__username', 'content'
    )
    
    readonly_fields = (
        'created_at', 'updated_at', 'created_by', 'updated_by'
    )
    
    def save_model(self, request, obj, form, change):
        """
        Salva o modelo definindo o usuário que criou/modificou.
        """
        if not change:
            obj.created_by = request.user
            if not obj.author:
                obj.author = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(KnowledgeAttachment)
class KnowledgeAttachmentAdmin(admin.ModelAdmin):
    """
    Admin para KnowledgeAttachment.
    """
    list_display = (
        'name', 'entry', 'uploaded_by', 'uploaded_at'
    )
    
    list_filter = ('uploaded_at',)
    
    search_fields = (
        'name', 'description', 'entry__title', 'uploaded_by__username'
    )
    
    readonly_fields = ('uploaded_at',)


@admin.register(KnowledgeRating)
class KnowledgeRatingAdmin(admin.ModelAdmin):
    """
    Admin para KnowledgeRating.
    """
    list_display = (
        'entry', 'user', 'rating', 'created_at'
    )
    
    list_filter = ('rating', 'created_at')
    
    search_fields = (
        'entry__title', 'user__username', 'comment'
    )
    
    readonly_fields = ('created_at',)