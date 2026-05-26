---
type: skill
name: Feature Breakdown
description: Break down feature requests into implementable tasks for Django Hyperview. Use when planning new Hyperview screens, new Django apps, or major feature additions.
skillSlug: feature-breakdown
phases: [P]
generated: 2026-05-25
status: filled
scaffoldVersion: "2.0.0"
---

## Workflow

1. Understand the feature from the user's perspective (mobile screen or web page)
2. Determine which architectural layer it touches (view, template, model, config)
3. Break down into tasks following the implementation order:
   - URL pattern
   - View class (with context)
   - HXML template (or HTML template)
   - Template includes (if reusable components)
   - Tests
   - Documentation updates

## Task Breakdown Template

For a new Hyperview screen:

```
1. [hv] Register URL: path("name/", NameView.as_view(), name="name")
2. [hv] Implement NameView (TemplateView or View with get/post)
   - Context variables: base_url, show_back, ...
3. [templates] Create hv/name.xml extending base.xml
   - Fill {% block styles %}, {% block container %}, {% block tab_bar %}
4. [templates] Create includes if needed (name_styles.xml + name.xml)
5. [tests] Add test_name to HyperviewViewsTestCase
6. [docs] Update AGENTS.md endpoint table
7. [docs] Update docs/HYPERVIEW.md reference section
```

## Estimation Guidelines

| Complexity | Scope | Example |
|-----------|-------|---------|
| Small | Read-only screen with static data | `AboutView` |
| Medium | Screen with URL params + context | `DetailView` |
| Large | Form with GET+POST + validation | `FormView`, `LoginView` |
| Complex | Screen with auth, DB queries, fragments | Full CRUD with infinite scroll |

## Quality Bar

- Tasks are ordered (dependencies first)
- Each task is independently verifiable
- All files that need changes are identified
- Tests and docs are included in the breakdown
- Pattern matches existing codebase conventions
