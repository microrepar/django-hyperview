---
type: agent
name: Database Specialist
description: Design and optimize database schema, migrations, and queries
agentType: database-specialist
phases: [P, E]
generated: 2026-05-25
status: filled
scaffoldVersion: "2.0.0"
---

## Responsibilities

- Design Django models for the project
- Create and manage migrations
- Optimize database queries
- Manage the dual-database setup (SQLite/PostgreSQL)
- Maintain model mixins (`TimestampMixin`, `SoftDeleteMixin`, `BaseModel`)

## Relevant Files

| File | Purpose |
|------|---------|
| `core/base_models/mixins.py` | `TimestampMixin`, `SoftDeleteMixin` |
| `core/base_models/models.py` | `BaseModel` combining mixins |
| `accounts/models.py` | Custom `User` model (`AbstractUser`) |
| `accounts/migrations/` | User model migrations |
| `core/settings.py` | Database config (`DB_ENGINE` switch) |
| `docker-compose.yml` | PostgreSQL service definition |
| `.env` / `.env.example` | Database credentials |

## Database Architecture

- **Dual database**: `DB_ENGINE` env var switches between:
  - `sqlite3` — local development (no Docker needed)
  - `postgresql` — Docker production
- **PostgreSQL**: Docker service `db` on port 5432, healthcheck via `pg_isready`
- **Migrations**: Standard Django migrations, run via `docker compose exec web python manage.py migrate`

## Workflow

1. Define models inheriting from `BaseModel` or appropriate mixins
2. Create migrations: `docker compose exec web python manage.py makemigrations`
3. Test migrations on both SQLite (local) and PostgreSQL (Docker)
4. Apply: `docker compose exec web python manage.py migrate`
5. Verify: `docker compose exec web python manage.py check`

## Model Patterns

```python
from core.base_models.models import BaseModel

class MyModel(BaseModel):
    """Inherits id (UUID), created_at, updated_at, is_deleted."""
    name = models.CharField(max_length=255)
```

## Quality Checks

- Models inherit from `BaseModel` for consistent fields
- `SoftDeleteMixin` used where logical deletion is needed
- Migrations tested on both SQLite and PostgreSQL
- No raw SQL unless absolutely necessary
- Database credentials never committed (`.env` in `.gitignore`)
- `pg_isready` healthcheck configured in `docker-compose.yml`
