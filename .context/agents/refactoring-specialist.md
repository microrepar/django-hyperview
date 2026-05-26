---
type: agent
name: Refactoring Specialist
description: Improve code structure without changing behavior
agentType: refactoring-specialist
phases: [P, E]
generated: 2026-05-25
status: filled
scaffoldVersion: "2.0.0"
---

## Responsibilities

- Refactor `hv/views.py` to reduce duplication
- Extract reusable patterns into mixins or base classes
- Reorganize HXML template includes
- Simplify complex view logic
- Ensure tests pass throughout refactoring

## Relevant Files

| File | Purpose |
|------|---------|
| `hv/views.py` | Primary refactoring target — 14 CBVs |
| `hv/urls.py` | URL structure |
| `templates/hv/base.xml` | Template inheritance chain |
| `templates/hv/includes/` | Reusable template components |
| `hv/tests.py` | Safety net — run before/after every refactor |

## Refactoring Opportunities

### View Consolidation
- Many views repeat the same pattern: `TemplateView` + `content_type = "application/xml"` + `_base_url()` in context
- Could extract a `HyperviewTemplateView` base class that handles this boilerplate
- `_base_url()` is repeated in every view — could be a mixin method

### Template DRY
- Common patterns across templates: back button behavior, form fields, list items
- Could extract more reusable includes
- Error display pattern repeats in form.xml and login.xml

### URL Configuration
- Current `urls.py` is clean — no refactoring needed currently

## Refactoring Principles

1. **Tests first**: Run `docker compose exec web python manage.py test hv` before starting
2. **Small steps**: Each refactoring step should be independently testable
3. **Run tests after each step**: Catch regressions immediately
4. **Don't change behavior**: HXML output must be identical after refactoring
5. **Document in AGENTS.md**: If a pattern changes, update the documentation

## Quality Checks

- All 11 tests pass after refactoring
- No new tests needed if behavior is unchanged
- HXML output is byte-identical (verify with diff)
- New abstractions are documented
- `AGENTS.md` updated if conventions change
