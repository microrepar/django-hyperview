# AGENTS.md — Contexto do Projeto para Agentes de IA

## Stack

| Camada | Tecnologia | Versão |
|--------|-----------|--------|
| Backend | Django | 5.2.x |
| Python | CPython | 3.13 |
| Banco | PostgreSQL (Docker) / SQLite (local) | 15 |
| Cache / Filas | Redis + Celery | 6.2 / 5.x |
| Proxy | Nginx | latest |
| Frontend Web | Tailwind CSS v4 (standalone CLI) + HTMX 2.x | — |
| Mobile | Hyperview (HXML servido pelo Django) | 0.105 |
| Dependências | uv | — |
| Containers | Docker Compose | — |

## Arquitetura

```
┌─────────────────────────────────────────────────────────┐
│  Docker Compose                                         │
│  ┌──────────┐  ┌──────────┐  ┌───────┐  ┌──────┐ ┌────┐│
│  │ nginx    │  │ web      │  │ db    │  │redis │ │wkr ││
│  │ :8080    │  │ :8000    │  │ :5432 │  │      │ │    ││
│  └──────────┘  └──────────┘  └───────┘  └──────┘ └────┘│
└─────────────────────────────────────────────────────────┘
         │
         │ HXML (application/xml)
         ▼
┌─────────────────┐
│ Hyperview Client │  App mobile React Native (Expo)
│ (demo/app)      │  Busca HXML do Django e renderiza
└─────────────────┘  telas nativas iOS/Android
```

## Hyperview — como funciona

O Django **não** serve HTML para o mobile. Serve **HXML** (Hyperview XML), um
formato que descreve telas mobile nativas (listas, formulários, navegação).

Fluxo:
1. App mobile faz `GET /hyperview/` → Django retorna XML com `<navigator>` e tabs
2. Cada tab (`/hyperview/home/`, `/hyperview/list/`, etc) retorna XML com `<screen>`
3. Toques/interações disparam `<behavior>` elements que fazem novas requests HTTP
4. Django processa (valida formulário, busca dados) e retorna novo XML
5. Hyperview Client renderiza o XML como tela nativa no dispositivo

### Endpoints HXML (app `hv`)

| URL | View (CBV) | Template |
|-----|-----------|----------|
| `/hyperview/` | `IndexView` | `hv/index.xml` |
| `/hyperview/home/` | `HomeView` | `hv/home.xml` |
| `/hyperview/list/` | `ListView` | `hv/list.xml` |
| `/hyperview/detail/<id>/` | `DetailView` | `hv/detail.xml` |
| `/hyperview/form/` | `FormView` (GET+POST) | `hv/form.xml` |
| `/hyperview/login/` | `LoginView` (GET+POST) | `hv/login.xml` |
| `/hyperview/profile/` | `ProfileView` | `hv/profile.xml` |
| `/hyperview/settings/` | `SettingsView` | `hv/settings.xml` |
| `/hyperview/about/` | `AboutView` | `hv/about.xml` |

### URLs: `core/urls.py` → `include("hv.urls")` com `app_name = "hv"`

### CSRF: `FormView` e `LoginView` usam `@method_decorator(csrf_exempt, name="dispatch")`
Correto para APIs mobile que não usam cookie de sessão (doc Django recomenda).

### Templates: `templates/hv/` (segue convenção Django: nome do diretório = nome do app)

## Estrutura de diretórios relevantes

```
django-hyperview/
├── core/                  # Config Django (settings, urls, celery, wsgi)
│   ├── urls.py            # include("hv.urls") para /hyperview/
│   ├── settings.py        # INSTALLED_APPS + "hv"
│   └── base_models/       # Mixins: TimestampMixin, SoftDeleteMixin, BaseModel
├── hv/                    # App Hyperview (1 app, 9 views, 12 templates)
│   ├── urls.py            # app_name = "hv", urlpatterns com CBVs
│   ├── views.py           # TemplateView + View com get()/post()
│   └── tests.py           # 11 testes com reverse()
├── accounts/              # User customizado (AbstractUser)
├── templates/
│   ├── base.html          # Template base web (Tailwind + HTMX)
│   ├── home.html          # Home page web
│   └── hv/                # Templates HXML (12 arquivos)
│       ├── base.xml       # Base com <doc>, loading screens
│       ├── index.xml      # Navigator tabs
│       ├── home.xml       # Dashboard
│       ├── list.xml       # Lista + pull-to-refresh + infinite scroll
│       ├── detail.xml     # Detalhes com ações
│       ├── form.xml       # Formulário com validação server-side
│       ├── login.xml      # Login
│       ├── profile.xml    # Perfil
│       ├── settings.xml   # Configurações
│       ├── about.xml      # Sobre
│       └── includes/
│           ├── header.xml # Header reutilizável
│           └── styles.xml # Estilos globais HXML
├── staticfiles/           # collectstatic output
├── media/                 # Uploads
├── docker-compose.yml     # db, web, nginx, redis, worker
├── Dockerfile             # Python 3.13 + Tailwind CSS CLI
├── nginx.conf             # proxy_pass → web:8000
├── pyproject.toml         # uv + taskipy (css-build, css-watch, css-dev)
└── requirements.txt       # Exportado do uv
```

## Comandos essenciais

```bash
# Subir tudo
docker compose up -d --build

# Ver logs
docker compose logs -f web

# Django check
docker compose exec web python manage.py check

# Testes Hyperview
docker compose exec web python manage.py test hv

# CSS Tailwind
docker compose exec web tailwindcss -i /code/core/static/core/css/input.css -o /code/core/static/core/css/output.css --minify

# Dependências (sempre usar uv, NUNCA editar requirements.txt direto)
uv add "pacote>=versao"
uv lock
uv export --format requirements.txt --output requirements.txt --without-hashes
docker compose up -d --build
```

## Mobile — Demo Hyperview

O cliente mobile é o **demo oficial do Hyperview** em `/mnt/c/workspaces/PythonProjects/hyperview/demo/`.

Para apontar pro Django, duas linhas foram alteradas no demo:

1. `App.tsx` — entrypointUrl trocado de `/hyperview/public/index.xml` para `/hyperview/`
2. `app.config.ts` — baseUrl usa `BASE_URL` env var

Build do APK:
```bash
cd /mnt/c/workspaces/PythonProjects/hyperview/demo
eas login
BASE_URL="https://SEU_DOMINIO" eas build --platform android --profile preview
```

Dev local (sem build, usa Expo Go no celular):
```bash
cd /mnt/c/workspaces/PythonProjects/hyperview/demo
yarn install
BASE_URL="http://192.168.1.100:8000" yarn start
```

## Regras

- **SEMPRE** usar `docker compose exec` para comandos Django (migrate, test, shell)
- **SEMPRE** usar `uv add` para dependências, nunca editar requirements.txt
- **NUNCA** commitar `.env`
- Templates HXML retornam `content_type='application/xml'`
- Views com POST usam `@method_decorator(csrf_exempt, name="dispatch")`
- URLs usam `reverse("hv:nome")` nos testes, nunca hardcoded
