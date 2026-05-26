---
type: doc
name: data-flow
description: How data moves through the system and external integrations
category: data-flow
generated: 2026-05-25
status: filled
scaffoldVersion: "2.0.0"
---

## Data Flow & Integrations

Data flows through the system in two distinct pipelines — **web (HTML)** and **mobile (HXML)** —
both originating from the same Django backend and database, but rendered through different
template engines into different content types.

### Module Dependencies

```
core/urls.py
  ├── include("hv.urls")     → hv/urls.py → hv/views.py → templates/hv/*.xml
  ├── include("django.contrib.auth.urls")  → Django auth views
  ├── HomeView (web)          → core/views.py → templates/home.html
  └── admin/                  → Django admin

hv/views.py
  ├── django.views.generic.base.TemplateView  (read-only screens)
  ├── django.views.View                       (GET+POST forms)
  └── templates/hv/*.xml                      (13 templates)

core/base_models/
  ├── mixins.py (TimestampMixin, SoftDeleteMixin)
  └── models.py (BaseModel combining mixins)

accounts/
  └── models.py (User extends AbstractUser)
```

### Service Layer

Django does not have a separate service layer — business logic lives in views:

| View Class | Type | Data Source | Output |
|-----------|------|-------------|--------|
| `IndexView` | TemplateView | Static context | `hv/index.xml` |
| `HomeView` | TemplateView | Hardcoded updates + user | `hv/home.xml` |
| `ListView` | TemplateView | Generated items (50), paginated | `hv/list.xml` |
| `ListItemsView` | TemplateView | Generated items (50), paginated | `hv/list_items.xml` (fragment) |
| `DetailView` | TemplateView | URL param (`item_id`) | `hv/detail.xml` |
| `FormView` | View (GET+POST) | POST data validation | `hv/form.xml` |
| `LoginView` | View (GET+POST) | `django.contrib.auth.authenticate()` | `hv/login.xml` |
| `ProfileView` | TemplateView | `request.user` | `hv/profile.xml` |
| `SettingsView` | TemplateView | Static context | `hv/settings.xml` |
| `AboutView` | TemplateView | Static context | `hv/about.xml` |
| `ShareView` | TemplateView | URL param (`item_id`) | `hv/share.xml` |
| `DeleteView` | View (GET+POST) | URL param (`item_id`) | `hv/delete.xml` |
| `ProfileEditView` | View (GET+POST) | `request.user` + POST data | `hv/profile_edit.xml` |
| `LogoutView` | View (GET+POST) | `django.contrib.auth.logout()` | `hv/logout.xml` |

### High-level Flow

**Mobile (HXML) Request Flow:**
1. Mobile app sends `GET /hyperview/` → Django returns `hv/index.xml` with `<navigator>` and tab routes
2. User taps a tab → app navigates to the tab's `href` (e.g., `/hyperview/home/`)
3. Django view builds context, renders HXML template, returns `Content-Type: application/xml`
4. Hyperview client parses XML, renders native components (lists, forms, buttons)
5. User interactions (tap, form submit, scroll) trigger `<behavior>` elements → new HTTP requests
6. Django processes (validates, queries) and returns new XML (full screen or fragment)
7. Hyperview client updates the UI (replace, append, navigate)

**Infinite Scroll Flow:**
1. `GET /hyperview/list/` → `ListView` renders full page with first page of items + sentinel
2. Sentinel `<item trigger="visible">` fires `GET /hyperview/list/items/?page=2`
3. `ListItemsView` returns `<items>` wrapper with new items + next sentinel
4. `action="replace"` replaces the sentinel, appending new items
5. Last page omits sentinel → no more requests

**Pull-to-Refresh Flow:**
1. User pulls down on list → `<behavior trigger="refresh" action="replace" target="main-list">`
2. Request to `GET /hyperview/list/?page=1`
3. Server returns full `<list>` XML
4. Hyperview replaces the entire list

**Form Submission Flow:**
1. User fills form, taps submit → `<behavior trigger="submit" action="replace">` POSTs to same URL
2. `FormView.post()` validates fields server-side
3. If invalid: returns same form XML with `<text style="error">` elements
4. If valid: returns form XML with success message

### Internal Movement

- **No message queues between views**: All communication is synchronous HTTP request/response.
- **No events or signals used**: Views are self-contained; no Django signals for Hyperview flows.
- **Celery**: Available for background tasks (`redis` + `worker` services in Docker) but not
  currently used by Hyperview views.
- **Session auth**: Django's standard session middleware. Mobile auth via `LoginView` POST.
- **Database**: All views currently use hardcoded/generated data (no real models in `hv` app).
  The `accounts.User` model is the only database-backed model in active use.

### External Integrations

| Integration | Endpoint | Method | Auth |
|-------------|----------|--------|------|
| Hyperview Mobile Client | `/hyperview/*` | GET/POST | Session (cookie) or csrf_exempt |
| Web Browser | `/` and `/admin/` | GET | Session |
| Nginx | All traffic | Reverse proxy | — |
| PostgreSQL | Internal Docker network | TCP | `.env` credentials |
| Redis | Internal Docker network | TCP | None |

### Observability & Failure Modes

- **Logging**: Django's default logging to stdout (captured by Docker).
- **Error handling**: HXML templates include error message display. Views return 200 with
  error context rather than HTTP error codes (Hyperview pattern).
- **No dead-letter queues**: Failed requests are silently dropped on the mobile client side.
- **Database failures**: Django raises exceptions; Nginx returns 502. No retry logic at
  application level.
- **CSS build failures**: Tailwind CLI errors surface during Docker build. Runtime CSS
  is static after `collectstatic`.

## Related Resources

- [Architecture Notes](architecture.md)
- [Project Overview](project-overview.md)
- [Development Workflow](development-workflow.md)
