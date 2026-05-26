---
type: skill
name: Documentation
description: Create and update project documentation following Django Hyperview conventions. Use when writing AGENTS.md updates, .context docs, Hyperview reference docs, or README changes.
skillSlug: documentation
phases: [P, R, C]
generated: 2026-05-25
status: filled
scaffoldVersion: "2.0.0"
---

## Workflow

1. Identify what document needs updating based on the change
2. Determine the right location:
   - **AGENTS.md**: Project conventions, rules, lessons learned
   - **.context/docs/**: Structured AI context (architecture, data-flow, etc.)
   - **docs/HYPERVIEW.md**: Full Hyperview reference guide
   - **.docs/DJANGO-SETUP.md**: Django setup conventions
3. Write concrete, verifiable content with real file paths
4. Cross-link to related documents
5. Verify paths and code examples are correct

## Document Map

| Change Type | Document to Update |
|-------------|-------------------|
| New view/endpoint | `AGENTS.md` (endpoint table), `docs/HYPERVIEW.md` (reference section) |
| New Hyperview pattern/pitfall | `AGENTS.md` (Lições aprendidas), `docs/HYPERVIEW.md` |
| New Django convention | `AGENTS.md` (Regras), `.docs/DJANGO-SETUP.md` |
| Architecture change | `.context/docs/architecture.md`, `.context/docs/data-flow.md` |
| New tool/command | `.context/docs/tooling.md`, `AGENTS.md` (Comandos essenciais) |
| Security concern | `.context/docs/security.md` |
| Test strategy change | `.context/docs/testing-strategy.md` |

## Writing Principles

1. **Concrete, not abstract**: Use real class names (`FormView`), file paths (`hv/views.py`), and commands
2. **Portuguese for dev docs**: AGENTS.md, Hyperview reference, Django setup (pt-br)
3. **English for context docs**: `.context/` files (AI consumption)
4. **Code examples**: Show exactly what to write, not abstract patterns
5. **Cross-reference**: Link between related docs
6. **Lessons learned**: Each Hyperview pitfall goes in AGENTS.md with root cause and fix

## Quality Bar

- All file paths are correct and exist in the repo
- Code examples are syntactically valid
- Cross-references are not broken
- New patterns are documented with examples from the codebase
- Content is actionable for both humans and AI agents
