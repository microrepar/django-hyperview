---
type: doc
name: testing-strategy
description: Testing approach, frameworks, and conventions
category: testing
generated: 2026-05-25
status: filled
scaffoldVersion: "2.0.0"
---

## Testing Strategy

### Framework

- **Django TestCase** (`django.test.TestCase`): Standard Django test framework.
- **Test runner**: `python manage.py test` (via Docker: `docker compose exec web python manage.py test hv`).
- **No pytest**: Uses Django's built-in unittest-based runner.

### Test Location

All Hyperview tests live in `hv/tests.py`. One test class: `HyperviewViewsTestCase`.

### Current Test Coverage

| Test | View | Method | What it checks |
|------|------|--------|---------------|
| `test_index` | `IndexView` | GET | Status 200, Content-Type application/xml |
| `test_home` | `HomeView` | GET | Status 200, Content-Type application/xml |
| `test_list` | `ListView` | GET | Status 200, Content-Type application/xml |
| `test_detail` | `DetailView` | GET | Status 200, Content-Type application/xml |
| `test_form_get` | `FormView` | GET | Status 200, Content-Type application/xml |
| `test_form_post_valid` | `FormView` | POST | Status 200, contains "sucesso" |
| `test_form_post_invalid` | `FormView` | POST | Status 200, contains "obrigatorio" |
| `test_login_get` | `LoginView` | GET | Status 200, Content-Type application/xml |
| `test_about` | `AboutView` | GET | Status 200, Content-Type application/xml |
| `test_profile` | `ProfileView` | GET | Status 200, Content-Type application/xml |
| `test_settings` | `SettingsView` | GET | Status 200, Content-Type application/xml |

**Total: 11 tests. Coverage: 11 of 14 views tested (79%).**

### Views NOT tested

- `ListItemsView` — fragment endpoint (tested indirectly via `test_list`)
- `ShareView` — missing test
- `DeleteView` — missing test (GET + POST)
- `ProfileEditView` — missing test (GET + POST)
- `LogoutView` — missing test (GET + POST)

### Testing Conventions

1. **Always use `reverse()`**: `url = reverse("hv:view_name")` — never hardcode URLs.
2. **Check Content-Type**: All HXML views must return `application/xml`.
3. **Test both GET and POST** for form views: Valid and invalid submissions.
4. **Use `assertContains`**: For checking response content (success messages, error messages).
5. **Run inside Docker**: `docker compose exec web python manage.py test hv`

### Test Patterns

**Read-only view (TemplateView):**
```python
def test_about(self):
    url = reverse("hv:about")
    response = self.client.get(url)
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response["Content-Type"], "application/xml")
```

**Form view (GET + POST):**
```python
def test_form_post_valid(self):
    url = reverse("hv:form")
    response = self.client.post(url, {
        "name": "Teste", "email": "teste@email.com", "phone": "12345",
    })
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, "sucesso")
```

### Gaps & Recommendations

- **Missing view tests**: `ShareView`, `DeleteView`, `ProfileEditView`, `LogoutView`
- **No integration tests**: All tests are unit-level HTTP request/response.
- **No template content assertions**: Tests don't validate HXML structure (correct elements, attributes).
- **No auth tests**: Login POST with valid/invalid credentials not tested.
- **No mobile-specific tests**: Infinite scroll behavior, fragment endpoint, pull-to-refresh.
- **No error case tests**: Malformed URLs, non-existent items, invalid HTTP methods.

## Related Resources

- [Development Workflow](development-workflow.md)
- [Tooling Guide](tooling.md)
- [hv/tests.py](../../hv/tests.py) — Current test suite
