#!/usr/bin/env python
"""
Script de correção rápida para problemas de migração
"""

import os
import subprocess
import sys

def run_command(command, description):
    """Executa um comando."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} - Concluído")
        if result.stdout:
            print(f"   {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Erro:")
        if e.stderr:
            print(f"   {e.stderr.strip()}")
        if e.stdout:
            print(f"   {e.stdout.strip()}")
        return False

def main():
    print("🚨 Correção Rápida - HR Internal System")
    print("=" * 50)
    
    # Parar se houver erro
    commands = [
        ("python manage.py makemigrations core", "Criando migrações do core"),
        ("python manage.py makemigrations accounts", "Criando migrações do accounts"),
        ("python manage.py makemigrations employees", "Criando migrações do employees"),
        ("python manage.py makemigrations documents", "Criando migrações do documents"),
        ("python manage.py makemigrations knowledge_base", "Criando migrações do knowledge_base"),
        ("python manage.py makemigrations calendar", "Criando migrações do calendar"),
        ("python manage.py migrate", "Aplicando todas as migrações"),
    ]
    
    for command, description in commands:
        if not run_command(command, description):
            print(f"\n❌ Falha em: {description}")
            print("Tente executar manualmente:")
            print(f"   {command}")
            return False
    
    print("\n✅ Correção concluída com sucesso!")
    print("\nAgora você pode:")
    print("1. python manage.py createsuperuser (se ainda não criou)")
    print("2. python manage.py runserver")
    print("3. Acessar http://127.0.0.1:8000")
    
    return True

if __name__ == "__main__":
    main()