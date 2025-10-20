#!/usr/bin/env python
"""
Script para corrigir problemas de migração do HR Internal System
"""

import os
import sys
import django
from django.core.management import execute_from_command_line
from django.db import connection

def setup_django():
    """Configura o Django."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hr_system.settings.dev')
    django.setup()

def check_table_exists(table_name):
    """Verifica se uma tabela existe no banco de dados."""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name=%s;
        """, [table_name])
        return cursor.fetchone() is not None

def main():
    print("🔧 Corrigindo problemas de migração...")
    print("=" * 50)
    
    # Configurar Django
    setup_django()
    
    # Remover migrações existentes (se houver problemas)
    migration_dirs = [
        'apps/core/migrations',
        'apps/accounts/migrations',
        'apps/employees/migrations',
        'apps/documents/migrations',
        'apps/knowledge_base/migrations',
        'apps/calendar/migrations'
    ]
    
    print("🗑️ Limpando migrações antigas...")
    for migration_dir in migration_dirs:
        if os.path.exists(migration_dir):
            for file in os.listdir(migration_dir):
                if file.endswith('.py') and file != '__init__.py':
                    file_path = os.path.join(migration_dir, file)
                    os.remove(file_path)
                    print(f"   Removido: {file_path}")
    
    # Remover banco de dados SQLite se existir
    if os.path.exists('db.sqlite3'):
        print("🗑️ Removendo banco de dados antigo...")
        os.remove('db.sqlite3')
        print("   ✅ db.sqlite3 removido")
    
    # Criar novas migrações
    print("\n📝 Criando novas migrações...")
    
    apps_order = ['core', 'accounts', 'employees', 'documents', 'knowledge_base', 'calendar']
    
    for app in apps_order:
        print(f"   Criando migração para {app}...")
        try:
            execute_from_command_line(['manage.py', 'makemigrations', app])
            print(f"   ✅ Migração criada para {app}")
        except Exception as e:
            print(f"   ❌ Erro ao criar migração para {app}: {e}")
    
    # Aplicar migrações
    print("\n🔄 Aplicando migrações...")
    try:
        execute_from_command_line(['manage.py', 'migrate'])
        print("✅ Migrações aplicadas com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao aplicar migrações: {e}")
        return False
    
    # Criar grupos
    print("\n👥 Criando grupos de usuários...")
    try:
        from django.contrib.auth.models import Group
        
        admin_group, created = Group.objects.get_or_create(name='Admin')
        if created:
            print("   ✅ Grupo 'Admin' criado")
        else:
            print("   ℹ️ Grupo 'Admin' já existe")
        
        employee_group, created = Group.objects.get_or_create(name='Colaborador')
        if created:
            print("   ✅ Grupo 'Colaborador' criado")
        else:
            print("   ℹ️ Grupo 'Colaborador' já existe")
            
    except Exception as e:
        print(f"   ❌ Erro ao criar grupos: {e}")
    
    # Verificar se as tabelas foram criadas
    print("\n🔍 Verificando tabelas criadas...")
    important_tables = [
        'accounts_userprofile',
        'employees_employee',
        'documents_documentrequest',
        'knowledge_base_knowledgeentry',
        'calendar_calendarevent'
    ]
    
    for table in important_tables:
        if check_table_exists(table):
            print(f"   ✅ Tabela {table} existe")
        else:
            print(f"   ❌ Tabela {table} NÃO existe")
    
    print("\n" + "=" * 50)
    print("🎉 Correção de migrações concluída!")
    print("\nPróximos passos:")
    print("1. python manage.py createsuperuser")
    print("2. python manage.py runserver")
    print("3. Acesse http://127.0.0.1:8000")
    print("=" * 50)
    
    return True

if __name__ == "__main__":
    main()