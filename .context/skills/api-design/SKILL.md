---
type: skill
name: Api Design
description: Design HXML hypermedia endpoints following Hyperview patterns. Use when designing new Hyperview endpoints, restructuring URL patterns, or planning navigation flows.
skillSlug: api-design
phases: [P, R]
generated: 2026-05-25
status: filled
scaffoldVersion: "2.0.0"
---

## Workflow

1. Define the screen type: full page, fragment (infinite scroll), or modal
2. Choose the CBV: `TemplateView` for read-only, `View` with `get()`/`post()` for forms
3. Design URL following RESTful conventions: `/hyperview/resource/`, `/hyperview/resource/<id>/`
4. Determine context variables the template needs
5. Plan error handling (server-side validation errors, auth errors)
6. Register in `hv/urls.py` with `app_name = "hv"` and descriptive snake_case name
7. Add CSRF exemption if POST from mobile

## Endpoint Patterns

| Pattern | View Class | Use Case |
|---------|-----------|----------|
| `TemplateView` | Read-only screen | Home, About, Settings, Profile, Detail |
| `View` with `get()`/`post()` | Form with validation | Form, Login, Delete, ProfileEdit, Logout |
| Fragment endpoint | Infinite scroll items | `ListItemsView` returning `<items>` wrapper |

## URL Conventions

```python
# In hv/urls.py:
path("", IndexView.as_view(), name="index")           # Navigator entrypoint
path("home/", HomeView.as_view(), name="home")        # Tab screen
path("list/", ListView.as_view(), name="list")        # Tab screen
path("list/items/", ListItemsView.as_view(), name="list_items")  # Fragment
path("detail/<int:item_id>/", DetailView.as_view(), name="detail")
path("form/", FormView.as_view(), name="form")
path("detail/<int:item_id>/share/", ShareView.as_view(), name="detail_share")
path("detail/<int:item_id>/delete/", DeleteView.as_view(), name="detail_delete")
```

## Quality Bar

- URL names use snake_case, consistent with existing patterns
- Path converters match parameter types (`<int:item_id>`)
- All endpoints return `content_type='application/xml'`
- Fragment endpoints return partial XML (not full `<screen>`)
- Tests use `reverse("hv:name")` — never hardcoded paths
- `csrf_exempt` only on mobile POST endpoints, with code comment explaining why

## Reference Files

- `hv/urls.py` — All existing URL patterns
- `hv/views.py` — All existing CBV implementations
- `hv/tests.py` — Test patterns using `reverse()`
