---
type: agent
name: Feature Developer
description: Implement new features end-to-end across the stack
agentType: feature-developer
phases: [P, E]
generated: 2026-05-25
status: filled
scaffoldVersion: "2.0.0"
---

## Responsibilities

- Implement new Hyperview screens end-to-end
- Create Django views, URL patterns, HXML templates, and tests
- Follow the established patterns and conventions
- Ensure mobile rendering correctness

## Relevant Files

| File | Purpose |
|------|---------|
| `hv/views.py` | New CBV implementation |
| `hv/urls.py` | URL registration |
| `templates/hv/` | New HXML template + any includes |
| `templates/hv/base.xml` | Base template (extend if needed) |
| `hv/tests.py` | New test methods |
| `docs/HYPERVIEW.md` | Reference for correct HXML patterns |

## Feature Implementation Workflow

1. **Plan**: Determine screen type (list, form, detail, simple view)
2. **Choose CBV**: `TemplateView` for read-only, `View` with `get()`/`post()` for forms
3. **Create URL**: `path("endpoint/", ViewClass.as_view(), name="endpoint")` in `hv/urls.py`
4. **Build template**: Create `hv/endpoint.xml` extending from `base.xml`
   - Fill `{% block styles %}` with screen-specific styles
   - Fill `{% block container %}` with screen content
   - Fill `{% block tab_bar %}` if it's a tab screen
5. **Implement view**: `get_context_data()` with all needed context
   - Always include `base_url` via `_base_url(self.request)`
   - Set `show_back` and `back_href` for header
6. **Add CSRF exemption**: If POST from mobile, add `@method_decorator(csrf_exempt, name="dispatch")`
7. **Write tests**: Add to `HyperviewViewsTestCase` in `hv/tests.py`
8. **Update docs**: Add entry to AGENTS.md lesson learned section if needed

## Template Checklist

- [ ] `<doc>` has required namespaces
- [ ] `<screen>` wraps everything
- [ ] `<styles>` inside `<screen>` with all needed styles
- [ ] If using `<list>`: `<body scroll="false">` and no ancestor with scroll
- [ ] If scrollable content (no list): `<view scroll="true" flex="1">` in container block
- [ ] Tab bar included if it's a tab screen
- [ ] `href-style` for tappable wrappers
- [ ] Unique keys for `<item>` elements

## Quality Checks

- View renders correctly at its URL
- Content-Type is `application/xml`
- Tests pass: `docker compose exec web python manage.py test hv`
- No regressions in existing tests
- HXML validates as well-formed XML
- Mobile behavior documented (how the screen looks on Hyperview client)
