@echo off
echo ========================================
echo HR Internal System - Setup Windows
echo INFRASECUR MOCAMBIQUE LTD
echo ========================================

REM Verificar se Python está instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERRO: Python nao encontrado. Instale Python 3.8+ primeiro.
    pause
    exit /b 1
)

echo Python encontrado!

REM Criar ambiente virtual
echo Criando ambiente virtual...
python -m venv venv
if %errorlevel% neq 0 (
    echo ERRO: Falha ao criar ambiente virtual
    pause
    exit /b 1
)

REM Ativar ambiente virtual
echo Ativando ambiente virtual...
call venv\Scripts\activate.bat

REM Executar setup
echo Executando setup automatizado...
python setup.py

echo.
echo ========================================
echo Setup concluido!
echo Para iniciar o servidor:
echo 1. venv\Scripts\activate.bat
echo 2. python manage.py runserver
echo ========================================
pause