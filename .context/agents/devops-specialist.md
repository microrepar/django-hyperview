---
type: agent
name: DevOps Specialist
description: Manage Docker, CI/CD, deployment, and infrastructure
agentType: devops-specialist
phases: [P, E]
generated: 2026-05-25
status: filled
scaffoldVersion: "2.0.0"
---

## Responsibilities

- Maintain Docker Compose configuration
- Manage Nginx reverse proxy
- Configure environment variables and secrets
- Set up CI/CD pipelines
- Manage the Hyperview mobile build process (EAS)

## Relevant Files

| File | Purpose |
|------|---------|
| `docker-compose.yml` | Service orchestration (db, web, nginx, redis, worker) |
| `Dockerfile` | Python 3.13 + Tailwind CSS CLI build |
| `nginx.Dockerfile` | Nginx build |
| `nginx.conf` | Reverse proxy configuration |
| `.env.example` | Environment variable template |
| `.dockerignore` | Docker build exclusions |
| `pyproject.toml` | uv config + taskipy scripts |

## Infrastructure Architecture

```
docker compose up -d
├── db (postgres:15)      → :5432, healthcheck: pg_isready
├── web (Django)          → :8000, depends_on: db (healthy)
├── nginx                 → :8080→80, proxy_pass → web:8000
├── redis (redis:6.2)     → Celery broker
└── worker (Celery)       → depends_on: db, redis
```

## Workflow

1. Build: `docker compose up -d --build`
2. Monitor: `docker compose logs -f web`
3. Deploy: `docker compose up -d` (with production `.env`)
4. Update: pull changes, `docker compose up -d --build`

## Key Commands

```bash
# Start all services
docker compose up -d --build

# Stop all services
docker compose down

# View logs
docker compose logs -f [service]

# Shell access
docker compose exec web bash
docker compose exec db psql -U postgres

# Rebuild single service
docker compose up -d --build web

# Clean restart
docker compose down -v && docker compose up -d --build
```

## Nginx Configuration

- Listens on port 80 (mapped to host 8080)
- Proxies to `web:8000`
- Serves `/static/` from `/code/staticfiles`
- Serves `/media/` from `/code/media`
- Custom error pages from `/etc/nginx/errors`

## Environment Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `SECRET_KEY` | Django secret | Required |
| `DEBUG` | Debug mode | `True` |
| `ALLOWED_HOSTS` | Allowed hosts | `*` |
| `DB_ENGINE` | `sqlite3` or `postgresql` | `sqlite3` |
| `DB_NAME` | PostgreSQL database | Required |
| `DB_USERNAME` | PostgreSQL user | Required |
| `DB_PASS` | PostgreSQL password | Required |
| `DB_HOST` | PostgreSQL host | `db` |
| `HYPERVIEW_BASE_URL` | HXML base URL | Auto-detected |
| `CELERY_BROKER_URL` | Redis URL | `redis://redis:6379/0` |

## Quality Checks

- `.env` never committed (in `.gitignore`)
- `.env.example` updated with new variables
- All services healthy: `docker compose ps`
- Nginx config valid: `docker compose exec nginx nginx -t`
- Database healthcheck passing
- No secrets in Dockerfile or docker-compose.yml
