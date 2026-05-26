---
type: skill
name: Security Audit
description: Audit Django Hyperview code for security vulnerabilities. Use when reviewing CSRF, auth, injection vectors, or configuration security before production deployment.
skillSlug: security-audit
phases: [R, V]
generated: 2026-05-25
status: filled
scaffoldVersion: "2.0.0"
---

## Workflow

1. Audit CSRF exemption usage: are all mobile POST views properly exempted? Are any web views incorrectly exempted?
2. Check authentication: login/logout flows, session handling
3. Scan for injection vectors: XSS in templates, SQL injection
4. Review configuration: DEBUG, ALLOWED_HOSTS, SECRET_KEY, CSRF_TRUSTED_ORIGINS
5. Check Docker security: exposed ports, secrets management, container privileges
6. Review Nginx: security headers, rate limiting, static file serving
7. Document findings and recommend fixes

## Audit Checklist

### CSRF (check `hv/views.py`)
```bash
# Find csrf_exempt usage
grep -n "csrf_exempt" hv/views.py
```
Expected: 6 views (FormView, LoginView, ShareView, DeleteView, ProfileEditView, LogoutView)
- [ ] All have `@method_decorator(csrf_exempt, name="dispatch")`
- [ ] Each has a comment explaining why (mobile POST, no cookies)
- [ ] No csrf_exempt on read-only views (IndexView, HomeView, etc.)

### Authentication
- [ ] Login uses `django.contrib.auth.authenticate()` — constant-time comparison
- [ ] Logout clears session via `auth_logout()`
- [ ] No hardcoded credentials

### Injection
- [ ] Django auto-escaping active (check for `|safe` filter on user data)
- [ ] No raw SQL queries
- [ ] Template variables properly escaped in HXML

### Configuration
```bash
grep -E "DEBUG|SECRET_KEY|ALLOWED_HOSTS" core/settings.py
```
- [ ] `DEBUG` from env var, defaults to `True` (safe for dev)
- [ ] `SECRET_KEY` from `.env`, not hardcoded
- [ ] `ALLOWED_HOSTS` restricted in production

### Secrets
```bash
grep -r "SECRET_KEY\|password\|token" --include="*.py" --include="*.yml" --include="*.conf" .
```
- [ ] No secrets in committed files
- [ ] `.env` in `.gitignore`

## Quality Bar

- All audit items checked
- Findings documented with severity and fix recommendations
- Critical issues addressed before production deploy
