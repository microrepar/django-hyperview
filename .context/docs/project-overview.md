---
type: doc
name: project-overview
description: High-level project description, goals, and tech stack
category: overview
generated: 2026-05-25
status: filled
scaffoldVersion: "2.0.0"
---

## Project Overview

**Django Hyperview** is a full-stack web and mobile application demonstrating server-driven
UI architecture. The Django backend serves both a traditional web frontend (Tailwind CSS + HTMX)
and a native mobile experience via **Hyperview** — an XML-based hypermedia format rendered
by a React Native client.

### Goals

- Demonstrate **Hyperview** integration with Django as a server-driven mobile framework
- Provide a reference implementation for HXML templates, navigation, forms, lists, and auth
- Serve dual frontends (web + mobile) from a single Django codebase
- Establish best practices for Django + Hyperview development

### Tech Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| Backend | Django | 5.2.x |
| Python | CPython | 3.13 |
| Database | PostgreSQL 15 (Docker) / SQLite (local) |
| Cache / Queues | Redis 6.2 + Celery 5.x |
| Proxy | Nginx | latest |
| Web Frontend | Tailwind CSS v4 (standalone CLI) + HTMX 2.x |
| Mobile Client | Hyperview (HXML) | 0.105 |
| Dependencies | uv | — |
| Containers | Docker Compose | — |

### Key Features

- **14 HXML endpoints** covering navigation, lists (infinite scroll + pull-to-refresh),
  forms with server-side validation, login, profile, settings, sharing, and deletion
- **Modular template system**: Base template with blocks, reusable includes (header, tab bar,
  loading screens)
- **Django CBVs**: `TemplateView` for read-only, `View` with `get()`/`post()` for forms
- **CSRF-exempt mobile endpoints**: Correct per Django docs for non-cookie API auth
- **Configurable base URL**: `HYPERVIEW_BASE_URL` env var for HXML hyperlinks
- **Dual database**: PostgreSQL in Docker, SQLite for local dev via `DB_ENGINE` env var

### Project Structure

```
django-hyperview/
├── core/                  # Django config (settings, urls, celery, wsgi)
│   ├── urls.py            # Root URL routing (include hv.urls)
│   ├── settings.py        # All Django settings
│   └── base_models/       # TimestampMixin, SoftDeleteMixin, BaseModel
├── hv/                    # Hyperview app (14 views, 14 URLs, 11 tests)
│   ├── urls.py            # app_name = "hv"
│   ├── views.py           # CBVs: TemplateView + View (GET/POST)
│   └── tests.py           # 11 test cases using reverse()
├── accounts/              # Custom User model (AbstractUser)
├── templates/
│   ├── base.html          # Web base template (Tailwind + HTMX)
│   ├── home.html          # Web home page
│   └── hv/                # HXML templates
│       ├── base.xml       # Base: <doc>, <screen>, header, loading screens
│       ├── index.xml      # Navigator with tab routes
│       ├── home.xml       # Dashboard
│       ├── list.xml       # Infinite scroll + pull-to-refresh
│       ├── list_items.xml # Fragment for infinite scroll
│       ├── detail.xml     # Item detail with actions
│       ├── form.xml       # Form with server-side validation
│       ├── login.xml      # Login screen
│       ├── profile.xml    # User profile
│       ├── settings.xml   # Settings screen
│       ├── about.xml      # About screen
│       ├── delete.xml     # Delete confirmation modal
│       ├── share.xml      # Share screen
│       ├── profile_edit.xml # Profile editing
│       ├── logout.xml     # Logout confirmation
│       └── includes/      # Reusable components
│           ├── header.xml / header_styles.xml
│           ├── tabbar.xml / tabbar_styles.xml
│           └── loading_*.xml (3 variants)
├── docker-compose.yml     # Services: db, web, nginx, redis, worker
├── Dockerfile             # Python 3.13 + Tailwind CSS CLI
├── nginx.conf             # Reverse proxy config
├── pyproject.toml         # uv + taskipy scripts
└── requirements.txt       # Exported from uv
```

### Mobile Client

The mobile app is the [Hyperview demo client](https://github.com/instawork/hyperview) (React Native/Expo).
Two configuration changes point it at this Django backend:
1. `App.tsx`: `entrypointUrl` → `/hyperview/`
2. `app.config.ts`: `baseUrl` uses `BASE_URL` env var

Build: `eas build --platform android --profile preview`
Dev: `yarn start` with `BASE_URL="http://<IP>:8000"`

## Related Resources

- [Architecture Notes](architecture.md)
- [Data Flow & Integrations](data-flow.md)
- [Development Workflow](development-workflow.md)
- [AGENTS.md](../../AGENTS.md)
