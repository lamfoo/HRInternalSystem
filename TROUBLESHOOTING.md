# Guia de Solução de Problemas - HR Internal System

## 🚨 Erro: "no such table: accounts_userprofile"

Este é um erro comum que acontece quando as migrações do Django não foram executadas corretamente.

### ✅ Solução Rápida (Recomendada)

Execute o script de correção automática:

```bash
python fix_database.py
```

### 🔧 Solução Manual

Se o script automático não funcionar, siga estes passos:

#### 1. Remover banco de dados problemático
```bash
rm db.sqlite3
```

#### 2. Criar migrações na ordem correta
```bash
python manage.py makemigrations core
python manage.py makemigrations accounts
python manage.py makemigrations employees
python manage.py makemigrations documents
python manage.py makemigrations knowledge_base
python manage.py makemigrations calendar
```

#### 3. Aplicar migrações
```bash
python manage.py migrate
```

#### 4. Criar grupos de usuários
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

#### 5. Criar superusuário
```bash
python manage.py createsuperuser
```

#### 6. Executar servidor
```bash
python manage.py runserver
```

## 🔍 Outros Problemas Comuns

### Erro: "ModuleNotFoundError: No module named 'apps'"

**Solução:**
```bash
# Certifique-se de estar no diretório correto
cd hr-internal-system

# Ative o ambiente virtual
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

### Erro: "CSRF verification failed"

**Solução:**
Verifique se `CSRF_COOKIE_SECURE = False` no arquivo `hr_system/settings/dev.py`.

### Erro: "Static files not found"

**Solução:**
```bash
python manage.py collectstatic --clear
```

### Erro: "Permission denied" (Linux/Mac)

**Solução:**
```bash
chmod -R 755 media/
chmod -R 755 staticfiles/
```

### Erro: "Port already in use"

**Solução:**
```bash
# Use uma porta diferente
python manage.py runserver 8001

# Ou mate o processo na porta 8000
lsof -ti:8000 | xargs kill -9  # Linux/Mac
netstat -ano | findstr :8000   # Windows
```

## 🔄 Reset Completo do Sistema

Se nada funcionar, faça um reset completo:

```bash
# 1. Remover banco de dados
rm db.sqlite3

# 2. Remover migrações antigas
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete

# 3. Recriar migrações
python manage.py makemigrations
python manage.py migrate

# 4. Recriar superusuário
python manage.py createsuperuser

# 5. Executar script de setup
python setup.py
```

## 📞 Suporte

Se os problemas persistirem:

1. **Verifique os logs**: Procure por mensagens de erro detalhadas
2. **Ambiente virtual**: Certifique-se de que está ativo
3. **Dependências**: Execute `pip install -r requirements.txt` novamente
4. **Python version**: Certifique-se de usar Python 3.8+

### Informações para Suporte

Ao relatar problemas, inclua:

- Sistema operacional
- Versão do Python (`python --version`)
- Mensagem de erro completa
- Passos que levaram ao erro

### Contato

- **Email**: rh@infrasecur.co.mz
- **Telefone**: +258 21 123 456

## 🛠️ Comandos Úteis para Debug

```bash
# Verificar status das migrações
python manage.py showmigrations

# Verificar configurações do Django
python manage.py check

# Abrir shell do Django
python manage.py shell

# Verificar usuários existentes
python manage.py shell -c "from django.contrib.auth.models import User; print(f'Usuários: {User.objects.count()}')"

# Verificar grupos
python manage.py shell -c "from django.contrib.auth.models import Group; print([g.name for g in Group.objects.all()])"

# Verificar tabelas no banco
python manage.py dbshell
.tables  # SQLite
\dt      # PostgreSQL
```

## 📝 Logs de Debug

Para ativar logs detalhados:

```bash
export DJANGO_LOG_LEVEL=DEBUG
python manage.py runserver
```

Ou adicione no `settings/dev.py`:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
}
```

---

**Desenvolvido para INFRASECUR MOÇAMBIQUE LTD**