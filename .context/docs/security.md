---
type: doc
name: security
description: Security considerations, authentication, and data protection
category: security
generated: 2026-05-25
status: filled
scaffoldVersion: "2.0.0"
---

## Security

### Authentication

- **Django session auth**: Used for web (`/`, `/admin/`). Standard cookie-based sessions.
- **Mobile auth**: `LoginView` (`hv/views.py:217`) accepts POST with `username`/`password`,
  calls `django.contrib.auth.authenticate()`. Session cookie is set on successful login.
- **Logout**: `LogoutView` (`hv/views.py:367`) calls `django.contrib.auth.logout()` and
  clears the session.
- **Custom User model**: `accounts.User` extends `AbstractUser` (`accounts/models.py:4`).

### CSRF Protection

- **Web endpoints**: Standard Django CSRF middleware protection. All web forms use
  `{% csrf_token %}`.
- **Mobile POST endpoints**: 5 views use `@method_decorator(csrf_exempt, name="dispatch")`:
  - `FormView` (`hv/views.py:166`)
  - `LoginView` (`hv/views.py:217`)
  - `ShareView` (`hv/views.py:276`)
  - `DeleteView` (`hv/views.py:302`)
  - `ProfileEditView` (`hv/views.py:328`)
  - `LogoutView` (`hv/views.py:367`)
- **Rationale**: Mobile apps don't use cookies for authentication and can't obtain CSRF tokens.
  Django docs recommend `csrf_exempt` for API endpoints with alternative authentication.
  This is documented inline in `hv/views.py`.

### Environment & Secrets

- **`.env` file**: Contains `SECRET_KEY`, `DB_NAME`, `DB_USERNAME`, `DB_PASS`, etc.
  Never committed to git (in `.gitignore`).
- **`.env.example`**: Template with placeholder values, safe to commit.
- **`DEBUG`**: Controlled by `DEBUG` env var. Should be `False` in production.
- **`ALLOWED_HOSTS`**: Configured via env var, defaults to `*` (development only).
- **`CSRF_TRUSTED_ORIGINS`**: Configured for localhost URLs. Must be updated for production
  domains.

### HTTPS / Proxy

- **`SECURE_PROXY_SSL_HEADER`**: Set to `('HTTP_X_FORWARDED_PROTO', 'https')` for Cloudflare
  or other SSL-terminating proxies.
- **Nginx**: Terminates SSL in production (not configured in this prototype).
- **`HYPERVIEW_BASE_URL`**: Controls the base URL in HXML hyperlinks. Should be set to the
  production domain in deployment.

### Data Protection

- **No sensitive data in HXML templates**: All current data is hardcoded/generated demo content.
- **User model**: Custom `accounts.User` with standard Django password hashing (PBKDF2 by default).
- **Soft delete**: `SoftDeleteMixin` (`core/base_models/mixins.py:13`) provides logical deletion
  without data loss. Not currently used by any production model.
- **Media uploads**: Served via Nginx at `/media/`. No auth gating currently.

### Security Checklist

- [ ] Set `DEBUG=False` in production `.env`
- [ ] Restrict `ALLOWED_HOSTS` to production domains
- [ ] Set `HYPERVIEW_BASE_URL` to production domain
- [ ] Update `CSRF_TRUSTED_ORIGINS` for production
- [ ] Rotate `SECRET_KEY` for production
- [ ] Use strong `DB_PASS` in production `.env`
- [ ] Enable HTTPS on Nginx with valid certificates
- [ ] Consider rate limiting on login endpoint
- [ ] Add `SECURE_HSTS_SECONDS`, `SECURE_SSL_REDIRECT` for production
- [ ] Audit `csrf_exempt` views for production use

## Related Resources

- [Architecture Notes](architecture.md)
- [Development Workflow](development-workflow.md)
- [AGENTS.md](../../AGENTS.md)
