---
type: doc
name: glossary
description: Key terms and concepts used throughout the project
category: reference
generated: 2026-05-25
status: filled
scaffoldVersion: "2.0.0"
---

## Glossary

### Hyperview & HXML

| Term | Definition |
|------|-----------|
| **Hyperview** | Open-source framework for server-driven mobile apps. Backend serves XML, client renders native UI. |
| **HXML** | Hyperview XML — the markup format describing mobile screens, lists, forms, and navigation. |
| **`<doc>`** | Root element of every HXML document. Declares XML namespaces. |
| **`<screen>`** | Represents a full mobile screen. Contains `<styles>`, `<body>`, and optional loading screens. |
| **`<body>`** | Container for screen content. `scroll="false"` is required when using `<list>`. |
| **`<list>`** | Renders a native FlatList (VirtualizedList). Must not be nested inside ScrollView. |
| **`<item>`** | Child of `<list>`. Represents a single row. Can have `trigger`, `action`, `href` for interactivity. |
| **`<behavior>`** | Declarative interaction. Attributes: `trigger` (press, visible, refresh, submit), `action` (push, replace, append, navigate, back), `href` (target URL). |
| **`<view>`** | Generic container. Use `scroll="true"` for scrollable content areas. |
| **`<text>`** | Text display. Supports `style` for styling. |
| **`<text-field>`** | Text input field. Name attribute maps to POST parameter. |
| **`<spinner>`** | Loading indicator. Typically used in sentinel items for infinite scroll. |
| **`<navigator>`** | Navigation container. Defines stack, tab, or modal navigator structure. |
| **`<nav-route>`** | Named route within a navigator. `id` is used for programmatic navigation. |
| **`<styles>`** | Style definitions within a `<screen>`. Cannot be placed in `<body>`. |
| **Namespaces** | Required in `<doc>`: `xmlns="https://hyperview.org/hyperview"`, `xmlns:navigation`, `xmlns:safe-area`. |

### Django Concepts

| Term | Definition |
|------|-----------|
| **CBV** | Class-Based View. Django pattern using classes instead of functions for views. |
| **TemplateView** | Simplest CBV. Renders a template with context. Used for read-only screens. |
| **`View`** | Base CBV class. Use with `get()`/`post()` methods for forms. |
| **`reverse()`** | Django function to resolve URL names to paths. Used in tests: `reverse("hv:list")`. |
| **`app_name`** | Namespace for app URLs. Defined in `hv/urls.py` as `app_name = "hv"`. |
| **`csrf_exempt`** | Decorator disabling CSRF protection. Used on mobile POST endpoints that don't use cookies. |
| **`content_type`** | Response header. HXML views return `"application/xml"` instead of `"text/html"`. |
| **`HYPERVIEW_BASE_URL`** | Env var for base URL of HXML hyperlinks. Falls back to request scheme/host if unset. |
| **`DB_ENGINE`** | Env var switching between `sqlite3` (local) and `postgresql` (Docker). |

### Project-Specific

| Term | Definition |
|------|-----------|
| **Infinite Scroll** | Pattern where new items load as the user scrolls. Uses a sentinel `<item>` with `trigger="visible"`. |
| **Pull-to-Refresh** | Pattern where pulling down on a list reloads it. Uses `<behavior trigger="refresh" action="replace">`. |
| **Fragment Endpoint** | An endpoint that returns partial XML (not a full `<screen>`). Used by `ListItemsView`. |
| **Sentinel** | The `<item>` at the end of a list that triggers loading more data. Has `id="load-more-spinner"`. |
| **Tab Bar** | Bottom navigation bar. Rendered via custom element `<navigation:bottom-tab-bar>`. Must be included in each tab screen manually. |
| **Header** | Top bar with optional back button. Uses `show_back` and `back_href` context variables. |
| **Loading Screens** | Three variants: `loading_pushed.xml` (push navigation), `loading_modal.xml` (modal), `loading_reload.xml` (reload). Included in `base.xml`. |
| **`_base_url()`** | Helper function in `hv/views.py:27` that resolves the base URL for HXML hrefs. Uses `HYPERVIEW_BASE_URL` or request scheme/host. |

## Related Resources

- [Architecture Notes](architecture.md)
- [Development Workflow](development-workflow.md)
- [docs/HYPERVIEW.md](../../docs/HYPERVIEW.md) — Full Hyperview reference
