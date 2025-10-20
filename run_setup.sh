#!/bin/bash

echo "========================================"
echo "HR Internal System - Setup Linux/Mac"
echo "INFRASECUR MOÇAMBIQUE LTD"
echo "========================================"

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "ERRO: Python 3 não encontrado. Instale Python 3.8+ primeiro."
    exit 1
fi

echo "Python encontrado!"
python3 --version

# Verificar se pip está instalado
if ! command -v pip3 &> /dev/null; then
    echo "ERRO: pip3 não encontrado. Instale pip primeiro."
    exit 1
fi

# Criar ambiente virtual
echo "Criando ambiente virtual..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "ERRO: Falha ao criar ambiente virtual"
    exit 1
fi

# Ativar ambiente virtual
echo "Ativando ambiente virtual..."
source venv/bin/activate

# Atualizar pip
echo "Atualizando pip..."
pip install --upgrade pip

# Executar setup
echo "Executando setup automatizado..."
python setup.py

echo ""
echo "========================================"
echo "Setup concluído!"
echo "Para iniciar o servidor:"
echo "1. source venv/bin/activate"
echo "2. python manage.py runserver"
echo "========================================"