#!/usr/bin/env python
"""
Script para criar templates faltantes do HR Internal System
"""

import os

def create_template(path, content):
    """Cria um template se não existir."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    
    if not os.path.exists(path):
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Criado: {path}")
    else:
        print(f"ℹ️ Já existe: {path}")

def main():
    print("🔧 Criando templates faltantes...")
    print("=" * 50)
    
    # Template base para páginas simples
    base_template = '''{% extends 'base/base.html' %}
{% load static %}
{% load crispy_forms_tags %}

{% block title %}{{ title }} - HR Internal System{% endblock %}

{% block content %}
<div class="container-fluid py-4">
    <!-- Header -->
    <div class="row mb-4">
        <div class="col-12">
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <h1 class="h3 mb-1">{{ title }}</h1>
                    <p class="text-muted mb-0">
                        Página em desenvolvimento
                    </p>
                </div>
                <a href="javascript:history.back()" class="btn btn-outline-secondary">
                    <i class="bi bi-arrow-left"></i>
                    Voltar
                </a>
            </div>
        </div>
    </div>
    
    <!-- Content -->
    <div class="row">
        <div class="col-12">
            <div class="card border-0 shadow-sm">
                <div class="card-body text-center py-5">
                    <i class="bi bi-tools text-muted" style="font-size: 4rem;"></i>
                    <h4 class="text-muted mt-3">Página em Desenvolvimento</h4>
                    <p class="text-muted">Esta funcionalidade será implementada em breve.</p>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}'''
    
    # Lista de templates para criar
    templates = [
        # Documents
        'templates/documents/document_request_list.html',
        'templates/documents/document_request_detail.html',
        'templates/documents/document_request_form.html',
        'templates/documents/document_request_approve.html',
        'templates/documents/document_stats.html',
        'templates/documents/template_list.html',
        'templates/documents/template_form.html',
        
        # Knowledge Base
        'templates/knowledge_base/home.html',
        'templates/knowledge_base/entry_form.html',
        'templates/knowledge_base/entry_detail.html',
        'templates/knowledge_base/category_list.html',
        'templates/knowledge_base/category_form.html',
        'templates/knowledge_base/category_detail.html',
        'templates/knowledge_base/stats.html',
        
        # Calendar
        'templates/calendar/event_detail.html',
        'templates/calendar/event_approve.html',
        'templates/calendar/notifications.html',
        'templates/calendar/stats.html',
        
        # Employees
        'templates/employees/employee_stats.html',
        'templates/employees/employee_confirm_delete.html',
    ]
    
    # Criar todos os templates
    for template_path in templates:
        create_template(template_path, base_template)
    
    # Template específico para lista de documentos
    documents_list_template = '''{% extends 'base/base.html' %}
{% load static %}
{% load crispy_forms_tags %}

{% block title %}{{ title }} - HR Internal System{% endblock %}

{% block content %}
<div class="container-fluid py-4">
    <!-- Header -->
    <div class="row mb-4">
        <div class="col-12">
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <h1 class="h3 mb-1">{{ title }}</h1>
                    <p class="text-muted mb-0">
                        Suas requisições de documentos
                    </p>
                </div>
                <a href="{% url 'documents:create' %}" class="btn btn-primary">
                    <i class="bi bi-file-plus"></i>
                    Nova Requisição
                </a>
            </div>
        </div>
    </div>
    
    <!-- Search Form -->
    <div class="row mb-4">
        <div class="col-12">
            <div class="card border-0 shadow-sm">
                <div class="card-body">
                    {% crispy form %}
                </div>
            </div>
        </div>
    </div>
    
    <!-- Documents List -->
    <div class="row">
        <div class="col-12">
            <div class="card border-0 shadow-sm">
                <div class="card-header bg-transparent">
                    <h5 class="card-title mb-0">
                        <i class="bi bi-file-earmark-text"></i>
                        Requisições de Documentos
                    </h5>
                </div>
                <div class="card-body p-0">
                    {% if page_obj %}
                        <div class="table-responsive">
                            <table class="table table-hover mb-0">
                                <thead>
                                    <tr>
                                        <th>Tipo de Documento</th>
                                        <th>Status</th>
                                        <th>Solicitado em</th>
                                        <th>Ações</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td colspan="4" class="text-center text-muted py-4">
                                            Nenhuma requisição encontrada
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    {% else %}
                        <div class="text-center py-5">
                            <i class="bi bi-file-earmark-text text-muted" style="font-size: 4rem;"></i>
                            <h4 class="text-muted mt-3">Nenhuma requisição</h4>
                            <p class="text-muted">Você ainda não fez nenhuma requisição de documento.</p>
                            <a href="{% url 'documents:create' %}" class="btn btn-primary">
                                <i class="bi bi-file-plus"></i>
                                Primeira Requisição
                            </a>
                        </div>
                    {% endif %}
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}'''
    
    create_template('templates/documents/document_request_list.html', documents_list_template)
    
    # Template para knowledge base home
    knowledge_home_template = '''{% extends 'base/base.html' %}
{% load static %}
{% load crispy_forms_tags %}

{% block title %}{{ title }} - HR Internal System{% endblock %}

{% block content %}
<div class="container-fluid py-4">
    <!-- Header -->
    <div class="row mb-4">
        <div class="col-12">
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <h1 class="h3 mb-1">{{ title }}</h1>
                    <p class="text-muted mb-0">
                        Compartilhe conhecimento e encontre soluções
                    </p>
                </div>
                <a href="{% url 'knowledge_base:create' %}" class="btn btn-primary">
                    <i class="bi bi-plus-circle"></i>
                    Nova Entrada
                </a>
            </div>
        </div>
    </div>
    
    <!-- Search -->
    <div class="row mb-4">
        <div class="col-12">
            <div class="card border-0 shadow-sm">
                <div class="card-body">
                    {% crispy form %}
                </div>
            </div>
        </div>
    </div>
    
    <!-- Knowledge Entries -->
    <div class="row">
        <div class="col-lg-9">
            <div class="card border-0 shadow-sm">
                <div class="card-header bg-transparent">
                    <h5 class="card-title mb-0">
                        <i class="bi bi-book"></i>
                        Entradas de Conhecimento
                    </h5>
                </div>
                <div class="card-body">
                    <div class="text-center py-5">
                        <i class="bi bi-book text-muted" style="font-size: 4rem;"></i>
                        <h4 class="text-muted mt-3">Base de Conhecimento Vazia</h4>
                        <p class="text-muted">Seja o primeiro a compartilhar conhecimento!</p>
                        <a href="{% url 'knowledge_base:create' %}" class="btn btn-primary">
                            <i class="bi bi-plus-circle"></i>
                            Criar Primeira Entrada
                        </a>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="col-lg-3">
            <!-- Categories -->
            <div class="card border-0 shadow-sm mb-4">
                <div class="card-header bg-transparent">
                    <h6 class="card-title mb-0">
                        <i class="bi bi-tags"></i>
                        Categorias
                    </h6>
                </div>
                <div class="card-body">
                    <p class="text-muted small">Nenhuma categoria criada ainda.</p>
                </div>
            </div>
            
            <!-- Stats -->
            <div class="card border-0 shadow-sm">
                <div class="card-header bg-transparent">
                    <h6 class="card-title mb-0">
                        <i class="bi bi-graph-up"></i>
                        Estatísticas
                    </h6>
                </div>
                <div class="card-body">
                    <div class="d-flex justify-content-between mb-2">
                        <span>Total de Entradas:</span>
                        <strong>{{ stats.total_entries|default:0 }}</strong>
                    </div>
                    <div class="d-flex justify-content-between mb-2">
                        <span>Categorias:</span>
                        <strong>{{ stats.categories_count|default:0 }}</strong>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}'''
    
    create_template('templates/knowledge_base/home.html', knowledge_home_template)
    
    print("\n" + "=" * 50)
    print("🎉 Templates criados com sucesso!")
    print("Agora o sistema deve funcionar sem erros de template.")
    print("=" * 50)

if __name__ == "__main__":
    main()