---
type: skill
name: Commit Message
description: Write conventional commit messages for the Django Hyperview project. Use when crafting git commits, squashing PRs, or preparing release notes.
skillSlug: commit-message
phases: [E, C]
generated: 2026-05-25
status: filled
scaffoldVersion: "2.0.0"
---

## Workflow

1. Identify the type of change: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`
2. Scope to the affected area: `hv`, `core`, `accounts`, `templates`, `docker`, `deps`
3. Write a concise summary in imperative mood
4. Add body with details if the change is complex

## Format

```
<type>(<scope>): <summary>

<body>
```

## Types

| Type | Use Case |
|------|----------|
| `feat` | New Hyperview screen, view, or endpoint |
| `fix` | Bug fix in views, templates, or config |
| `refactor` | Code restructuring without behavior change |
| `test` | Adding or updating tests |
| `docs` | Documentation updates (AGENTS.md, .context/, docs/) |
| `chore` | Build, deps, Docker, CI changes |
| `style` | HXML template formatting, CSS changes |

## Examples

```
feat(hv): add ShareView endpoint for item sharing
fix(hv): prefix item keys with page number to prevent duplicate keys
refactor(hv): extract _base_url() helper to reduce duplication
test(hv): add tests for LoginView POST valid/invalid
docs(context): fill architecture.md with project-specific content
chore(deps): add django-extensions via uv
fix(templates): add scroll="false" to body in list screens
```

## Quality Bar

- Type and scope are correct
- Summary is in imperative mood ("add" not "adds" or "added")
- Body explains why, not just what
- References to issue numbers if applicable
