---
type: doc
name: tooling
description: Development tools, build system, and utilities
category: tooling
generated: 2026-05-25
status: filled
scaffoldVersion: "2.0.0"
---

## Tooling Guide

### Package Management: uv

**uv** is the Python package and project manager. All dependency operations go through uv.

```bash
# Add a dependency
uv add "django>=5.2"

# Update lock file
uv lock

# Export to requirements.txt (for Docker)
uv export --format requirements.txt --output requirements.txt --without-hashes

# Sync environment
uv sync
```

**Never edit `requirements.txt` directly** — it's generated from `uv.lock`/`pyproject.toml`.

### Task Runner: taskipy

Defined in `pyproject.toml`:

```toml
[tool.taskipy.tasks]
css-build = "tailwindcss -i core/static/core/css/input.css -o core/static/core/css/output.css --minify"
css-watch = "tailwindcss -i core/static/core/css/input.css -o core/static/core/css/output.css --watch"
css-dev = "tailwindcss -i core/static/core/css/input.css -o core/static/core/css/output.css"
```

```bash
uv run task css-build   # Production CSS build
uv run task css-watch   # Watch mode for development
uv run task css-dev     # Dev build (unminified)
```

### CSS: Tailwind CSS v4 (Standalone CLI)

Tailwind runs as a standalone binary (no Node.js required), bundled in the Docker image:

```dockerfile
# From Dockerfile
RUN curl -sLO https://github.com/tailwindlabs/tailwindcss/releases/download/v4.0.0/tailwindcss-linux-x64 \
    && chmod +x tailwindcss-linux-x64 \
    && mv tailwindcss-linux-x64 /usr/local/bin/tailwindcss
```

**Input**: `core/static/core/css/input.css`
**Output**: `core/static/core/css/output.css`

### Containerization: Docker Compose

**Services:**
| Service | Image | Port | Purpose |
|---------|-------|------|---------|
| `db` | `postgres:15` | 5432 | Database |
| `web` | Custom Dockerfile | 8000 | Django app |
| `nginx` | Custom `nginx.Dockerfile` | 8080 → 80 | Reverse proxy + static files |
| `redis` | `redis:6.2` | — | Celery broker |
| `worker` | Custom Dockerfile | — | Celery worker |

**Key commands:**
```bash
docker compose up -d --build   # Start all services
docker compose down            # Stop all services
docker compose logs -f web     # Follow web logs
docker compose exec web bash   # Shell inside web container
docker compose exec web python manage.py <cmd>  # Django management
```

### Django Extensions

Included in `INSTALLED_APPS`:
- **`django_extensions`**: Shell plus, graph models, runscript, etc.
- **`django_htmx`**: HTMX integration middleware for web frontend.

### Development Tools

| Tool | Purpose | Command |
|------|---------|---------|
| `python manage.py check` | Django system checks | `docker compose exec web python manage.py check` |
| `python manage.py test` | Run tests | `docker compose exec web python manage.py test hv` |
| `python manage.py shell` | Interactive shell | `docker compose exec web python manage.py shell` |
| `python manage.py makemigrations` | Create migrations | `docker compose exec web python manage.py makemigrations` |
| `python manage.py migrate` | Apply migrations | `docker compose exec web python manage.py migrate` |
| `python manage.py collectstatic` | Collect static files | `docker compose exec web python manage.py collectstatic --noinput` |

### Mobile Build Tool: EAS (Expo Application Services)

For building the Hyperview mobile client APK:
```bash
cd /mnt/c/workspaces/PythonProjects/hyperview/demo
eas login
BASE_URL="https://YOUR_DOMAIN" eas build --platform android --profile preview
```

### Local Dev Without Docker

```bash
# Set SQLite database
export DB_ENGINE=sqlite3

# Install dependencies
uv sync

# Run Django
python manage.py runserver

# Build CSS
uv run task css-dev
```

## Related Resources

- [Development Workflow](development-workflow.md)
- [Testing Strategy](testing-strategy.md)
- [pyproject.toml](../../pyproject.toml)
- [docker-compose.yml](../../docker-compose.yml)
- [Dockerfile](../../Dockerfile)
