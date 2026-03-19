# Guia de Configuração do Projeto Django com Docker e Docker Compose

Guia completo para configurar um projeto Django com modelo de Usuário customizado, gerenciamento de dependências com uv, infraestrutura Docker, Tailwind CSS v4 e HTMX.

## Índice

1. [Pré-requisitos](#pré-requisitos)
2. [Seleção da Versão do Django](#seleção-da-versão-do-django)
3. [Pré-requisitos do Projeto](#pré-requisitos-do-projeto)
4. [Configuração do Projeto Django](#configuração-do-projeto-django)
5. [Configuração do Ambiente](#configuração-do-ambiente)
6. [Modelo de Usuário Customizado](#modelo-de-usuário-customizado)
7. [Infraestrutura Docker](#infraestrutura-docker)
8. [Tailwind CSS v4 Standalone](#tailwind-css-v4-standalone)
9. [EXECUÇÃO OBRIGATÓRIA DO PROJETO](#execução-obrigatória-do-projeto)
10. [Notas Importantes](#notas-importantes)
11. [Fluxo Obrigatório: Adicionar Dependências Python](#fluxo-obrigatório-adicionar-dependências-python)
12. [Validação da Aplicação](#validação-da-aplicação)
13. [Referências](#referências)

---

## ⚠️ INSTRUÇÕES PARA CRIAÇÃO DE PRD

**ATENÇÃO**: Se você está lendo este guia para criar um PRD (Product Requirements Document), siga ESTRICTAMENTE as regras abaixo:

### Regra 1: EXECUÇÃO LITERAL
- **NÃO modifique** qualquer configuração especificada neste guia
- **NÃO improvise** "melhorias" ou "adaptações"
- **NÃO substitua** tecnologias, comandos, paths ou estruturas
- Se o guia diz X, você faz X. Se você acha que X está "errado", você AINDA faz X

### Regra 2: PROIBIÇÕES EXPLÍCITAS
Ao criar o PRD, é **ESTRITAMENTE PROIBIDO**:

❌ **NÃO** substituir bind mounts por volumes nomeados Docker
❌ **NÃO** substituir arquivos de configuração separados (nginx.conf) por comandos inline
❌ **NÃO** substituir `env_file: .env` por variáveis de ambiente inline
❌ **NÃO** alterar paths especificados (ex: `core/static/core/js/htmx/`)
❌ **NÃO** usar raciocínio para "corrigir" supostos problemas de compatibilidade
❌ **NÃO** adicionar notas sobre "WSL2 incompatível" ou qualquer justificativa para mudar o guia

### Regra 3: EXEMPLOS DE VIOLAÇÕES

**O que o guia especifica:**
```yaml
volumes:
  - ./staticfiles:/code/staticfiles
```

**VIOLAÇÃO** (o que NÃO fazer):
```yaml
volumes:
  - staticfiles:/code/staticfiles  # ❌ Volume nomeado NÃO é bind mount
```

**O que o guia especifica:**
```yaml
env_file: .env
```

**VIOLAÇÃO** (o que NÃO fazer):
```yaml
environment:
  - SECRET_KEY=value  # ❌ Variáveis inline NÃO substituem env_file
```

### Regra 4: CHECKLIST DE VALIDAÇÃO

Ao criar o PRD, verifique que:
- [ ] Todo path de arquivo foi copiado EXATAMENTE como está no guia
- [ ] Todo comando foi copiado EXATAMENTE como está no guia
- [ ] Todo conteúdo de arquivo YAML/Python/HTML foi copiado EXATAMENTE
- [ ] Nenhuma "melhoria" ou "adaptação" foi adicionada
- [ ] Nenhuma justificativa do tipo "para compatibilidade com X" foi adicionada

### Regra 5: O GUIA É A ESPECIFICAÇÃO

**Este guia é a especificação, não uma sugestão.**

Se você tem dúvida sobre como implementar algo, a resposta está **neste guia**. Se o guia não menciona, você NÃO inventa.

---

## Pré-requisitos

As ferramentas a seguir devem estar **pré-instaladas pelo usuário na máquina host** antes de iniciar esta configuração. O agente de IA assume que estas já estão disponíveis, mas deverá verificar a versão do python no ambiente virtual:

- **uv** - Gerenciador de dependências Python (instalação via curl ou pip)
- **Docker Desktop** - Para executar containers
- **Git** - Controle de versão
- **ignr** - Gerenciador de arquivos ignorados


⚠️ **IMPORTANTE**: Este guia de configuração assume que todos os pré-requisitos acima já estão disponíveis no ambiente de desenvolvimento.

### Verificar as instalações:
```bash
uv --version
docker --version
git --version
uv tool list
```

### Verificação do ignr
**Nota**: O `ignr` não suporta `--version`. Verifique com:
```bash
ignr -h  # ou simplesmente: ignr --help
```

### Criar ambiente virtual com uv
```bash
uv venv 3.13
```

### Verificar a versão do python definida no ambiente virtual
```bash
uv python version
```
---

## Seleção da Versão do Django

⚠️ **INSTRUÇÃO DO AGENTE DE IA**: No início da execução, se já não tiver sido informado, pergunte ao usuário qual versão do Django ele deseja para o projeto, de preferência a versões LTS (Suporte de Longo Prazo).

### Versões Django Suportadas e Compatibilidade com Python

As seguintes versões Django estão disponíveis e sua compatibilidade com Python foi verificada usando MCP Context7:

| Versão Django | Versões Python Suportadas | Status de Suporte | Notas |
|---------------|--------------------------|----------------|-------|
| **Django 5.2** | 3.10, 3.11, 3.12, 3.13 | ✅ Última Estável | Recomendado para novos projetos com Python 3.11+ |
| **Django 5.0** | 3.10, 3.11, 3.12 | ✅ Estável | Boa alternativa para Python 3.11+ |
| **Django 4.2** | 3.8, 3.9, 3.10, 3.11 | ✅ LTS (Suporte de Longo Prazo) | Última versão a suportar Python 3.9 |
| **Django 6.0** | 3.12, 3.13, 3.14 | ❌ Não Compatível | Requer Python 3.12+, não compatível com Python 3.11 |

### Comparação de Versões

**Série Django 5.2.x** (Recomendado)
- ✅ Compatível com Python 3.10, 3.11, 3.12, 3.13
- ✅ Último lançamento estável com suporte ativo
- ✅ Inclui recursos modernos e melhorias
- ✅ Este guia utiliza Django 5.2.12 por padrão

**Série Django 4.2 LTS**
- ✅ Suporte de Longo Prazo até Abril 2026
- ✅ Última versão Django a suportar Python 3.9
- ✅ Estabilidade comprovada e atualizações de segurança

**Série Django 6.0**
- ⚠️ Requer Python 3.12, 3.13 ou 3.14
- ❌ **NÃO compatível** com o requisito Python 3.11 deste projeto
- ✅ Mais recentes recursos mas mudanças quebrantes em relação ao 5.x

### Prompt de Seleção

Pergunte ao usuário se ainda não selecionou uma versão do Django:
```
Qual versão do Django você gostaria de usar para este projeto?
1. Django 5.2.x (recomendado, Python 3.11+)
2. Django 5.0.x (estável, Python 3.11+)
3. Django 4.2.x (LTS, Python 3.9+)

Por favor, entre com sua escolha (1, 2 ou 3):
```

Com base na escolha do usuário, instale a versão apropriada na seção [Configuração do Projeto Django](#configuração-do-projeto-django):
- Para Django 5.2.x: `uv add "Django>=5.2,<6.0"`
- Para Django 5.0.x: `uv add "Django>=5.0,<6.0"`
- Para Django 4.2.x: `uv add "Django>=4.2,<5.0"`

Este guia assume **Django 5.2.12** como versão padrão se nenhuma escolha for especificada.

---

## Pré-requisitos do Projeto (Responsabilidades do Usuário)

⚠️ **IMPORTANTE**: O agente de IA será executado a partir do diretório raiz do projeto. Todos os passos a seguir devem ser concluídos:

⚠️ **Nota**: os nomes que não estão definidos como no caso do [nome_do_projeto] deverá ser alterado pelo nome do diretório parent da raiz do projeto. A versão do python será definida pelo uv ao criar o ambiente virtual.

### 1. Descobrir o Nome do Projeto = "nome_do_diretório_parent_da_raiz_do_projeto"
```bash
pwd
```

### 2. Criar Ambiente Virtual com uv
```bash
uv init --python 3.13
uv venv
```

### 3. Criar o arquivo .gitignore
```bash
ignr -p django > .gitignore
```

### 4. Adicionar ao final do .gitignore
```.gitignore
statifiles/
data/
node_modules/
```

---

## Configuração do Projeto Django

### 1. Instalar o Django e Dependências
```bash
uv add "Django>=5.0,<6.0" psycopg2-binary django_extensions python-dotenv django-htmx
```

### 2. Instalar Dependências de Desenvolvimento
```bash
uv add --dev pytest pytest-cov taskipy ruff
```

### 3. Instalar Dependências no Ambiente Virtual
```bash
uv sync
```

### 4. Criar Projeto Django
```bash
uv run python manage.py startproject core .
```

---

## Configuração do Ambiente

### 1. Criar Arquivo .env.example

⚠️ **CRÍTICO**: O arquivo `.env` **NUNCA** deve ser commitado no git. Use sempre `.env.example` como template.

Crie `.env.example` na raiz do projeto:

```bash
# Django Settings
SECRET_KEY='your-secret-key-here-change-in-production'
DEBUG=True
ALLOWED_HOSTS="*"
CSRF_TRUSTED_ORIGINS='http://localhost:8080,http://localhost:8000,http://127.0.0.1:8080,http://127.0.0.1:8000,https://localhost:8080,https://localhost:8000,https://127.0.0.1:8080,https://127.0.0.1:8000'

# Banco de dados
DB_ENGINE=postgresql
DB_USERNAME=postgres
DB_PASS=postgres
DB_HOST=db
DB_PORT=5432
DB_NAME=postgres

# Celery
CELERY_BROKER_URL=redis://redis:6379/0

# Elasticsearch
ELASTIC_USERNAME=elastic
ELASTIC_PASSWORD=changeme

# Email
SENDER_EMAIL_URL="entrypoint"
RECEIVER_EMAIL_LIST="example1@email.com,example2@email.com"
```

**Instruções para novos desenvolvedores:**

```bash
# Copiar o template para criar o .env local
cp .env.example .env

# Editar o .env com suas configurações locais
nano .env
```

### 2. Atualizar .gitignore

⚠️ **CRÍTICO**: Certifique-se de que `.env` está no `.gitignore` e `.env.example` NÃO:

```bash
# Verificar se .env está no gitignore
grep -q "^\.env$" .gitignore || echo ".env" >> .gitignore

# Remover .env do versionamento se foi adicionado acidentalmente
git rm --cached .env 2>/dev/null || true

# Adicionar .env.example ao versionamento
git add .env.example
```

## Modelo de Usuário Customizado

### 1. Criar a Aplicação Accounts
```bash
uv run python manage.py startapp accounts
```

### 2. Criar Modelo de Usuário Customizado
Edite `accounts/models.py`:

```python
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    pass
```

### 3. Registrar Usuário Customizado
Adicione a `core/settings.py`:

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_htmx',
    'django_extensions',
    'accounts',
]

AUTH_USER_MODEL = 'accounts.User'
```

### 4. Registrar Usuário no Admin
Edite `accounts/admin.py`:

```python
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    pass
```

### 5. Criar Modelos Base (Base Models)

Crie o módulo `core/base_models/` com classes base reutilizáveis para todos os modelos do projeto.

#### 5.1 Criar o Diretório
```bash
mkdir -p core/base_models
touch core/base_models/__init__.py
```

#### 5.2 Criar Mixins Base (`core/base_models/mixins.py`)
```python
from django.db import models


class TimestampMixin(models.Model):
    """Adiciona campos de timestamp (created_at, updated_at) aos modelos."""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SoftDeleteMixin(models.Model):
    """Permite soft delete nos modelos."""
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.save()
```

#### 5.3 Criar Modelo Base (`core/base_models/models.py`)
```python
from uuid import uuid4
from django.db import models
from .mixins import TimestampMixin, SoftDeleteMixin


class BaseModel(TimestampMixin, SoftDeleteMixin, models.Model):
    """Modelo base abstrato com todos os mixins."""
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    class Meta:
        abstract = True

    def update(self, commit=True, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        if commit:
            self.save()

    @staticmethod
    def get_columns():
        return []
```

#### 5.4 Atualizar `core/base_models/__init__.py`
```python
from .mixins import TimestampMixin, SoftDeleteMixin
from .models import BaseModel

__all__ = ['TimestampMixin', 'SoftDeleteMixin', 'BaseModel']
```

#### 5.5 Estrutura Final
```
core/
└── base_models/
    ├── __init__.py
    ├── mixins.py
    └── models.py
```

### 6. Criar e Aplicar as Migrações

⚠️ **IMPORTANTE**: Limpe o banco de dados e migrações existentes antes de criar o usuário customizado:

```bash
rm -f db.sqlite3
rm -rf users/migrations/
```

Depois:

```bash
uv run python manage.py makemigrations
uv run python manage.py migrate
```

### 7. Criar Superusuário
```bash
uv run python manage.py createsuperuser
```

## Infraestrutura Docker

### 1. Criar Dockerfile
Crie `Dockerfile` na raiz do projeto:

```dockerfile
# syntax=docker/dockerfile:1
FROM python:3.13-slim

# Variáveis de ambiente para otimizar o comportamento do Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Definir locale
ENV LANG=pt_BR.UTF-8
ENV LANGUAGE=pt_BR:pt
ENV LC_ALL=pt_BR.UTF-8

# Atualiza pacotes do sistema e instala o cliente do PostgreSQL
RUN apt-get update && \
    apt-get install -y --no-install-recommends postgresql-client && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Definir diretório de trabalho
WORKDIR /code

# Copiar e instalar dependências do projeto
COPY requirements.txt /code/
RUN pip install -U pip
RUN pip install -r requirements.txt

# Copiar o resto do código da aplicação
COPY . /code/

```

### 2. Criar .dockerignore
Crie `.dockerignore` na raiz do projeto:

```dockerignore
# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/

# Git
.git/
.gitignore

# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.so

# Django
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal

# Docker
docker-compose*.yml
Dockerfile*
.docker/
nginx.Dockerfile

# Documentation
README.md
*.md

# Data
data/
media/
staticfiles/

# Testing
.pytest_cache/
.coverage
htmlcov/

# Node
node_modules/
```

### 3. Criar docker-compose.yml
Crie `docker-compose.yml` na raiz do projeto:

```yaml
services:
  db:
    image: postgres:15
    stdin_open: true
    tty: true
    restart: always
    volumes:
      - ./data/db:/var/lib/postgresql/data
    env_file: .env
    environment:
      - POSTGRES_NAME=${DB_NAME}
      - POSTGRES_USER=${DB_USERNAME}
      - POSTGRES_PASSWORD=${DB_PASS}
      - POSTGRES_DB=${DB_NAME}
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USERNAME} -d ${DB_NAME}"]
      interval: 5s
      timeout: 10s
      retries: 20
    networks:
      - [nome_do_projeto_network]

  web:
    platform: linux/x86_64
    build: .
    stdin_open: true
    tty: true
    restart: always
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - .:/code
    ports:
      - "8000:8000"
    env_file: .env
    depends_on:
      db:
        condition: service_healthy
    networks:
      - [nome_do_projeto_network]

  nginx:
    build:
      context: .
      dockerfile: nginx.Dockerfile
    restart: always
    ports:
      - "8080:80"
    volumes:
      - ./staticfiles:/code/staticfiles
      - ./media:/code/media
      - ./staticfiles/errors:/etc/nginx/errors
    depends_on:
      - web
    networks:
      - [nome_do_projeto_network]

  redis:
    image: redis:6.2
    restart: always
    networks:
      - [nome_do_projeto_network]

  worker:
    build: .
    restart: always
    command: celery -A core worker --loglevel=info
    volumes:
      - .:/code
      - ./media:/code/media
    env_file: .env
    depends_on:
      - db
      - redis
    networks:
      - [nome_do_projeto_network]
    deploy:
      resources:
        limits:
          cpus: '2.00'
          memory: 2048M
        reservations:
          cpus: '1.00'
          memory: 1024M

networks:
  [nome_do_projeto_network]:
    driver: bridge
```

### 4. Criar Configuração do Nginx

#### 4.1. Criar nginx.conf
Crie `nginx.conf` na raiz do projeto:

```nginx
server {
    listen 80;

    server_name localhost;

    location / {
        proxy_pass http://web:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /code/staticfiles/;
    }

    location /media/ {
        alias /code/media/;
    }
}
```

### 5. Adicionar Dependências do Celery
```bash
uv add celery redis
```

### 6. Exportar Requisitos
```bash
uv lock
uv export --format requirements.txt --output requirements.txt --without-hashes
```

## Tailwind CSS v4 Standalone

Esta seção documenta a instalação e configuração do Tailwind CSS v4 usando o CLI standalone, sem necessidade de Node.js.

### 1. Baixar Tailwind CSS CLI Standalone (Opcional)

⚠️ **IMPORTANTE**: O Tailwind CSS CLI já está instalado no container Docker. O download local é **opcional** e apenas necessário se você quiser executar o build fora do Docker.

Para execução via Docker (recomendado), pule esta etapa e use as tasks configuradas na seção 4.

O Tailwind CSS v4 oferece um executável standalone que não requer Node.js. Baixe a versão apropriada para seu sistema operacional **apenas se precisar de execução local**:

#### Windows (PowerShell):
```powershell
mkdir -p bin
Invoke-WebRequest -Uri "https://github.com/tailwindlabs/tailwindcss/releases/latest/download/tailwindcss-windows-x64.exe" -OutFile "bin/tailwindcss.exe"
```

#### Windows (curl):
```bash
mkdir -p bin
curl -sLO "https://github.com/tailwindlabs/tailwindcss/releases/latest/download/tailwindcss-windows-x64.exe" -o bin/tailwindcss.exe
```

#### Linux:
```bash
mkdir -p bin
curl -sLO "https://github.com/tailwindlabs/tailwindcss/releases/latest/download/tailwindcss-linux-x64"
mv tailwindcss-linux-x64 bin/tailwindcss
chmod +x bin/tailwindcss
```

#### macOS:
```bash
mkdir -p bin
curl -sLO "https://github.com/tailwindlabs/tailwindcss/releases/latest/download/tailwindcss-macos-x64"
mv tailwindcss-macos-x64 bin/tailwindcss
chmod +x bin/tailwindcss
```

⚠️ **IMPORTANTE**: Para versões específicas, substitua `latest` pela versão desejada (ex: `v4.1.18`).

### 2. Criar Estrutura de Diretórios

Crie a estrutura de diretórios para os arquivos CSS e templates:

```bash
mkdir -p core/static/core/css
mkdir -p core/static/core/js
mkdir -p templates
mkdir -p scripts
```

### 3. Baixar HTMX (Versão Mais Recente)

⚠️ **IMPORTANTE**: Baixe sempre a versão mais recente do HTMX. Esta seção foi consultada via **MCP Context7** para garantir que você está usando a última versão estável.

**Versão mais recente do HTMX**: 2.0.8 (verificada em 2026-02-21)

#### 3.1. Baixar HTMX via CDN (Recomendado)

Crie o diretório para o HTMX e baixe a versão mais recente:

```bash
# Criar diretório para o HTMX
mkdir -p core/static/core/js/htmx

# Baixar versão mais recente do HTMX (2.0.8)
curl -sL https://unpkg.com/htmx.org@2.0.8/dist/htmx.min.js -o core/static/core/js/htmx/htmx.min.js
```

#### 3.2. Verificar Versão Atual

Para verificar sempre a versão mais recente disponível, consulte:

- **Site oficial**: https://htmx.org/
- **GitHub releases**: https://github.com/bigskysoftware/htmx/releases
- **CDN unpkg**: https://unpkg.com/htmx.org/ (mostra versão atual)
- **CDN jsDelivr**: https://www.jsdelivr.com/package/npm/htmx.org

#### 3.3. URLs Alternativas

Se a URL unpkg não funcionar, você pode usar:

```bash
# Via jsDelivr CDN
curl -sL https://cdn.jsdelivr.net/npm/htmx.org@2.0.8/dist/htmx.min.js -o core/static/js/core/htmx/htmx.min.js

# Ou especificar uma versão diferente (substitua X.X.X pela versão desejada)
curl -sL https://unpkg.com/htmx.org@X.X.X/dist/htmx.min.js -o core/static/core/js/htmx/htmx.min.js
```

⚠️ **NOTA**: O template `base.html` referencia o HTMX em:
```html
<script src="{% static 'core/js/htmx/htmx.min.js' %}" defer></script>
```

### 4. Criar Arquivo CSS de Entrada

Crie `core/static/core/css/input.css`:

```css
@import "tailwindcss";

/* Custom styles for Django */
@layer base {
  body {
    @apply bg-gray-50 text-gray-900 antialiased;
  }
}

@layer components {
  .btn {
    @apply px-4 py-2 rounded-lg font-medium transition-colors duration-200 inline-block cursor-pointer border-0;
  }
  
  .btn-primary {
    @apply px-4 py-2 rounded-lg font-medium transition-colors duration-200 inline-block cursor-pointer border-0 bg-blue-600 text-white hover:bg-blue-700;
  }
  
  .btn-secondary {
    @apply px-4 py-2 rounded-lg font-medium transition-colors duration-200 inline-block cursor-pointer border-0 bg-gray-200 text-gray-800 hover:bg-gray-300;
  }
  
  .card {
    @apply bg-white rounded-lg shadow-md p-6;
  }
  
  .form-input {
    @apply w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none;
  }
}
```

### 5. Configurar Tasks do Taskipy (Execução via Docker)

⚠️ **IMPORTANTE**: As tasks do Tailwind CSS são executadas **via Docker** para garantir compatibilidade em qualquer ambiente (Windows, Linux, macOS). O Tailwind CSS CLI já está instalado no container Docker.

Adicione as seguintes tasks ao `pyproject.toml`:

```toml
[tool.taskipy.tasks]
# Tasks via Docker - Funcionam em qualquer ambiente
css-build = { cmd = "docker compose exec web tailwindcss -i /code/core/static/core/css/input.css -o /code/core/static/core/css/output.css --minify", help = "Build Tailwind CSS for production via Docker" }
css-watch = { cmd = "docker compose exec web tailwindcss -i /code/core/static/core/css/input.css -o /code/core/static/core/css/output.css --watch", help = "Watch and rebuild Tailwind CSS via Docker" }
css-dev = { cmd = "docker compose exec web tailwindcss -i /code/core/static/core/css/input.css -o /code/core/static/core/css/output.css", help = "Build Tailwind CSS for development via Docker" }
```

**Nota**: Certifique-se de que os containers Docker estão rodando antes de executar as tasks:
```bash
docker compose up -d
```

### 6. Scripts de Build (Opcional - Execução Local)

Se preferir executar o Tailwind CSS localmente (requer baixar o CLI específico para seu sistema operacional), crie os scripts abaixo:

**⚠️ NOTA**: O método recomendado é usar as tasks via Docker configuradas na seção 4.

#### Windows (scripts/build-css.bat) - Execução Local:
```batch
@echo off
echo Building Tailwind CSS...
".\bin\tailwindcss.exe" -i "core\static\core\css\input.css" -o "core\static\core\css\output.css" --minify
if %errorlevel% neq 0 (
    echo Error: Build failed!
    exit /b 1
)
echo Build complete!
```

#### Windows (scripts/watch-css.bat) - Execução Local:
```batch
@echo off
echo Starting Tailwind CSS watcher...
echo Press Ctrl+C to stop
".\bin\tailwindcss.exe" -i "core\static\core\css\input.css" -o "core\static\core\css\output.css" --watch
echo Watcher stopped.
```

#### Linux/macOS (scripts/build-css.sh) - Execução Local:
```bash
#!/bin/bash
# Build Tailwind CSS for production (requer ./bin/tailwindcss)
echo "Building Tailwind CSS..."
./bin/tailwindcss -i ./core/static/core/css/input.css -o ./core/static/core/css/output.css --minify
echo "Build complete!"
```

**Torne o script executável (Linux/macOS):**
```bash
chmod +x scripts/build-css.sh
```

### 7. Criar Templates Django com Tailwind

#### Template Base (templates/base.html):
```html
{% load static %}
{% load django_htmx %}
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}[nome_do_projeto]{% endblock %}</title>
    <link rel="stylesheet" href="{% static 'core/css/output.css' %}">
    <!-- HTMX -->
    <script src="{% static 'core/js/htmx/htmx.min.js' %}" defer></script>  
    {% django_htmx_script %}
    {% block extra_css %}{% endblock %}
</head>
<body class="min-h-screen flex flex-col" hx-headers='{"x-csrftoken": "{{ csrf_token }}"}'>
    <!-- Navigation -->
    <nav class="bg-white shadow-sm">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex justify-between h-16">
                <div class="flex items-center">
                    <a href="{% url 'home' %}" class="text-2xl font-bold text-blue-600">
                        [nome_do_projeto]
                    </a>
                </div>
                <div class="flex items-center space-x-4">
                    {% if user.is_authenticated %}
                        <span class="text-gray-700">Olá, {{ user.username }}</span>
                        <form method="post" action="{% url 'logout' %}" class="inline">
                            {% csrf_token %}
                            <button type="submit" class="btn-secondary">Sair</button>
                        </form>
                    {% else %}
                        <a href="{% url 'login' %}" class="btn-primary">Entrar</a>
                    {% endif %}
                </div>
            </div>
        </div>
    </nav>

    <!-- Main Content -->
    <main class="flex-grow max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full">
        {% block content %}{% endblock %}
    </main>

    <!-- Footer -->
    <footer class="bg-gray-800 text-white py-6 mt-auto">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <p>&copy; 2026 [nome_do_projeto]. Todos os direitos reservados.</p>
        </div>
    </footer>

    {% block extra_js %}{% endblock %}
</body>
</html>
```

#### Template Home (templates/home.html):
```html
{% extends 'base.html' %}

{% block title %}Home - [nome_do_projeto]{% endblock %}

{% block content %}
<div class="text-center py-20">
    <h1 class="text-5xl font-bold text-gray-900 mb-6">
        Bem-vindo ao [nome_do_projeto]
    </h1>
    <p class="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
        Sistema desenvolvido com Django 5.2 e Tailwind CSS v4.
    </p>
    
    <div class="flex justify-center gap-4">
        {% if user.is_authenticated %}
            <a href="{% url 'admin:index' %}" class="btn-primary text-lg">
                Acessar Admin
            </a>
        {% else %}
            <a href="{% url 'login' %}" class="btn-primary text-lg">
                Entrar no Sistema
            </a>
        {% endif %}
    </div>
</div>

<!-- Features Section -->
<div class="grid md:grid-cols-3 gap-8 mt-16">
    <div class="card">
        <div class="text-blue-600 text-4xl mb-4">🚀</div>
        <h3 class="text-xl font-semibold mb-2">Moderno</h3>
        <p class="text-gray-600">Desenvolvido com as mais recentes tecnologias.</p>
    </div>
    
    <div class="card">
        <div class="text-blue-600 text-4xl mb-4">⚡</div>
        <h3 class="text-xl font-semibold mb-2">Rápido</h3>
        <p class="text-gray-600">Performance otimizada com Django e Tailwind.</p>
    </div>
    
    <div class="card">
        <div class="text-blue-600 text-4xl mb-4">🔒</div>
        <h3 class="text-xl font-semibold mb-2">Seguro</h3>
        <p class="text-gray-600">Autenticação e autorização robustas.</p>
    </div>
</div>
{% endblock %}
```

### 8. Criar View para Home

Crie `core/views.py`:

```python
from django.views.generic import TemplateView


class HomeView(TemplateView):
    template_name = 'home.html'
```

### 9. Configurar URLs

Edite `core/urls.py`:

```python
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import HomeView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomeView.as_view(), name='home'),
    path('accounts/', include('django.contrib.auth.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

### 10. Configurar Celery (necessário para Tailwind no Docker)

Crie `core/celery.py`:

```python
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('core')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
```

Edite `core/__init__.py`:

```python
from __future__ import absolute_import, unicode_literals
from .celery import app as celery_app

__all__ = ('celery_app',)
```

### 11. Atualizar Dockerfile para Tailwind CSS

Atualize o `Dockerfile` para incluir o Tailwind CSS CLI e compilar o CSS durante o build:

```dockerfile
# syntax=docker/dockerfile:1
FROM python:3.13-slim

# Variáveis de ambiente para otimizar o comportamento do Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Definir locale
ENV LANG=pt_BR.UTF-8
ENV LANGUAGE=pt_BR:pt
ENV LC_ALL=pt_BR.UTF-8

# Atualiza pacotes do sistema e instala o cliente do PostgreSQL e curl
RUN apt-get update && \
    apt-get install -y --no-install-recommends postgresql-client curl && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Baixar Tailwind CSS CLI v4 para Linux
RUN curl -sLO https://github.com/tailwindlabs/tailwindcss/releases/download/v4.1.18/tailwindcss-linux-x64 && \
    mv tailwindcss-linux-x64 /usr/local/bin/tailwindcss && \
    chmod +x /usr/local/bin/tailwindcss

# Definir diretório de trabalho
WORKDIR /code

# Copiar e instalar dependências do projeto
COPY requirements.txt /code/
RUN pip install -U pip
RUN pip install -r requirements.txt

# Copiar o resto do código da aplicação
COPY . /code/

# Build Tailwind CSS no container
RUN tailwindcss -i /code/core/static/core/css/input.css -o /code/core/static/core/css/output.css --minify
```

⚠️ **IMPORTANTE**: Para versões diferentes do Tailwind CSS, substitua `v4.1.18` pela versão desejada.

### 12. Atualizar .dockerignore

Adicione ao `.dockerignore`:

```dockerignore
# Tailwind CSS
bin/tailwindcss.exe
bin/tailwindcss-macos*
bin/tailwindcss-linux*

# Scripts
scripts/*.bat
```

### 13. Build Inicial do CSS (Via Docker)

Execute o build inicial do CSS usando o container Docker:

#### Usando Taskipy (recomendado - via Docker):
```bash
# Certifique-se que os containers estão rodando
docker compose up -d

# Execute o build
uv run task css-build
```

#### Usando Docker diretamente:
```bash
docker compose exec web tailwindcss -i /code/core/static/core/css/input.css -o /code/core/static/core/css/output.css --minify
```

**Nota**: O CSS também é compilado automaticamente durante o build da imagem Docker (`docker compose up --build`).

### 14. Comandos Úteis do Tailwind CSS (Via Docker)

Todos os comandos são executados através do container Docker, garantindo compatibilidade em qualquer ambiente.

#### Build para Produção (minificado):
```bash
uv run task css-build
```

#### Build para Desenvolvimento (não minificado):
```bash
uv run task css-dev
```

#### Watch Mode (recompila automaticamente):
```bash
uv run task css-watch
```

**Pré-requisito**: Os containers Docker devem estar em execução:
```bash
docker compose up -d
```

### 15. Estrutura Final do Tailwind CSS

Após a configuração, a estrutura de arquivos deve estar assim:

```
[nome_do_projeto]/
├── bin/
│   └── tailwindcss.exe          # CLI Windows (opcional - execução via Docker é recomendada)
├── core/
│   ├── static/
│   │   └── core/
│   │       └── css/
│   │           ├── input.css    # Arquivo fonte com @import "tailwindcss"
│   │           └── output.css   # CSS compilado (gerado pelo build)
│   ├── views.py                 # HomeView
│   ├── urls.py                  # Configuração de URLs
│   ├── celery.py                # Configuração Celery
│   └── __init__.py              # Import do Celery app
├── templates/
│   ├── base.html               # Template base
│   └── home.html               # Template home
├── scripts/                    # Scripts de build (opcional)
│   ├── build-css.bat           # Script build Windows
│   ├── watch-css.bat           # Script watch Windows
│   ├── build-css.sh            # Script build Linux/macOS
│   └── watch-css.sh            # Script watch Linux/macOS
├── pyproject.toml              # Tasks do Taskipy (css-build, css-watch, css-dev)
└── Dockerfile                  # Com build do Tailwind CSS integrado
```

---

## EXECUÇÃO OBRIGATÓRIA DO PROJETO

⚠️ **INSTRUÇÃO CRÍTICA**: O agente de IA DEVE executar TODOS os passos abaixo.
O projeto NÃO está completo até que todas as fases sejam 100% executadas!
O agente DEVE executar estes passos na ORDEM abaixo:

### FASE 1: Configuração (seguir seções 1-9)
- [ ] Inicializar uv
- [ ] Criar ambiente virtual
- [ ] Instalar dependências
- [ ] Criar projeto Django
- [ ] Configurar settings.py
- [ ] Criar app accounts com User customizado
- [ ] Criar arquivos Docker
- [ ] Criar script auxiliar docker-compose-dev.sh
- [ ] Criar docker-compose.devcontainer.yml (OBRIGATÓRIO para devcontainer)
- [ ] Criar .env.example e remover .env do git
- [ ] Configurar Tailwind CSS v4

### FASE 2: Execução Final OBRIGATÓRIA ⚠️

**AMBIENTE HOST NORMAL (Fora do Devcontainer):**
- [ ] Remover db.sqlite3
- [ ] Executar: docker compose up -d --build
- [ ] Executar: docker compose exec web python manage.py migrate
- [ ] Executar: uv run task css-build
- [ ] Verificar: verifique recursivamente no diretório core/static se a task css-build gerou o arquivo output.css
- [ ] Executar: docker compose exec web python manage.py collectstatic --noinput
- [ ] Executar: docker compose exec web python manage.py createsuperuser (username: system, password: system123)
- [ ] Verificar: docker compose exec db psql -U postgres -c "SELECT username FROM accounts_user;"

### FASE 3: Verificação Final OBRIGATÓRIA ⚠️
- [ ] Executar: docker compose logs web (ou ./docker-compose-dev.sh logs web)
- [ ] Executar: docker compose logs db (ou ./docker-compose-dev.sh logs db)
- [ ] Executar: docker compose logs redis (ou ./docker-compose-dev.sh logs redis)
- [ ] Executar: docker compose logs worker (ou ./docker-compose-dev.sh logs worker)
- [ ] Executar: docker compose logs nginx (ou ./docker-compose-dev.sh logs nginx)
- [ ] Executar: curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/
- [ ] Executar: curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/accounts/login/

### FASE 4: Versionamento - commit inicial ⚠️
- [ ] Verificar: .env NÃO está no git (git status)
- [ ] Verificar: .env.example ESTÁ no git (git status)
- [ ] Executar: git add -A && git commit -m "feat: initial commit"

**⚠️ O projeto NÃO está completo até que todas as FASES ATÉ a 4 sejam 100% executadas sem erros!**

**NOTA**: Valide a implementação do projeto executando todos os passos desta seção.

### 1. Criar Diretório Estático
```bash
mkdir -p core/static
mkdir -p staticfiles
```

### 2. Atualizar o arquivo `.env`:
**Remover comentários do trecho comentado no .env:**
```.env
...

# Banco de dados (descomentar para usar PostgreSQL)
DB_ENGINE=postgresql
DB_USERNAME=postgres
DB_PASS=postgres
DB_HOST=db
DB_PORT=5432
DB_NAME=postgres

...

```

### 3. Remover o banco de dados SQLite3:
```bash
rm -f db.sqlite3
```

### 4. Compilar e Iniciar:
```bash
docker compose up -d --build
```

### 5. Executar Migrões
```bash
docker compose exec web python manage.py makemigrations
docker compose exec web python manage.py migrate

# Coletar arquivos estáticos para serem servidos pelo proxy reverso
docker compose exec web python manage.py collectstatic --noinput
```

Acesse http://127.0.0.1:8000 para verificar se o Django está em execução.

### 6. Crie um super usuário
username: system
password: system123

```bash
docker compose exec web python manage.py createsuperuser
```

### 7. Verifique no banco de dados se o usuário "system" foi criado.

### 8. Commit Inicial deve ser executado apenas no fim do projeto.
```bash
git add -A
git commit -m "feat: initial commit."
```

---

## Notas Importantes

### Estrutura do Projeto
```
[nome_do_projeto]/
├── accounts/                    # App de Usuário customizado
│   ├── models.py               # Modelo de Usuário customizado
│   ├── admin.py                # UserAdmin
│   └── migrations/
├── core/                        # Projeto Django
│   ├── settings.py             # Configurações com BD dinâmica
│   ├── urls.py
│   ├── wsgi.py
│   ├── views.py                # HomeView
│   ├── celery.py               # Configuração Celery
│   └── static/                # Arquivos estáticos (inclui Tailwind)
│       └── core/
│           └── css/
│               ├── input.css
│               └── output.css
├── templates/                  # Templates Django
│   ├── base.html
│   └── home.html
├── bin/                        # Binários (Tailwind CSS CLI)
│   └── tailwindcss.exe
├── scripts/                    # Scripts de build
│   ├── build-css.bat
│   ├── watch-css.bat
│   ├── build-css.sh
│   └── watch-css.sh
├── .devcontainer/              # Configuração VS Code Devcontainer (opcional)
│   └── devcontainer.json
├── .vscode/                    # Definições do VSCode
├── data/                       # Dados do PostgreSQL (Docker)
├── media/                      # Uploads de usuários
├── staticfiles/                # Arquivos estáticos coletados
├── .env                        # Variáveis de ambiente (NÃO commitar!)
├── .env.example                # Template de variáveis de ambiente (COMMITAR)
├── .dockerignore               # Arquivo de ignorar do Docker
├── .gitignore                  # Arquivo de ignorar do Git
├── Dockerfile                  # Configuração de imagem Docker (com Tailwind)
├── nginx.conf                  # Configuração do Nginx
├── manage.py                   # CLI do Django
├── uv.lock                     # Arquivo de lock do uv
├── pyproject.toml              # Configuração do uv (com tasks Tailwind)
├── requirements.txt            # Requisitos Python
└── .venv                       # Ambiente virtual
```

**Arquivos OBRIGATÓRIOS:**
- `.env.example` - Template seguro para versionamento (substitui .env no git)

### Ajustes-Chave Realizados

1. **Restrição de Versão Python**: Definido como `>=3.11,<4.0` para evitar problemas de compatibilidade com taskipy
2. **Versão Django**: Usa Django 5.2.12 compatível com Python 3.11+
3. **Configuração de Banco de Dados**: Alternância dinâmica entre SQLite (local) e PostgreSQL (Docker)
4. **CSRF_TRUSTED_ORIGINS**: Corrigido para incluir prefixo de esquema (`http://`, `https://`)
5. **Worker do Celery**: Comando usa `-A core` em vez de `setup` como módulo da aplicação
6. **Internacionalização**: Configurado para Português Brasileiro (pt-br, America/Sao_Paulo)
7. **Tailwind CSS v4**: CLI standalone sem Node.js, compilado automaticamente no Dockerfile
8. **Nginx com Dockerfile**: Configurado para usar `nginx.Dockerfile` com `COPY` em vez de bind mount, garantindo funcionamento em ambos os ambientes (host normal e devcontainer)

### Comandos Docker

#### Compilar e Iniciar:

**Ambiente Normal (Host):**
```bash
docker compose up -d --build
```

#### Executar Migrações no Docker:

**Ambiente Normal:**
```bash
docker compose exec web python manage.py migrate
```

#### Criar Superusuário no Docker:

**Ambiente Normal:**
```bash
docker compose exec web python manage.py createsuperuser
```

#### Ver Logs:

**Ambiente Normal:**
```bash
docker compose logs -f web
```

#### Parar Serviços:

**Ambiente Normal:**
```bash
docker compose stop
```

#### Remover Serviços:

**Ambiente Normal:**
```bash
docker compose down
```

#### Coletar Arquivos Estáticos:

**Ambiente Normal:**
```bash
docker compose exec web python manage.py collectstatic --noinput
```

⚠️ **IMPORTANTE**: Em devcontainers, **sempre use o script auxiliar** `./docker-compose-dev.sh` em vez de `docker compose` direto. O script detecta automaticamente o ambiente e aplica o override correto.

### Comandos Tailwind CSS

#### Build para Produção:
```bash
uv run task css-build
```

#### Build para Desenvolvimento:
```bash
uv run task css-dev
```

#### Watch Mode:
```bash
uv run task css-watch
```

### Fluxo de Desenvolvimento

1. **Adicionar Dependências**:
   ```bash
   uv add nome-do-pacote
   uv lock
   uv export --format requirements.txt --output requirements.txt --without-hashes
   ```

2. **Criar Apps**:
   ```bash
   uv run python manage.py startapp nomeapp
   # Adicione a INSTALLED_APPS em core/settings.py
   ```

3. **Atualizar CSS (Tailwind)**:
   ```bash
   uv run task css-watch  # Durante desenvolvimento
   uv run task css-build  # Para produção

   docker compose exec web python manage.py collectstatic --noinput  # Coleta arquivos estáticos
   ```

4. **Executar Testes**:
   ```bash
   pytest
   ```

5. **Qualidade de Código**:
   ```bash
   ruff check .
   ruff format .
   ```

---

## ⚠️ FLUXO OBRIGATÓRIO: Adicionar Dependências Python {#fluxo-obrigatório-adicionar-dependências-python}

**ATENÇÃO**: Esta seção é CRÍTICA. Erros na gestão de dependências causam falhas graves na aplicação.

### Ordem OBRIGATÓRIA de Operações

❌ **NUNCA faça isso**:
```bash
# ERRADO - Adicionar manualmente ao requirements.txt
echo "django-lib==1.0.0" >> requirements.txt

# ERRADO - Instalar apenas no venv local sem usar uv
pip install django-lib
```

✅ **SEMPRE faça isso**:
```bash
# PASSO 1: Adicionar via uv (atualiza pyproject.toml e uv.lock)
uv add "django-lib>=1.0.0"

# PASSO 2: Gerar lockfile e exportar para requirements.txt
uv lock
uv export --format requirements.txt --output requirements.txt --without-hashes

# PASSO 3: Rebuild containers Docker (CRÍTICO!)
docker compose up -d --build

# PASSO 4: Reiniciar nginx (necessário após rebuild do web)
docker compose restart nginx

# PASSO 5: Verificar logs
docker compose logs web --tail 50
docker compose logs worker --tail 50

# PASSO 6: Testar endpoints
curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/
```

### Por que essa ordem é CRÍTICA?

1. **pyproject.toml é a fonte da verdade**: Define as dependências do projeto
2. **uv.lock garante reprodutibilidade**: Lock exato das versões instaladas
3. **requirements.txt é um EXPORT**: Gerado automaticamente do pyproject.toml
4. **Docker usa requirements.txt no BUILD**: Alterações só surtem efeito com rebuild

### Erros Comuns e Soluções

#### Erro 1: "ModuleNotFoundError" no Docker

**Causa**: Biblioteca está no `requirements.txt` mas NÃO no `pyproject.toml`

**Solução**:
```bash
# Adicionar via uv
uv add "nome-lib>=versao"

# Reexportar requirements.txt
uv lock
uv export --format requirements.txt --output requirements.txt --without-hashes

# Rebuild Docker
docker compose up -d --build
```

#### Erro 2: Biblioteca funciona localmente mas não no Docker

**Causa**: `requirements.txt` não foi atualizado ou Docker não foi rebuildado

**Solução**:
```bash
# Verificar se requirements.txt contém a biblioteca
grep nome-lib requirements.txt

# Se não contiver, exportar novamente
uv lock
uv export --format requirements.txt --output requirements.txt --without-hashes

# Rebuild obrigatório
docker compose up -d --build
```

#### Erro 3: Nginx retorna HTTP 502 após rebuild

**Causa**: Nginx mantém cache de conexão para IP antigo do container web

**Solução**:
```bash
docker compose restart nginx
```

### Checklist para Adicionar Dependências

Use este checklist SEMPRE:

- [ ] **OBRIGATÓRIO**: Adicionar via `uv add "nome-lib>=versao"`
- [ ] **OBRIGATÓRIO**: Verificar se `pyproject.toml` foi atualizado
- [ ] **OBRIGATÓRIO**: Gerar lockfile via `uv lock`
- [ ] **OBRIGATÓRIO**: Exportar via `uv export --format requirements.txt --output requirements.txt --without-hashes`
- [ ] **OBRIGATÓRIO**: Verificar se `requirements.txt` contém a nova lib
- [ ] **OBRIGATÓRIO**: `docker compose up -d --build`
- [ ] **OBRIGATÓRIO**: `docker compose restart nginx`
- [ ] **OBRIGATÓRIO**: Verificar logs `docker compose logs web --tail 50`
- [ ] **OBRIGATÓRIO**: Testar endpoints `curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/`
- [ ] **OBRIGATÓRIO**: Executar check `docker compose exec web python manage.py check`

---

### Melhores Práticas

1. ✅ SEMPRE use uv para gerenciamento de dependências
2. ✅ **JAMAIS edite requirements.txt manualmente** - é um export do pyproject.toml
3. ✅ **JAMAIS instale libs com pip install** - sempre use `uv add`
4. ✅ **SEMPRE rebuild do Docker após mudar requirements.txt** (`docker compose up -d --build`)
5. ✅ **SEMPRE reinicie nginx após rebuild do web** (`docker compose restart nginx`)
6. ✅ **NUNCA faça commit de arquivos sensíveis** (.env, db.sqlite3)
7. ✅ **SEMPRE use .env.example no git, nunca .env**
8. ✅ Teste localmente antes de fazer commit
9. ✅ Siga convenções de mensagem de commit: `feat:`, `fix:`, `refactor:`
10. ✅ Use `.venv` criado pelo uv na raiz do projeto
11. ✅ NUNCA mude `AUTH_USER_MODEL` após as migrações serem criadas
12. ✅ Execute `uv run task css-build` (via Docker) antes de fazer commit de mudanças no CSS
13. ✅ Use `uv run task css-watch` (via Docker) durante desenvolvimento para auto-reload
14. ✅ Realize o commit inicial apenas a conclusão de toda implementação, execução e testes
15. ✅ **Use o checklist de dependências** sempre que adicionar novas bibliotecas
17. ✅ **NUNCA faça commit de .env** - use `.env.example` como template
18. ✅ **Verifique se .env está no .gitignore** antes de fazer commit

### Sinais de Alerta - Quando Algo Está Errado

⚠️ **Atenção se:**
- Container `web` ou `worker` fica reiniciando constantemente
- `docker compose logs web` mostra `ModuleNotFoundError`
- Nginx retorna HTTP 502 mas o web responde na porta 8000
- Adicionou biblioteca ao projeto mas `requirements.txt` não foi atualizado

**Ação imediata:**
```bash
# Verificar se pyproject.toml e requirements.txt estão sincronizados
uv sync

# Reexportar requirements.txt
uv lock
uv export --format requirements.txt --output requirements.txt --without-hashes

# Rebuild tudo
docker compose up -d --build
docker compose restart nginx
```

---

## ✅ Validação da Aplicação {#validação-da-aplicação}

Após seguir todos os passos deste guia, valide que a aplicação está funcionando corretamente:

### Validação Básica

```bash
# Verificar containers rodando
docker compose ps

# Todos os containers devem estar "Up"
# - db (PostgreSQL)
# - web (Django)
# - nginx (Proxy reverso)
# - redis
# - worker (Celery)
```

### Validação do Django

```bash
# Verificar configuração
docker compose exec web python manage.py check
# Saída esperada: "System check identified no issues"

# Verificar migrações
docker compose exec web python manage.py showmigrations
# Todas as migrações devem estar marcadas com [X]

# Verificar arquivos estáticos
docker compose exec web ls -la /code/staticfiles/core/css/output.css
# Saída esperada: arquivo output.css presente
```

### Validação do Nginx

```bash
# Testar de dentro do container nginx
docker compose exec nginx curl -s -o /dev/null -w "%{http_code}\n" http://localhost/
# Saída esperada: 200

# Verificar logs do nginx
docker compose logs nginx --tail 20
# Saída esperada: "Configuration complete; ready for start up"
```

### Validação de Acesso

**De dentro do devcontainer**:
```bash
# Testar acesso via nginx
docker compose exec nginx curl -s http://localhost/ | head -20
# Saída esperada: HTML completo com Tailwind CSS
```

**De fora do devcontainer (host físico)**:
```bash
# Testar acesso direto ao web (sem nginx)
curl -s http://localhost:8000/ | head -20

# Testar acesso via nginx
curl -s http://localhost:8080/ | head -20
```

### Validação do Superuser

```bash
# Criar superuser (se ainda não existe)
docker compose exec web python manage.py createsuperuser

# Verificar no banco
docker compose exec db psql -U postgres -c "SELECT username, is_superuser FROM accounts_user;"
# Saída esperada: username=system, is_superuser=t
```

### Solução de Problemas

**Erro: "relation django_session does not exist"**
```bash
# As migrações não foram aplicadas. Execute:
docker compose exec web python manage.py migrate
```

**Erro: nginx não inicia**
```bash
# Verificar logs
docker compose logs nginx

# Rebuild nginx
docker compose up -d --build nginx
```

**Erro: Porta 8080 ou 8000 já em uso**
```bash
# Verificar o que está usando as portas
sudo lsof -i :8080
sudo lsof -i :8000

# Parar o serviço que está usando a porta ou mudar as portas no docker-compose.yml
```

---

## Referências

- [Documentação do Django](https://docs.djangoproject.com/en/5.2/)
- [Documentação do uv](https://docs.astral.sh/uv/)
- [Documentação do Docker Compose](https://docs.docker.com/compose/)
- [Documentação do Celery](https://docs.celeryproject.org/)
- [Modelo de Usuário Customizado](https://docs.djangoproject.com/en/5.2/topics/auth/customizing/)
- [Tailwind CSS v4 Standalone CLI](https://tailwindcss.com/docs/installation/tailwind-cli)

---

**Última Atualização**: 2026-03-14
**Versão do Projeto**: 0.1.17
**Versão Django**: 5.2.12
**Estado**: Versão ainda não testada.
