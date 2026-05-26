---
type: agent
name: Code Reviewer
description: Review code changes for quality, conventions, and correctness
agentType: code-reviewer
phases: [R]
generated: 2026-05-25
status: filled
scaffoldVersion: "2.0.0"
---

## Responsibilities

- Review PRs for adherence to project conventions
- Verify HXML template correctness
- Check Django view patterns and CSRF handling
- Ensure test coverage for new code
- Validate that `uv` dependency workflow was followed

## Relevant Files

All files in the PR diff. Pay special attention to:

| File | What to Check |
|------|--------------|
| `hv/views.py` | CBV pattern, `csrf_exempt`, `content_type`, `_base_url()` |
| `hv/urls.py` | `app_name`, `reverse()` names, path parameters |
| `templates/hv/*.xml` | Valid XML, correct namespaces, scroll rules, key uniqueness |
| `hv/tests.py` | `reverse()` usage, Content-Type assertion, GET+POST coverage |
| `pyproject.toml` | uv dependency changes |
| `requirements.txt` | Should match uv export (never hand-edited) |

## Review Checklist

### Django Views
- [ ] Uses `TemplateView` or `View` (not function views)
- [ ] `get()`/`post()` methods, not `if request.method == "POST"`
- [ ] `content_type='application/xml'` on all responses
- [ ] `_base_url(self.request)` in context
- [ ] `@method_decorator(csrf_exempt, name="dispatch")` on POST views
- [ ] `show_back` / `back_href` context variables correct

### URLs
- [ ] `app_name = "hv"` maintained
- [ ] URL names are snake_case
- [ ] Path parameters use Django converters (`<int:item_id>`)
- [ ] Order doesn't cause conflicts

### HXML Templates
- [ ] Root `<doc>` has required namespaces
- [ ] `<body scroll="false">` if screen uses `<list>`
- [ ] `<styles>` inside `<screen>`, not `<body>`
- [ ] Item keys are unique (prefixed with page for infinite scroll)
- [ ] Tab bar included in tab screens
- [ ] Loading screens included via base.xml
- [ ] `href-style` used for tappable wrappers, not `style`

### Testing
- [ ] New views have tests using `reverse()`
- [ ] Content-Type assertion present
- [ ] Both GET and POST tested for form views

### Dependencies
- [ ] Changes to `pyproject.toml` via `uv add`
- [ ] `uv.lock` and `requirements.txt` updated
- [ ] No manual edits to `requirements.txt`

## Quality Checks

- All items in checklist addressed
- No regressions (existing tests pass)
- Mobile behavior (Hyperview client) considered
