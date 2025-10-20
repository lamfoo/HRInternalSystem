#!/usr/bin/env python
"""
Script de setup automatizado para o HR Internal System
"""

import os
import sys
import subprocess
import django
from django.core.management import execute_from_command_line
from django.contrib.auth.models import Group, User


def run_command(command, description):
    """Executa um comando e exibe o resultado."""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} - Concluído")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Erro: {e}")
        print(f"Saída do erro: {e.stderr}")
        return False


def setup_django():
    """Configura o Django e cria dados iniciais."""
    print("\n🔄 Configurando Django...")
    
    # Configurar Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hr_system.settings.dev')
    django.setup()
    
    # Importar após configurar Django
    from django.contrib.auth.models import Group, User
    
    # Criar grupos
    print("📝 Criando grupos de usuários...")
    admin_group, created = Group.objects.get_or_create(name='Admin')
    if created:
        print("✅ Grupo 'Admin' criado")
    else:
        print("ℹ️ Grupo 'Admin' já existe")
    
    employee_group, created = Group.objects.get_or_create(name='Colaborador')
    if created:
        print("✅ Grupo 'Colaborador' criado")
    else:
        print("ℹ️ Grupo 'Colaborador' já existe")
    
    # Verificar se já existe superusuário
    if not User.objects.filter(is_superuser=True).exists():
        print("\n👤 Criando superusuário...")
        print("Por favor, forneça as informações do administrador:")
        
        username = input("Nome de usuário: ").strip()
        email = input("Email: ").strip()
        
        if username and email:
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password='admin123'  # Senha padrão - deve ser alterada
            )
            user.groups.add(admin_group)
            print(f"✅ Superusuário '{username}' criado com sucesso!")
            print("⚠️ Senha padrão: 'admin123' - ALTERE IMEDIATAMENTE após o primeiro login!")
        else:
            print("❌ Nome de usuário e email são obrigatórios")
    else:
        print("ℹ️ Superusuário já existe")
    
    print("✅ Configuração do Django concluída")


def create_directories():
    """Cria diretórios necessários."""
    print("\n📁 Criando diretórios necessários...")
    
    directories = [
        'media',
        'media/documents',
        'media/documents/declarations',
        'media/avatars',
        'media/knowledge_base',
        'media/calendar',
        'media/templates',
        'staticfiles',
        'logs'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Diretório '{directory}' criado/verificado")


def main():
    """Função principal do setup."""
    print("🚀 HR Internal System - Setup Automatizado")
    print("=" * 50)
    print("INFRASECUR MOÇAMBIQUE LTD")
    print("=" * 50)
    
    # Verificar se está em um ambiente virtual
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️ AVISO: Recomenda-se executar em um ambiente virtual (venv)")
        response = input("Continuar mesmo assim? (s/N): ").lower()
        if response != 's':
            print("❌ Setup cancelado")
            return
    
    # Verificar Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ é necessário")
        return
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    
    # Instalar dependências
    if not run_command("pip install -r requirements.txt", "Instalando dependências"):
        return
    
    # Criar diretórios
    create_directories()
    
    # Executar migrações
    if not run_command("python manage.py makemigrations", "Criando migrações"):
        return
    
    if not run_command("python manage.py migrate", "Aplicando migrações"):
        return
    
    # Configurar Django e criar dados iniciais
    setup_django()
    
    # Coletar arquivos estáticos
    if not run_command("python manage.py collectstatic --noinput", "Coletando arquivos estáticos"):
        return
    
    print("\n" + "=" * 50)
    print("🎉 SETUP CONCLUÍDO COM SUCESSO!")
    print("=" * 50)
    print("\n📋 PRÓXIMOS PASSOS:")
    print("1. Execute: python manage.py runserver")
    print("2. Acesse: http://127.0.0.1:8000")
    print("3. Faça login com o superusuário criado")
    print("4. ALTERE a senha padrão imediatamente!")
    print("5. Configure as variáveis de ambiente no arquivo .env")
    print("\n📧 CONFIGURAÇÃO DE EMAIL:")
    print("- Copie .env.example para .env")
    print("- Configure as credenciais de email")
    print("- Reinicie o servidor após as alterações")
    print("\n🔒 SEGURANÇA:")
    print("- Altere a SECRET_KEY em produção")
    print("- Configure DEBUG=False em produção")
    print("- Use HTTPS em produção")
    print("\n📞 SUPORTE:")
    print("- Email: rh@infrasecur.co.mz")
    print("- Telefone: +258 21 123 456")
    print("\n" + "=" * 50)


if __name__ == "__main__":
    main()