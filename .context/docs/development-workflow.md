---
type: doc
name: development-workflow
description: Day-to-day engineering processes, branching, and contribution guidelines
category: workflow
generated: 2026-05-25
status: filled
scaffoldVersion: "2.0.0"
---

## Development Workflow

This project uses Docker Compose for all development and testing. All Django commands
must run inside the container via `docker compose exec`.

### Branching & Releases

- **Branching**: Feature branches from `main`, merge via PR.
- **No formal release process**: Current phase is prototype/demo.
- **No version tags**: Version is tracked in `AboutView` context (`app_version: "1.0.0"`).
- **Mobile builds**: Triggered manually via `eas build` from the Hyperview demo client.

### Local Development

**Setup:**
```bash
# Copy environment
cp .env.example .env

# Build and start all services
docker compose up -d --build

# Run migrations
docker compose exec web python manage.py migrate

# Create superuser
docker compose exec web python manage.py createsuperuser
```

**Daily commands:**
```bash
# View logs
docker compose logs -f web

# Django management
docker compose exec web python manage.py check
docker compose exec web python manage.py shell
docker compose exec web python manage.py makemigrations
docker compose exec web python manage.py migrate

# Run tests
docker compose exec web python manage.py test hv
docker compose exec web python manage.py test hv.tests.HyperviewViewsTestCase

# Tailwind CSS
docker compose exec web tailwindcss -i /code/core/static/core/css/input.css -o /code/core/static/core/css/output.css --minify

# Collect static files (production)
docker compose exec web python manage.py collectstatic --noinput
```

**Adding dependencies (ALWAYS use uv):**
```bash
uv add "pacote>=versao"
uv lock
uv export --format requirements.txt --output requirements.txt --without-hashes
docker compose up -d --build
```

**Taskipy shortcuts (from `pyproject.toml`):**
```bash
uv run task css-build   # Build Tailwind CSS
uv run task css-watch   # Watch Tailwind CSS
uv run task css-dev     # Dev CSS build
```

### Code Review Expectations

- **Tests required** for new views and endpoints (use `reverse()` for URLs).
- **Follow Django CBV patterns**: `TemplateView` for read-only, `View` with `get()`/`post()`
  for forms. Avoid `if request.method == "POST"` in function views.
- **HXML rules**: `<body scroll="false">` for screens with `<list>`, proper namespaces in
  `<doc>`, `href-style` for tappable wrappers.
- **CSRF exemption**: Only for mobile POST endpoints. Document why in code comments.
- **Template includes**: Each reusable component needs two files (`_styles.xml` + `.xml`)
  due to Django's include-with-blocks limitation.
- **No hardcoded URLs in tests**: Use `reverse("hv:view_name")`.
- **Never edit `requirements.txt` directly**: Always use `uv add` → `uv lock` → `uv export`.

### Onboarding Tasks

1. Read `AGENTS.md` for full project conventions.
2. Read `docs/HYPERVIEW.md` for Hyperview-specific patterns and pitfalls.
3. Read `.docs/DJANGO-SETUP.md` for Django setup conventions.
4. Run the test suite: `docker compose exec web python manage.py test hv`
5. Explore a simple read-only view first (e.g., `AboutView` in `hv/views.py:260`).
6. Set up the Hyperview mobile demo: `cd /mnt/c/workspaces/PythonProjects/hyperview/demo && yarn install`

## Related Resources

- [Testing Strategy](testing-strategy.md)
- [Tooling Guide](tooling.md)
- [AGENTS.md](../../AGENTS.md)
