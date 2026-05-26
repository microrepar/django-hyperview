---
type: skill
name: PR Review
description: Review pull requests holistically — code, tests, docs, and deployment impact. Use when reviewing PRs before merge in the Django Hyperview project.
skillSlug: pr-review
phases: [R]
generated: 2026-05-25
status: filled
scaffoldVersion: "2.0.0"
---

## Workflow

1. **Context**: Read PR description, linked issue, and discussion
2. **Code**: Review against Django and Hyperview conventions
3. **Tests**: Verify new tests exist and pass
4. **Docs**: Check that documentation is updated
5. **Deploy**: Assess Docker, Nginx, or config impact
6. **Run**: Execute test suite and local verification
7. **Feedback**: Provide clear, actionable review comments

## PR Review Checklist

### Code Quality
- [ ] CBV pattern: `TemplateView` (read-only) or `View` with `get()`/`post()` (forms)
- [ ] `content_type='application/xml'` on HXML responses
- [ ] `csrf_exempt` only on mobile POST views, with documentation
- [ ] `_base_url()` used for all HXML hrefs
- [ ] No duplicated code — use includes or base classes

### Template Quality
- [ ] Valid XML (well-formed, correct namespaces)
- [ ] `<body scroll="false">` when `<list>` present
- [ ] `<styles>` in `<screen>`, not `<body>`
- [ ] Unique item keys (prefixed for infinite scroll)
- [ ] Tab bar on tab screens
- [ ] `href-style` on tappable wrappers

### Test Quality
- [ ] New views have tests in `hv/tests.py`
- [ ] `reverse("hv:name")` used for URLs
- [ ] Content-Type assertion
- [ ] GET + POST tested for forms
- [ ] Existing tests still pass

### Documentation
- [ ] `AGENTS.md` updated (new rules, endpoints, patterns, lessons)
- [ ] `.context/docs/` updated if architecture/flow changes
- [ ] `docs/HYPERVIEW.md` updated for new HXML patterns

### Dependencies
- [ ] `uv add` used (not manual edit)
- [ ] `uv.lock` + `requirements.txt` updated
- [ ] Docker rebuild tested if Dockerfile changed

## Quality Bar

- All checklist items verified
- `docker compose exec web python manage.py test hv` passes
- No security concerns (exposed secrets, unnecessary csrf_exempt)
- PR is scoped appropriately (not mixing unrelated changes)
