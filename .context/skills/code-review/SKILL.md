---
type: skill
name: Code Review
description: Review PRs for Django Hyperview conventions and quality. Use when reviewing code changes, before merging PRs, or auditing code quality.
skillSlug: code-review
phases: [R]
generated: 2026-05-25
status: filled
scaffoldVersion: "2.0.0"
---

## Workflow

1. Read the PR description and diff
2. Verify Django conventions (CBV pattern, URL naming, CSRF handling)
3. Check HXML template correctness (namespaces, scroll rules, key uniqueness)
4. Review test coverage (new views get tests, `reverse()` used)
5. Verify dependency changes use `uv` workflow
6. Run the test suite
7. Provide actionable feedback

## Review Checklist

### Django
- [ ] `TemplateView` for read-only, `View` with `get()`/`post()` for forms
- [ ] No `if request.method == "POST"` in function views
- [ ] `content_type='application/xml'` on all HXML responses
- [ ] `@method_decorator(csrf_exempt, name="dispatch")` on mobile POST views
- [ ] `_base_url(self.request)` in context for HXML hrefs
- [ ] `show_back`/`back_href` context variables set correctly

### URLs
- [ ] Registered in `hv/urls.py` with `app_name = "hv"`
- [ ] Snake_case names consistent with existing patterns
- [ ] Path converters match parameter types

### HXML Templates
- [ ] `<doc>` has `xmlns`, `xmlns:navigation`, `xmlns:safe-area`
- [ ] `<body scroll="false">` if screen uses `<list>`
- [ ] `<styles>` inside `<screen>` block
- [ ] Unique `key` attributes on `<item>` elements
- [ ] Tab bar included on tab screens
- [ ] `href-style` for tappable wrappers
- [ ] Template extends `base.xml` correctly

### Tests
- [ ] New views have tests in `hv/tests.py`
- [ ] `reverse("hv:name")` used for URLs
- [ ] `Content-Type` assertion present
- [ ] Both GET and POST tested for form views

### Dependencies
- [ ] `uv add` used (not manual `requirements.txt` edit)
- [ ] `uv.lock` updated
- [ ] `requirements.txt` exported via `uv export`

## Quality Bar

- All items in checklist verified
- Test suite passes: `docker compose exec web python manage.py test hv`
- No obvious security issues (unnecessary `csrf_exempt`, exposed secrets)
- Conventions consistent with existing codebase
