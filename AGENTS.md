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

| URL | View (CBV) | Template | Tipo |
|-----|-----------|----------|------|
| `/hyperview/` | `IndexView` | `hv/index.xml` | Página |
| `/hyperview/home/` | `HomeView` | `hv/home.xml` | Página |
| `/hyperview/list/` | `ListView` | `hv/list.xml` | Página |
| `/hyperview/list/items/` | `ListItemsView` | `hv/list_items.xml` | **Fragmento** |
| `/hyperview/detail/<id>/` | `DetailView` | `hv/detail.xml` | Página |
| `/hyperview/form/` | `FormView` (GET+POST) | `hv/form.xml` | Página |
| `/hyperview/login/` | `LoginView` (GET+POST) | `hv/login.xml` | Página |
| `/hyperview/profile/` | `ProfileView` | `hv/profile.xml` | Página |
| `/hyperview/settings/` | `SettingsView` | `hv/settings.xml` | Página |
| `/hyperview/about/` | `AboutView` | `hv/about.xml` | Página |

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
├── hv/                    # App Hyperview (1 app, 10 views, 13 templates)
│   ├── urls.py            # app_name = "hv", urlpatterns com CBVs
│   ├── views.py           # TemplateView + View com get()/post()
│   └── tests.py           # 11 testes com reverse()
├── accounts/              # User customizado (AbstractUser)
├── templates/
│   ├── base.html          # Template base web (Tailwind + HTMX)
│   ├── home.html          # Home page web
│   └── hv/                # Templates HXML
│       ├── base.xml       # Base: <doc>, <screen>, header, tab_bar, loading screens
│       ├── index.xml      # Navigator: stack → tab navigator com 3 rotas
│       ├── home.xml       # Dashboard
│       ├── list.xml       # Lista com pull-to-refresh + infinite scroll
│       ├── list_items.xml # Fragmento de <item> soltos (infinite scroll)
│       ├── detail.xml     # Detalhes com ações
│       ├── form.xml       # Formulário com validação server-side
│       ├── login.xml      # Login
│       ├── profile.xml    # Perfil
│       ├── settings.xml   # Configurações
│       ├── about.xml      # Sobre
│       └── includes/
│           ├── header.xml         # Header com botão voltar condicional
│           ├── header_styles.xml  # Estilos do header
│           ├── tabbar.xml         # Bottom tab bar (custom element)
│           ├── tabbar_styles.xml  # Estilos do tab bar
│           ├── loading_pushed.xml # Loading screen para navegação push
│           ├── loading_modal.xml  # Loading screen para modal
│           └── loading_reload.xml # Loading screen para reload
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

## Lições aprendidas — Hyperview

### HXML: regras de ouro

1. **`<list>` é FlatList (VirtualizedList)** — nunca pode ficar dentro de ScrollView. Se a tela
   tem `<list>`, o `<body>` deve ter `scroll="false"` e nenhum ancestral com scroll.
2. **`<body scroll="false">` é obrigatório em telas com `<list>`** — sem isso o Hyperview
   renderiza o body como ScrollView, e FlatList dentro de ScrollView = erro do React Native.
3. **Elementos com `href` recebem um wrapper tappable** — estilos de layout (como `flex="1"`)
   devem ir no wrapper via `href-style`, não no elemento via `style`.
4. **Tab bar não é automática** — precisa ser incluída manualmente em cada tela de tab via
   `<navigation:bottom-tab-bar navigation:navigator="main-tab-navigator">`. É um custom element
   registrado no demo app (`BottomTabBar`).
5. **`navigation:route="tab-home"` não é URL** — é o ID do `<nav-route>` no `index.xml`.
   O React Navigation usa esse ID para casar com a rota registrada. Quem faz o HTTP request
   é o `href` da `<nav-route>`, não o tab bar.
6. **Estilos vivem em `<styles>` dentro de `<screen>`** — não podem ficar soltos no `<body>`.
7. **Namespaces obrigatórios** no `<doc>`: `xmlns`, `xmlns:navigation`, `xmlns:safe-area`.

### Infinite scroll — padrão correto

**Docs:**
- https://hyperview.org/docs/example_infinite_scroll
- https://hyperview.org/docs/reference_index
- https://github.com/instawork/hyperview

O infinite scroll usa **dois endpoints**:

| Endpoint | View | O que retorna |
|----------|------|---------------|
| `GET /hyperview/list/` | `ListView` | `<doc><screen>...<list>...</list></screen></doc>` (página cheia) |
| `GET /hyperview/list/items/?page=N` | `ListItemsView` | `<items xmlns="..."><item>...</item></items>` (fragmento com wrapper) |

**Como funciona:**
1. `ListView` renderiza a `<list>` completa com a primeira página de itens
2. No final da lista, um `<item>` sentinela com `trigger="visible" once="true" action="replace"`
   dispara request para `ListItemsView` quando fica visível
3. `ListItemsView` retorna `<items xmlns="https://hyperview.org/hyperview">` contendo os novos `<item>` + novo sentinela
4. `action="replace"` substitui o sentinela pelos novos itens, preservando os existentes

**Por que `<items>` como wrapper?** XML exige um único elemento raiz. O Hyperview usa `<items>` como
container invisível — o `<list>` renderiza apenas os filhos `<item>`, ignorando o wrapper.

**Sentinela:**
```xml
<item key="load-more" id="load-more-spinner" trigger="visible" once="true"
      action="replace" href="{{ base_url }}/hyperview/list/items/?page={{ next_page }}"
      style="load-more-btn">
  <spinner />
</item>
```

**Resposta do endpoint (list_items.xml):**
```xml
<items xmlns="https://hyperview.org/hyperview">
  <item key="21" style="Item">
    <text style="Item__Label">Added: Item 21</text>
  </item>
  <!-- mais itens... -->
  <item key="load-more" id="load-more-spinner" trigger="visible" once="true"
        action="replace" href="/hyperview/list/items/?page=3" style="load-more-btn">
    <spinner />
  </item>
</items>
```

**Fim da lista (última página):** omitir o sentinela da resposta para não disparar mais requests.

**⚠️ Keys únicas com grouped items:** Ao usar `{% regroup %}` com infinite scroll, headers de categoria
se repetem em páginas diferentes. Prefixar keys com a página para evitar duplicatas:

```xml
<!-- list.xml (página 1) -->
<item key="header-p1-{{ grupo.grouper|default:"geral" }}" style="list-header">

<!-- list_items.xml (páginas seguintes) -->
<item key="header-p{{ page }}-{{ grupo.grouper|default:"geral" }}" style="list-header">
```

Sem o prefixo da página, React Native reclama: "Encountered two children with the same key".

### Pull-to-refresh

```xml
<list id="main-list">
  <behavior trigger="refresh" action="replace"
            href="{{ base_url }}/hyperview/list/?page=1" target="main-list" />
  ...
</list>
```

`action="replace"` com `target="main-list"` substitui a lista inteira pelo retorno do endpoint.
Aqui pode usar a mesma URL da ListView porque o Hyperview extrai os `<item>` do resultado.

### Template base.xml — blocos disponíveis

```xml
<doc>
  <screen>
    <styles>{% block styles %}{% endblock %}</styles>
    <body style="body" scroll="false">
      <safe-area:safe-area-view> {% include header %} </safe-area:safe-area-view>
      <view style="content-area"> {% block container %}{% endblock %} </view>
      {% block tab_bar %}{% endblock %}
    </body>
  </screen>
  {% include loading_pushed %}
  {% include loading_modal %}
  {% include loading_reload %}
</doc>
```

| Bloco | Uso |
|-------|-----|
| `styles` | Estilos da tela (obrigatório) |
| `container` | Conteúdo principal abaixo do header |
| `tab_bar` | Tab bar (incluir nas telas de tab: home, list, profile) |
| `custom_screen` | Telas extras no `<doc>` |

### Header — botão voltar condicional

O header (`includes/header.xml`) usa duas variáveis de contexto:

| Variável | Efeito |
|----------|--------|
| `show_back: True` | Exibe botão "‹ Voltar" em vez do título |
| `back_href: "#tab-home"` | Se presente, usa `action="navigate"` (volta pra tab). Se ausente, usa `action="back"` (volta na pilha push) |

**Quem recebe o quê:**

| View | `show_back` | `back_href` | Comportamento |
|------|-------------|-------------|---------------|
| `ListView` | `True` | `"#tab-home"` | Navigate → tab home |
| `DetailView` | `True` | — | Back → volta na pilha |
| `FormView` | `True` | — | Back → volta na pilha |
| `LoginView` | `True` | — | Back → volta na pilha |
| `SettingsView` | `True` | — | Back → volta na pilha |
| `AboutView` | `True` | — | Back → volta na pilha |
| `HomeView` | — | — | Sem botão, mostra título |
| `ProfileView` | — | — | Sem botão, mostra título |

### `regroup` exige lista pré-ordenada

A tag `{% regroup items by category as grouped_items %}` agrupa itens por categoria.
**Requer** que a lista esteja ordenada pelo campo de agrupamento (`category`). Sem ordenação
prévia, cada mudança de categoria cria um novo grupo → chaves duplicadas no React Native.

```python
items.sort(key=lambda x: (x["category"], x["id"]))  # antes do regroup no template
```

### Includes: dois arquivos (styles + markup)

Django não suporta blocos dentro de `{% include %}` (ticket #6646, wontfix). Por isso cada
componente incluído tem **dois arquivos**:

```
includes/
├── header.xml          # markup do header
├── header_styles.xml   # <style> do header (incluído no bloco styles do base.xml)
├── tabbar.xml          # markup do tab bar
├── tabbar_styles.xml   # <style> do tab bar
├── loading_pushed.xml  # loading screen para push
├── loading_modal.xml   # loading screen para modal
└── loading_reload.xml  # loading screen para reload
```

O `base.xml` inclui os `_styles.xml` dentro de `<styles>` e os `.xml` dentro de `<body>`.

### Telas com scroll vs telas com `<list>`

| Tipo de tela | Scroll |
|-------------|--------|
| Home, Profile, Detail, Form, Settings, About | Adicionam `<view scroll="true" flex="1">` dentro de `{% block container %}` |
| List | **NÃO adicionam scroll** — o `<list>` já é VirtualizedList (scroll próprio) |
| Login | Não precisa de scroll (conteúdo fixo) |

O `base.xml` tem `scroll="false"` no `<body>`. Cada tela controla seu próprio scroll.

### Docker + WSL: edição de arquivos

Arquivos em `/mnt/c/...` montados no container podem ter permissões restritas.
Se `edit` falhar, usar:
```bash
docker compose exec -T web python3 -c "
with open('/code/templates/hv/file.xml', 'r') as f:
    content = f.read()
content = content.replace('old', 'new')
with open('/code/templates/hv/file.xml', 'w') as f:
    f.write(content)
"
```

Templates `.xml` em `templates/hv/` geralmente podem ser editados diretamente.
Arquivos `.py` em `hv/` às vezes precisam do Docker exec.
## AI Context References
- Documentation index: `.context/docs/README.md`
- Agent playbooks: `.context/agents/README.md`
