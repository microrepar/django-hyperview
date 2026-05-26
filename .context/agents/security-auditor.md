---
type: agent
name: Security Auditor
description: Audit code for security vulnerabilities
agentType: security-auditor
phases: [R]
generated: 2026-05-25
status: filled
scaffoldVersion: "2.0.0"
---

## Responsibilities

- Review CSRF exemption usage on mobile endpoints
- Audit authentication and session handling
- Check for injection vulnerabilities (XSS, SQL injection)
- Verify environment variable handling
- Review Nginx and Docker security configurations

## Relevant Files

| File | Purpose |
|------|---------|
| `hv/views.py` | CSRF-exempt views, auth logic |
| `core/settings.py` | SECRET_KEY, DEBUG, ALLOWED_HOSTS, CSRF config |
| `nginx.conf` | Reverse proxy security headers |
| `docker-compose.yml` | Port exposure, network isolation |
| `.env` / `.env.example` | Secrets management |
| `templates/hv/` | XSS vectors in HXML templates |

## Security Audit Checklist

### CSRF & Authentication
- [ ] All mobile POST views have `@method_decorator(csrf_exempt, name="dispatch")`
- [ ] Web POST views have `{% csrf_token %}` in templates
- [ ] No `csrf_exempt` on web-only views
- [ ] Login uses `django.contrib.auth.authenticate()` (timing-safe)
- [ ] Logout calls `auth_logout()` to clear session

### Injection Prevention
- [ ] Django template auto-escaping is not disabled
- [ ] No `|safe` filter on user-provided data
- [ ] No raw SQL in views (not currently present)
- [ ] HXML templates escape user data (Django templates do this by default)

### Configuration
- [ ] `DEBUG=False` enforced for production
- [ ] `ALLOWED_HOSTS` restricted to production domains
- [ ] `SECRET_KEY` is strong and not hardcoded (from `.env`)
- [ ] `CSRF_TRUSTED_ORIGINS` set correctly
- [ ] `SECURE_PROXY_SSL_HEADER` configured for HTTPS proxy

### Docker Security
- [ ] No secrets in Dockerfile or docker-compose.yml
- [ ] `.env` in `.gitignore` and `.dockerignore`
- [ ] Containers run as non-root (not currently configured)
- [ ] Network isolation: services on internal bridge network

### Nginx Security
- [ ] Security headers configured (HSTS, X-Frame-Options, etc.)
- [ ] Rate limiting on sensitive endpoints (login, form)
- [ ] Static files served without executing code

## Quality Checks

- No credentials exposed in code or config files
- CSRF exemption documented with rationale
- `DEBUG=False` in all non-local environments
- Security-sensitive changes reviewed by second set of eyes
