# Guia de Instalação - HR Internal System

Este guia fornece instruções detalhadas para instalar e configurar o HR Internal System.

## 📋 Pré-requisitos

### Sistema Operacional
- Windows 10/11, macOS 10.15+, ou Linux (Ubuntu 18.04+)

### Software Necessário
- **Python 3.8+** (recomendado: 3.12)
- **pip** (gerenciador de pacotes Python)
- **Git** (controle de versão)
- **PostgreSQL** (opcional, para produção)

### Verificação dos Pré-requisitos

```bash
# Verificar Python
python --version
# ou
python3 --version

# Verificar pip
pip --version
# ou
pip3 --version

# Verificar Git
git --version
```

## 🚀 Instalação Rápida (Recomendada)

### Windows
1. Baixe e execute o script de setup:
```cmd
run_setup.bat
```

### Linux/Mac
1. Torne o script executável e execute:
```bash
chmod +x run_setup.sh
./run_setup.sh
```

## 🔧 Instalação Manual

### 1. Clone o Repositório
```bash
git clone <url-do-repositorio>
cd hr-internal-system
```

### 2. Crie um Ambiente Virtual

#### Windows
```cmd
python -m venv venv
venv\Scripts\activate
```

#### Linux/Mac
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instale as Dependências
```bash
pip install -r requirements.txt
```

### 4. Configure as Variáveis de Ambiente
```bash
# Copie o arquivo de exemplo
cp .env.example .env

# Edite o arquivo .env
nano .env  # Linux/Mac
notepad .env  # Windows
```

#### Configurações Mínimas (.env)
```env
SECRET_KEY=sua-chave-secreta-aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Email (opcional para desenvolvimento)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

### 5. Crie os Diretórios Necessários
```bash
mkdir -p media/documents/declarations
mkdir -p media/avatars
mkdir -p media/knowledge_base
mkdir -p media/calendar
mkdir -p staticfiles
mkdir -p logs
```

### 6. Execute as Migrações
```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Crie os Grupos de Usuários
```bash
python manage.py shell
```

```python
from django.contrib.auth.models import Group

# Criar grupos
admin_group, created = Group.objects.get_or_create(name='Admin')
employee_group, created = Group.objects.get_or_create(name='Colaborador')

print("Grupos criados!")
exit()
```

### 8. Crie um Superusuário
```bash
python manage.py createsuperuser
```

### 9. Colete Arquivos Estáticos
```bash
python manage.py collectstatic
```

### 10. Execute o Servidor
```bash
python manage.py runserver
```

Acesse: http://127.0.0.1:8000

## 🗄️ Configuração do Banco de Dados

### SQLite (Desenvolvimento - Padrão)
Não requer configuração adicional. O arquivo `db.sqlite3` será criado automaticamente.

### PostgreSQL (Produção)

#### 1. Instale o PostgreSQL
```bash
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# CentOS/RHEL
sudo yum install postgresql-server postgresql-contrib

# macOS (com Homebrew)
brew install postgresql

# Windows
# Baixe o instalador oficial do PostgreSQL
```

#### 2. Crie o Banco de Dados
```bash
sudo -u postgres psql

CREATE DATABASE hr_system_db;
CREATE USER hr_user WITH PASSWORD 'sua_senha';
GRANT ALL PRIVILEGES ON DATABASE hr_system_db TO hr_user;
\q
```

#### 3. Instale o Adaptador Python
```bash
pip install psycopg2-binary
```

#### 4. Configure no .env
```env
DB_ENGINE=django.db.backends.postgresql
DB_NAME=hr_system_db
DB_USER=hr_user
DB_PASSWORD=sua_senha
DB_HOST=localhost
DB_PORT=5432
```

## 📧 Configuração de Email

### Gmail (Desenvolvimento/Teste)
```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=sua-senha-de-app
DEFAULT_FROM_EMAIL=noreply@hrinternalsystem.com
```

**Nota**: Para Gmail, use uma "Senha de App" em vez da senha normal.

### Outros Provedores
```env
# Outlook/Hotmail
EMAIL_HOST=smtp-mail.outlook.com
EMAIL_PORT=587

# Yahoo
EMAIL_HOST=smtp.mail.yahoo.com
EMAIL_PORT=587

# SMTP Personalizado
EMAIL_HOST=seu-servidor-smtp.com
EMAIL_PORT=587
```

## 🔒 Configuração de Produção

### 1. Variáveis de Ambiente de Produção
```env
SECRET_KEY=sua-chave-secreta-super-segura
DEBUG=False
ALLOWED_HOSTS=seu-dominio.com,www.seu-dominio.com

# Banco de Dados
DB_ENGINE=django.db.backends.postgresql
DB_NAME=hr_system_prod
DB_USER=hr_prod_user
DB_PASSWORD=senha-super-segura
DB_HOST=localhost
DB_PORT=5432

# Email
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.seu-provedor.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=noreply@sua-empresa.com
EMAIL_HOST_PASSWORD=senha-do-email
```

### 2. Configurações de Segurança
```env
# HTTPS (obrigatório em produção)
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
```

### 3. Servidor Web (Nginx + Gunicorn)

#### Instale o Gunicorn
```bash
pip install gunicorn
```

#### Configure o Gunicorn
```bash
# Crie o arquivo gunicorn.conf.py
bind = "127.0.0.1:8000"
workers = 3
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 30
keepalive = 2
```

#### Execute com Gunicorn
```bash
gunicorn hr_system.wsgi:application -c gunicorn.conf.py
```

#### Configure o Nginx
```nginx
server {
    listen 80;
    server_name seu-dominio.com;
    
    location /static/ {
        alias /caminho/para/hr-internal-system/staticfiles/;
    }
    
    location /media/ {
        alias /caminho/para/hr-internal-system/media/;
    }
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 🐳 Docker (Opcional)

### Dockerfile
```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "hr_system.wsgi:application", "--bind", "0.0.0.0:8000"]
```

### docker-compose.yml
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=False
      - DATABASE_URL=postgresql://hr_user:password@db:5432/hr_system_db
    depends_on:
      - db
    volumes:
      - ./media:/app/media

  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=hr_system_db
      - POSTGRES_USER=hr_user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

## 🧪 Verificação da Instalação

### 1. Execute os Testes
```bash
python manage.py test
```

### 2. Verifique as URLs
- http://127.0.0.1:8000 - Página de login
- http://127.0.0.1:8000/admin - Django Admin
- http://127.0.0.1:8000/accounts/login/ - Login customizado

### 3. Teste as Funcionalidades
1. Faça login com o superusuário
2. Acesse o dashboard
3. Crie um colaborador de teste
4. Teste a requisição de documentos
5. Verifique o calendário

## 🔧 Solução de Problemas

### Erro: "No module named 'apps'"
```bash
# Certifique-se de estar no diretório correto
cd hr-internal-system

# Verifique se o ambiente virtual está ativo
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### Erro: "CSRF verification failed"
Verifique se `CSRF_COOKIE_SECURE = False` em desenvolvimento.

### Erro: "Database connection failed"
1. Verifique as configurações do banco no .env
2. Certifique-se de que o PostgreSQL está rodando
3. Teste a conexão manualmente

### Erro: "Static files not found"
```bash
python manage.py collectstatic --clear
```

### Erro: "Permission denied"
```bash
# Linux/Mac - ajustar permissões
chmod -R 755 media/
chmod -R 755 staticfiles/
```

## 📞 Suporte

### Documentação
- README.md - Visão geral do projeto
- CHANGELOG.md - Histórico de mudanças
- Este arquivo (INSTALL.md) - Guia de instalação

### Contato
- **Email**: rh@infrasecur.co.mz
- **Telefone**: +258 21 123 456

### Logs de Debug
```bash
# Ativar logs detalhados
export DJANGO_LOG_LEVEL=DEBUG
python manage.py runserver

# Verificar logs
tail -f logs/django.log
```

---

**Desenvolvido para INFRASECUR MOÇAMBIQUE LTD**