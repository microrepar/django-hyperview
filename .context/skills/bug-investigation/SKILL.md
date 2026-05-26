---
type: skill
name: Bug Investigation
description: Systematically diagnose and fix bugs in Django Hyperview. Use when debugging HXML rendering issues, Django view errors, template problems, or mobile client misbehavior.
skillSlug: bug-investigation
phases: [E, V]
generated: 2026-05-25
status: filled
scaffoldVersion: "2.0.0"
---

## Workflow

1. **Reproduce**: Run the failing test or curl the endpoint:
   ```bash
   docker compose exec web python manage.py test hv
   curl -s http://localhost:8000/hyperview/list/ | xmllint --format -
   ```
2. **Isolate**: Determine if bug is in view logic, template, or mobile client
3. **Compare**: Check against known correct patterns in the codebase
4. **Fix**: Apply minimal, targeted fix
5. **Verify**: Run tests, check XML output, verify mobile behavior

## Common Categories

### HXML Template Bugs
- **Symptom**: "Encountered two children with the same key" in React Native
  - **Cause**: Duplicate `key` attributes in `<item>` (common with `{% regroup %}` + infinite scroll)
  - **Fix**: Prefix keys with page number: `key="header-p{{ page }}-{{ group }}"`

- **Symptom**: FlatList inside ScrollView error
  - **Cause**: `<body>` has scroll enabled with `<list>` present
  - **Fix**: Set `<body scroll="false">`

- **Symptom**: Styles not applying
  - **Cause**: `<styles>` placed in `<body>` instead of `<screen>`
  - **Fix**: Move to `<screen><styles>...</styles></screen>`

### Django View Bugs
- **Symptom**: CSRF 403 on POST
  - **Cause**: Missing `@method_decorator(csrf_exempt, name="dispatch")`
  - **Fix**: Add decorator to mobile POST views

- **Symptom**: Wrong Content-Type
  - **Cause**: Missing `content_type='application/xml'` in response
  - **Fix**: Add to `render()` call or set on `TemplateView`

- **Symptom**: Tab bar not appearing
  - **Cause**: Missing `{% block tab_bar %}` include
  - **Fix**: Add tab bar include to screen template

### Docker/WSL Bugs
- **Symptom**: File permission errors editing `.py` files
  - **Cause**: Files on `/mnt/c/...` mount
  - **Fix**: Use `docker compose exec -T web python3 -c "..."` for edits

## Quality Bar

- Fix is verified by the test suite
- Regression test added for the specific bug
- No new issues introduced
- Bug documented in AGENTS.md "Lições aprendidas" if it's a reusable lesson
