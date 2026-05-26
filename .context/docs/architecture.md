---
type: doc
name: architecture
description: System architecture, layers, patterns, and design decisions
category: architecture
generated: 2026-05-25
status: filled
scaffoldVersion: "2.0.0"
---

## Architecture Notes

This is a **Django monolith** serving dual frontends: a traditional web UI (Tailwind CSS + HTMX)
and a server-driven mobile app via **Hyperview HXML**. Both frontends consume the same Django
backend, but through different rendering pipelines — HTML templates for web, XML templates for mobile.

The architecture follows Django conventions: URL routing → Views (CBVs) → Templates → Response.
There are no REST APIs or DRF serializers — all data is rendered server-side into hypermedia
(HXML for mobile, HTML for web). The Hyperview client renders native mobile screens directly
from the XML responses.

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│  Docker Compose                                         │
│  ┌──────────┐  ┌──────────┐  ┌───────┐  ┌──────┐ ┌────┐│
│  │ nginx    │  │ web      │  │ db    │  │redis │ │wkr ││
│  │ :8080    │  │ :8000    │  │ :5432 │  │      │ │    ││
│  └──────────┘  └──────────┘  └───────┘  └──────┘ └────┘│
└─────────────────────────────────────────────────────────┘
         │                         │
         │ HXML (application/xml)  │ HTML (text/html)
         ▼                         ▼
┌─────────────────┐    ┌──────────────────┐
│ Hyperview Client │    │ Web Browser      │
│ (React Native)   │    │ (Tailwind+HTMX)  │
└─────────────────┘    └──────────────────┘
```

- **Monolithic deployment**: Single Django process serves both web and mobile.
- **Nginx reverse proxy**: Routes `:8080 → web:8000`, serves static/media files.
- **PostgreSQL in Docker**: Production database; SQLite for local dev.
- **Redis + Celery**: Async task queue for background jobs.
- **Docker Compose**: All services (web, db, nginx, redis, worker) orchestrated together.

Request flow for mobile: `App → GET /hyperview/ → Django returns XML → Hyperview Client renders native UI`.
Subsequent interactions (taps, form submits) dispatch `<behavior>` elements that fire new HTTP
requests, and Django responds with new XML fragments or full screens.

## Architectural Layers

| Layer | Purpose | Key Directories |
|-------|---------|----------------|
| **Routing** | URL → View mapping | `core/urls.py`, `hv/urls.py` |
| **Views (CBVs)** | Request handling, context building | `hv/views.py` (13 CBVs), `core/views.py` |
| **Templates** | XML/HTML rendering | `templates/hv/` (13 XML templates), `templates/` (web HTML) |
| **Models** | Data layer with mixins | `core/base_models/`, `accounts/models.py` |
| **Config** | Django settings, Celery, WSGI | `core/settings.py`, `core/celery.py` |
| **Infrastructure** | Docker, Nginx, env vars | `docker-compose.yml`, `Dockerfile`, `nginx.conf` |

## Detected Design Patterns

| Pattern | Confidence | Locations | Description |
|---------|------------|-----------|-------------|
| TemplateView (CBV) | 100% | `hv/views.py:34-260` | Read-only views extending `TemplateView` |
| View with GET+POST | 100% | `hv/views.py:166,217,302,328,367` | Forms using `View` class with `get()`/`post()` |
| csrf_exempt decorator | 100% | `hv/views.py` (5 views) | POST endpoints exempt from CSRF (API pattern) |
| Mixin-based model inheritance | 100% | `core/base_models/mixins.py` | `TimestampMixin`, `SoftDeleteMixin`, `BaseModel` |
| Hypermedia (HATEOAS) | 100% | All HXML templates | Navigation via `<behavior href="...">` hyperlinks |
| Fragment endpoint | 100% | `hv/views.py:100` (`ListItemsView`) | Partial responses for infinite scroll |
| Base URL helper | 100% | `hv/views.py:27` (`_base_url()`) | Configurable base URL for HXML hrefs |

## Entry Points

- **Web**: `/` → `core/views.py:HomeView` (HTML)
- **Mobile entrypoint**: `/hyperview/` → `hv/views.py:IndexView` (XML navigator)
- **Django Admin**: `/admin/`
- **Static files**: `/static/`, `/media/` (via Nginx in production)
- **Docker**: `docker compose up -d --build`

## Public API

| Symbol | Type | Location |
|--------|------|----------|
| `IndexView` | TemplateView | `hv/views.py:34` |
| `HomeView` | TemplateView | `hv/views.py:43` |
| `ListView` | TemplateView | `hv/views.py:65` |
| `ListItemsView` | TemplateView | `hv/views.py:100` |
| `DetailView` | TemplateView | `hv/views.py:134` |
| `FormView` | View (GET+POST) | `hv/views.py:166` |
| `LoginView` | View (GET+POST) | `hv/views.py:217` |
| `ProfileView` | TemplateView | `hv/views.py:237` |
| `SettingsView` | TemplateView | `hv/views.py:251` |
| `AboutView` | TemplateView | `hv/views.py:260` |
| `ShareView` | TemplateView | `hv/views.py:276` |
| `DeleteView` | View (GET+POST) | `hv/views.py:302` |
| `ProfileEditView` | View (GET+POST) | `hv/views.py:328` |
| `LogoutView` | View (GET+POST) | `hv/views.py:367` |
| `TimestampMixin` | Mixin | `core/base_models/mixins.py:4` |
| `SoftDeleteMixin` | Mixin | `core/base_models/mixins.py:13` |
| `BaseModel` | Model | `core/base_models/models.py:6` |
| `User` | Model | `accounts/models.py:4` |

## Internal System Boundaries

- **`hv/` app**: All Hyperview/HXML logic — views, URLs, templates. Self-contained.
- **`accounts/` app**: Custom User model (`AbstractUser`), admin, migrations.
- **`core/` app**: Django configuration, base models/mixins, root URL routing, Celery config.
- **`templates/hv/`**: HXML templates separate from web HTML templates. Follow Django convention
  of `templates/<app_name>/` directory naming.
- **`templates/hv/includes/`**: Reusable HXML components (header, tab bar, loading screens).
  Each component has two files: `_styles.xml` (styles) and `.xml` (markup) due to Django's
  inability to have blocks inside `{% include %}`.

## External Service Dependencies

| Service | Purpose | Integration |
|---------|---------|-------------|
| PostgreSQL 15 | Primary database | Docker container, `docker-compose.yml` |
| Redis 6.2 | Celery broker + cache | Docker container |
| Nginx | Reverse proxy + static files | Docker container, `nginx.conf` |
| i.pravatar.cc | Avatar placeholder images | External HTTP (no auth) |

## Key Decisions & Trade-offs

1. **HXML over JSON API**: Chose Hyperview hypermedia approach — the mobile client is "thin"
   and all UI logic lives on the server. Trade-off: no offline support, but zero mobile deploys.
2. **csrf_exempt for mobile POST**: Django's CSRF protection requires cookies, which mobile
   apps don't use. Views that receive POST from mobile are exempted per Django docs
   recommendation for API endpoints.
3. **Dual template rendering**: Same Django backend serves `text/html` (web) and
   `application/xml` (mobile). No DRF layer — simpler but means separate template sets.
4. **SQLite for local dev**: `DB_ENGINE` env var switches between SQLite and PostgreSQL.
   Faster local setup without Docker dependency.
5. **uv for dependency management**: Replaces pip. Always use `uv add`/`uv lock`/`uv export`
   — never edit `requirements.txt` directly.

## Diagrams

```mermaid
graph TD
    A[Mobile App] -->|GET /hyperview/| B[Nginx :8080]
    C[Web Browser] -->|GET /| B
    B -->|proxy_pass| D[Django :8000]
    D --> E[URL Router core/urls.py]
    E --> F[/hyperview/ → hv/urls.py]
    E --> G[/ → core/views.py]
    F --> H[HXML Templates]
    G --> I[HTML Templates]
    D --> J[(PostgreSQL)]
    D --> K[Redis]
    K --> L[Celery Worker]
```

## Risks & Constraints

- **No offline support**: Hyperview requires network connectivity for all interactions.
- **Server-driven latency**: Every mobile interaction incurs an HTTP round-trip.
- **Single point of failure**: Monolithic Django process; no horizontal scaling.
- **Template complexity**: Maintaining two parallel template sets (HTML + HXML) for the same
  logical views could diverge.
- **Docker+WSL file permissions**: Files on `/mnt/c/...` mounted in containers may have
  restricted permissions; use `docker compose exec` for Python file edits.

## Top Directories Snapshot

| Directory | Files | Purpose |
|-----------|-------|---------|
| `hv/` | ~5 | Hyperview app (views, urls, tests, apps, models) |
| `core/` | ~10 | Django config, base models, Celery, WSGI |
| `accounts/` | ~6 | Custom User model, admin, migrations |
| `templates/hv/` | ~13 | HXML templates + includes |
| `templates/` | ~3 | Web HTML templates |
| `staticfiles/` | ~50+ | Collected static assets |
| `.context/` | ~31 | AI context scaffolding |

## Related Resources

- [Project Overview](project-overview.md)
- [Data Flow & Integrations](data-flow.md)
- [Development Workflow](development-workflow.md)
- [Testing Strategy](testing-strategy.md)
- [AGENTS.md](../../AGENTS.md) — Full project conventions and rules
