---
type: agent
name: Bug Fixer
description: Diagnose and fix bugs in the Django Hyperview application
agentType: bug-fixer
phases: [E]
generated: 2026-05-25
status: filled
scaffoldVersion: "2.0.0"
---

## Responsibilities

- Reproduce and diagnose bugs in Django views, HXML templates, or mobile rendering
- Fix issues in Hyperview HXML templates (wrong elements, missing attributes, styling bugs)
- Fix Django view logic (incorrect context, validation errors, URL routing)
- Fix Docker/nginx configuration issues

## Relevant Files

| File | Purpose |
|------|---------|
| `hv/views.py` | View logic bugs |
| `hv/urls.py` | URL routing bugs |
| `templates/hv/` | HXML template bugs (most common source) |
| `templates/hv/includes/` | Header, tab bar, loading screen bugs |
| `core/settings.py` | Configuration bugs |
| `nginx.conf` | Proxy/static file bugs |
| `docker-compose.yml` | Service bugs |

## Debugging Workflow

1. Reproduce the bug: `docker compose exec web python manage.py test hv`
2. Check Django logs: `docker compose logs -f web`
3. For HXML bugs: inspect the response XML directly via curl:
   ```bash
   curl -s http://localhost:8000/hyperview/list/ | xmllint --format -
   ```
4. Verify XML validity: missing namespaces, unclosed tags, invalid attributes
5. Check React Native errors in Hyperview client logs for key conflicts, scroll issues

## Common Bugs & Fixes

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| "Encountered two children with the same key" | Duplicate `key` in `<item>` | Prefix keys with page number in infinite scroll |
| FlatList inside ScrollView error | `<body>` has `scroll="true"` with `<list>` | Set `<body scroll="false">` |
| Tab bar not showing | Missing `<navigation:bottom-tab-bar>` | Add tab bar include to screen template |
| Back button not working | Wrong `back_href` or missing `show_back` | Check context in view |
| Infinite scroll loads same items | Page not incrementing in sentinel href | Fix `next_page` context variable |
| CSRF 403 on POST | Missing `csrf_exempt` decorator | Add `@method_decorator(csrf_exempt, name="dispatch")` |
| Styles not applying | `<styles>` placed in `<body>` instead of `<screen>` | Move to `<screen><styles>` |
| Docker file permission errors | Files on `/mnt/c/...` mount | Use `docker compose exec -T web python3 -c "..."` |

## Quality Checks

- Fix is verified with the test suite
- Regression test added if applicable
- No new issues introduced in template rendering
- HXML remains valid XML
