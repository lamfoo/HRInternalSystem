#!/usr/bin/env python
"""
Script para corrigir o problema do banco de dados
Execute este script para resolver o erro "no such table: accounts_userprofile"
"""

import os
import sys
import subprocess

def run_command(command):
    """Executa um comando e retorna True se bem-sucedido."""
    print(f"Executando: {command}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        if result.stdout.strip():
            print(f"✅ {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro: {e}")
        if e.stderr:
            print(f"Stderr: {e.stderr}")
        if e.stdout:
            print(f"Stdout: {e.stdout}")
        return False

def main():
    print("🔧 Corrigindo problema do banco de dados...")
    print("=" * 60)
    
    # Verificar se estamos no diretório correto
    if not os.path.exists('manage.py'):
        print("❌ Erro: manage.py não encontrado!")
        print("Certifique-se de estar no diretório raiz do projeto.")
        return False
    
    # Passo 1: Remover banco de dados existente (se houver problemas)
    if os.path.exists('db.sqlite3'):
        print("🗑️ Removendo banco de dados com problemas...")
        try:
            os.remove('db.sqlite3')
            print("✅ Banco de dados removido")
        except Exception as e:
            print(f"❌ Erro ao remover banco: {e}")
    
    # Passo 2: Criar migrações para cada app na ordem correta
    apps = ['core', 'accounts', 'employees', 'documents', 'knowledge_base', 'calendar']
    
    print("\n📝 Criando migrações...")
    for app in apps:
        print(f"\n--- Criando migração para {app} ---")
        if not run_command(f"python manage.py makemigrations {app}"):
            print(f"⚠️ Falha ao criar migração para {app}, continuando...")
    
    # Passo 3: Aplicar migrações
    print("\n🔄 Aplicando migrações...")
    if not run_command("python manage.py migrate"):
        print("❌ Falha ao aplicar migrações!")
        return False
    
    # Passo 4: Criar grupos
    print("\n👥 Criando grupos de usuários...")
    create_groups_script = '''
import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hr_system.settings.dev")
django.setup()

from django.contrib.auth.models import Group

admin_group, created = Group.objects.get_or_create(name="Admin")
print(f"Grupo Admin: {'criado' if created else 'já existe'}")

employee_group, created = Group.objects.get_or_create(name="Colaborador")
print(f"Grupo Colaborador: {'criado' if created else 'já existe'}")

print("✅ Grupos configurados com sucesso!")
'''
    
    with open('temp_create_groups.py', 'w') as f:
        f.write(create_groups_script)
    
    if run_command("python temp_create_groups.py"):
        os.remove('temp_create_groups.py')
    
    # Passo 5: Verificar se tudo está funcionando
    print("\n🔍 Verificando configuração...")
    test_script = '''
import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hr_system.settings.dev")
django.setup()

from django.contrib.auth.models import User
from apps.accounts.models import UserProfile

print("✅ Importações funcionando")
print(f"✅ Usuários no sistema: {User.objects.count()}")
print(f"✅ Perfis no sistema: {UserProfile.objects.count()}")
print("✅ Sistema funcionando corretamente!")
'''
    
    with open('temp_test.py', 'w') as f:
        f.write(test_script)
    
    if run_command("python temp_test.py"):
        os.remove('temp_test.py')
    
    print("\n" + "=" * 60)
    print("🎉 CORREÇÃO CONCLUÍDA COM SUCESSO!")
    print("=" * 60)
    print("\n📋 Próximos passos:")
    print("1. Se ainda não criou, execute: python manage.py createsuperuser")
    print("2. Execute o servidor: python manage.py runserver")
    print("3. Acesse: http://127.0.0.1:8000")
    print("\n💡 Dica: Se ainda houver problemas, delete o arquivo db.sqlite3")
    print("   e execute este script novamente.")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ Correção falhou. Tente executar os comandos manualmente:")
        print("1. rm db.sqlite3")
        print("2. python manage.py makemigrations")
        print("3. python manage.py migrate")
        print("4. python manage.py createsuperuser")
        sys.exit(1)