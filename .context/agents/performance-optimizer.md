---
type: agent
name: Performance Optimizer
description: Identify and fix performance bottlenecks
agentType: performance-optimizer
phases: [E]
generated: 2026-05-25
status: filled
scaffoldVersion: "2.0.0"
---

## Responsibilities

- Profile Django views for slow responses
- Optimize database queries (N+1 problems, missing indexes)
- Reduce HXML response size
- Optimize Tailwind CSS output
- Improve Docker build times and image sizes

## Relevant Files

| File | Purpose |
|------|---------|
| `hv/views.py` | View logic — most likely bottleneck |
| `templates/hv/` | Template rendering performance |
| `core/settings.py` | Django caching, database config |
| `Dockerfile` | Build optimization (layer caching, image size) |
| `docker-compose.yml` | Service resource limits |
| `requirements.txt` | Dependency size |

## Performance Considerations

### Django Views
- All current views use in-memory generated data (50 items). With a real database:
  - Use `select_related()` / `prefetch_related()` to avoid N+1 queries
  - Paginate with Django's `Paginator` instead of list slicing
  - Consider `only()` / `defer()` for large models

### HXML Responses
- Keep XML as lean as possible — every byte goes over mobile network
- Avoid redundant style definitions
- Use fragment endpoints (`ListItemsView` pattern) for large lists
- Consider gzip compression (Nginx can handle this)

### Database
- SQLite: fine for local dev but not for concurrent mobile users
- PostgreSQL: add indexes on filtered/sorted columns
- Connection pooling: Django's default `CONN_MAX_AGE` for persistent connections

### Docker
- Layer caching: copy `requirements.txt` before source code in Dockerfile
- `.dockerignore`: exclude `.venv`, `.git`, `node_modules`, `__pycache__`
- Worker resource limits already set in `docker-compose.yml`

### Tailwind CSS
- Already using `--minify` flag in production build
- Purge unused styles: Tailwind v4 standalone handles this automatically

## Quality Checks

- No visible latency increase in mobile interactions
- Docker build time under 2 minutes
- HXML response sizes reasonable (< 50KB typical)
- Database queries logged and analyzed in development
