# HR Internal System

Sistema interno de gerenciamento de recursos humanos desenvolvido para a **INFRASECUR MOÇAMBIQUE LTD**.

## 📋 Sobre o Projeto

O HR Internal System é uma aplicação web completa desenvolvida em Django que oferece funcionalidades essenciais para o gerenciamento de recursos humanos, incluindo:

- 👥 **Gestão de Colaboradores**: Cadastro completo com informações pessoais, profissionais e salariais
- 📄 **Requisição de Documentos**: Sistema automatizado para solicitação e geração de documentos (declarações, comprovantes, etc.)
- 📚 **Base de Conhecimento**: Plataforma colaborativa para compartilhamento de soluções e procedimentos
- 📅 **Calendário Interno**: Gestão de eventos, férias, reuniões e compromissos da equipe
- 🔐 **Sistema de Autenticação**: Controle de acesso baseado em roles (Admin/Colaborador)

## 🚀 Funcionalidades Principais

### Autenticação e Autorização
- Login/logout seguro
- Role-Based Access Control (RBAC)
- Grupos: Admin e Colaborador
- Perfis de usuário personalizáveis

### Gestão de Colaboradores
- Cadastro completo de colaboradores
- Informações pessoais, profissionais e salariais
- Controle de status (ativo, inativo, suspenso, férias)
- Diferentes tipos de contrato
- Estatísticas e relatórios

### Sistema de Documentos
- Requisição online de documentos
- Geração automática de documentos Word (.docx)
- Templates personalizáveis
- Aprovação/rejeição por administradores
- Envio automático por email
- Histórico completo de requisições

### Base de Conhecimento
- Criação de entradas de conhecimento
- Categorização e tags
- Sistema de comentários
- Avaliações e feedback
- Busca avançada
- Anexos e arquivos

### Calendário Interno
- Interface FullCalendar integrada
- Diferentes tipos de eventos
- Aprovação de eventos
- Notificações automáticas
- Drag-and-drop para reorganização
- Filtros e visualizações personalizadas

## 🛠️ Tecnologias Utilizadas

### Backend
- **Python 3.12+**
- **Django 5.1+**
- **SQLite** (desenvolvimento) / **PostgreSQL** (produção)
- **python-docx** (geração de documentos Word)
- **ReportLab** (geração de PDFs)
- **python-decouple** (configurações)

### Frontend
- **HTML5**
- **Bootstrap 5.3** (framework CSS responsivo)
- **Bootstrap Icons**
- **FullCalendar 6** (calendário interativo)
- **jQuery** (compatibilidade)
- **JavaScript ES6+**

### Ferramentas
- **Django Crispy Forms** (formulários estilizados)
- **Git** (controle de versão)
- **Virtualenv** (ambiente virtual)

## 📦 Instalação e Configuração

### Pré-requisitos
- Python 3.12 ou superior
- pip (gerenciador de pacotes Python)
- Git

### 1. Clone o Repositório
```bash
git clone <url-do-repositorio>
cd hr-internal-system
```

### 2. Crie um Ambiente Virtual
```bash
python -m venv venv

# Windows
venv\\Scripts\\activate

# Linux/Mac
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

# Edite o arquivo .env com suas configurações
```

### 5. Execute as Migrações
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Crie um Superusuário
```bash
python manage.py createsuperuser
```

### 7. Crie os Grupos Iniciais
```bash
python manage.py shell
```

```python
from django.contrib.auth.models import Group

# Criar grupos
admin_group, created = Group.objects.get_or_create(name='Admin')
employee_group, created = Group.objects.get_or_create(name='Colaborador')

print("Grupos criados com sucesso!")
exit()
```

### 8. Execute o Servidor de Desenvolvimento
```bash
python manage.py runserver
```

Acesse: http://127.0.0.1:8000

## 🔧 Configuração de Produção

### Banco de Dados PostgreSQL
```bash
# Instale o adaptador PostgreSQL
pip install psycopg2-binary

# Configure no .env
DB_ENGINE=django.db.backends.postgresql
DB_NAME=hr_system_db
DB_USER=hr_user
DB_PASSWORD=sua_senha
DB_HOST=localhost
DB_PORT=5432
```

### Configuração de Email
```bash
# Configure no .env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=sua-senha-de-app
```

### Deploy
```bash
# Colete arquivos estáticos
python manage.py collectstatic

# Use configurações de produção
export DJANGO_SETTINGS_MODULE=hr_system.settings.prod
```

## 📁 Estrutura do Projeto

```
hr-internal-system/
├── apps/                          # Apps modulares
│   ├── accounts/                  # Autenticação e perfis
│   ├── calendar/                  # Calendário interno
│   ├── core/                      # Funcionalidades base
│   ├── documents/                 # Requisição de documentos
│   ├── employees/                 # Gestão de colaboradores
│   └── knowledge_base/            # Base de conhecimento
├── hr_system/                     # Configurações do projeto
│   ├── settings/                  # Configurações por ambiente
│   │   ├── base.py               # Configurações base
│   │   ├── dev.py                # Desenvolvimento
│   │   └── prod.py               # Produção
│   ├── urls.py                   # URLs principais
│   └── wsgi.py                   # WSGI
├── media/                         # Arquivos de upload
├── static/                        # Arquivos estáticos
│   ├── css/                      # Estilos customizados
│   ├── js/                       # JavaScript customizado
│   └── img/                      # Imagens
├── templates/                     # Templates HTML
│   ├── base/                     # Templates base
│   ├── accounts/                 # Templates de autenticação
│   ├── calendar/                 # Templates do calendário
│   ├── core/                     # Templates principais
│   ├── documents/                # Templates de documentos
│   ├── employees/                # Templates de colaboradores
│   └── knowledge_base/           # Templates da base de conhecimento
├── manage.py                      # Script de gerenciamento Django
├── requirements.txt               # Dependências Python
├── .env.example                  # Exemplo de configurações
├── .gitignore                    # Arquivos ignorados pelo Git
└── README.md                     # Este arquivo
```

## 👥 Sistema de Permissões

### Administradores (Grupo: Admin)
- ✅ Gerenciar todos os colaboradores
- ✅ Aprovar/rejeitar requisições de documentos
- ✅ Moderar base de conhecimento
- ✅ Gerenciar eventos do calendário
- ✅ Acessar estatísticas e relatórios
- ✅ Criar novos usuários

### Colaboradores (Grupo: Colaborador)
- ✅ Ver próprio perfil
- ✅ Solicitar documentos
- ✅ Acessar base de conhecimento
- ✅ Criar entradas de conhecimento
- ✅ Visualizar calendário
- ✅ Criar eventos pessoais
- ❌ Gerenciar outros usuários

## 📊 Módulos Detalhados

### 1. Gestão de Colaboradores (`apps/employees/`)
- **Modelo**: Employee com campos completos
- **Funcionalidades**: CRUD, busca, filtros, estatísticas
- **Campos**: Nome, endereço, documento, email, cargo, salário, etc.

### 2. Sistema de Documentos (`apps/documents/`)
- **Modelos**: DocumentRequest, DocumentTemplate, DocumentHistory
- **Funcionalidades**: Requisição, aprovação, geração automática
- **Tipos**: Declaração de rendimentos, comprovantes, certificados

### 3. Base de Conhecimento (`apps/knowledge_base/`)
- **Modelos**: KnowledgeEntry, KnowledgeCategory, KnowledgeComment
- **Funcionalidades**: Criação, categorização, comentários, avaliações
- **Recursos**: Busca, tags, anexos, moderação

### 4. Calendário (`apps/calendar/`)
- **Modelos**: CalendarEvent, CalendarNotification, CalendarSettings
- **Funcionalidades**: Eventos, aprovações, notificações
- **Interface**: FullCalendar com drag-and-drop

## 🧪 Testes

Execute os testes unitários:
```bash
python manage.py test
```

Execute testes específicos:
```bash
python manage.py test apps.employees.tests
python manage.py test apps.documents.tests
```

## 📈 Monitoramento e Logs

### Logs de Desenvolvimento
Os logs são exibidos no console durante o desenvolvimento.

### Logs de Produção
Configure logs em arquivo no ambiente de produção:
```python
# settings/prod.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'logs/django.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

## 🔒 Segurança

### Medidas Implementadas
- ✅ CSRF Protection
- ✅ XSS Protection
- ✅ SQL Injection Protection (Django ORM)
- ✅ Secure Headers
- ✅ Password Hashing (PBKDF2)
- ✅ Session Security
- ✅ File Upload Validation

### Configurações de Segurança
```python
# settings/prod.py
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
```

## 🎨 Interface e UX

### Design Responsivo
- ✅ Bootstrap 5 Grid System
- ✅ Mobile-first approach
- ✅ Breakpoints: xs, sm, md, lg, xl
- ✅ Componentes responsivos

### Acessibilidade
- ✅ Semantic HTML
- ✅ ARIA labels
- ✅ Keyboard navigation
- ✅ Screen reader support

## 📞 Suporte e Contato

### Informações da Empresa
**INFRASECUR MOÇAMBIQUE LTD**
- 📍 Endereço: Rua da Resistência, nº 1234 - Maputo, Moçambique
- ☎️ Telefone: +258 21 123 456
- ✉️ Email: rh@infrasecur.co.mz

### Suporte Técnico
Para questões técnicas ou bugs, entre em contato com a equipe de TI.

## 📝 Licença

Este projeto é propriedade da **INFRASECUR MOÇAMBIQUE LTD** e destina-se exclusivamente ao uso interno da empresa.

## 🚀 Roadmap Futuro

### Versão 1.1
- [ ] Dashboard com gráficos interativos
- [ ] Relatórios em PDF
- [ ] Integração com API externa
- [ ] Notificações push

### Versão 1.2
- [ ] App mobile (PWA)
- [ ] Chat interno
- [ ] Workflow de aprovações
- [ ] Backup automático

### Versão 2.0
- [ ] Módulo de folha de pagamento
- [ ] Avaliação de desempenho
- [ ] Treinamentos online
- [ ] Integração com biometria

---

**Desenvolvido com ❤️ para a INFRASECUR MOÇAMBIQUE LTD**

*Sistema HR Internal - Versão 1.0.0*