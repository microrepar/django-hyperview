---
type: skill
name: Refactoring
description: Improve Django Hyperview code structure without changing behavior. Use when consolidating views, extracting mixins, reorganizing templates, or simplifying logic.
skillSlug: refactoring
phases: [P, E]
generated: 2026-05-25
status: filled
scaffoldVersion: "2.0.0"
---

## Workflow

1. Run tests to establish baseline: `docker compose exec web python manage.py test hv`
2. Identify the pattern to refactor
3. Apply the change in small, testable steps
4. Run tests after each step
5. Verify HXML output is identical (diff before/after XML responses)
6. Update docs if conventions changed

## Refactoring Targets

### View Layer
- **Boilerplate reduction**: 14 views repeat `content_type = "application/xml"` and `_base_url(self.request)`
  - **Solution**: Extract `HyperviewTemplateView` base class or `HyperviewContextMixin`

### Template Layer
- **DRY includes**: Common patterns across templates (form fields, error display, list items)
  - **Solution**: Extract more `includes/` components (each needs `_styles.xml` + `.xml`)

### URL Layer
- Currently clean — no refactoring needed

## Rules

1. **Tests first, tests last**: Never refactor without passing test suite
2. **Behavior preservation**: HXML output must be identical
3. **Small steps**: Each commit should be independently reviewable
4. **Document changes**: Update AGENTS.md if conventions change
5. **Don't over-engineer**: Current duplication is acceptable for 14 views

## Quality Bar

- All 11 tests pass before and after
- HXML output is byte-identical (verify with `curl | xmllint --format` diff)
- New abstractions have clear names and documented purpose
- No feature additions mixed with refactoring
