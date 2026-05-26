---
type: agent
name: Test Writer
description: Write and maintain tests for the Django Hyperview application
agentType: test-writer
phases: [P, E, V]
generated: 2026-05-25
status: filled
scaffoldVersion: "2.0.0"
---

## Responsibilities

- Write tests for new Hyperview views and endpoints
- Add regression tests for bug fixes
- Fill gaps in test coverage (currently 11/14 views tested)
- Ensure tests follow project conventions

## Relevant Files

| File | Purpose |
|------|---------|
| `hv/tests.py` | All Hyperview tests (`HyperviewViewsTestCase`) |
| `hv/views.py` | Reference for what to test |
| `hv/urls.py` | URL names for `reverse()` |

## Current Test Coverage Gaps

| Missing Test | View Type | Priority |
|-------------|-----------|----------|
| `test_share` | `ShareView` (GET) | Medium |
| `test_delete_get` | `DeleteView` (GET) | Medium |
| `test_delete_post` | `DeleteView` (POST) | High |
| `test_profile_edit_get` | `ProfileEditView` (GET) | Medium |
| `test_profile_edit_post` | `ProfileEditView` (POST) | High |
| `test_logout_get` | `LogoutView` (GET) | Medium |
| `test_logout_post` | `LogoutView` (POST) | High |
| `test_login_post_valid` | `LoginView` (POST) | High |
| `test_login_post_invalid` | `LoginView` (POST) | High |
| `test_list_items` | `ListItemsView` (GET) | Low |

## Test Patterns to Follow

**Read-only view:**
```python
def test_about(self):
    url = reverse("hv:about")
    response = self.client.get(url)
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response["Content-Type"], "application/xml")
```

**Form view (valid POST):**
```python
def test_form_post_valid(self):
    url = reverse("hv:form")
    response = self.client.post(url, {
        "name": "Teste", "email": "teste@email.com", "phone": "12345",
    })
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, "sucesso")
```

**Parameterized view:**
```python
def test_detail(self):
    url = reverse("hv:detail", kwargs={"item_id": 1})
    response = self.client.get(url)
    self.assertEqual(response.status_code, 200)
```

## Quality Checks

- All tests use `reverse()` — no hardcoded URLs
- Content-Type assertion on every HXML test
- Form views tested with both valid and invalid data
- Test class name matches convention: `HyperviewViewsTestCase`
- Tests run successfully: `docker compose exec web python manage.py test hv`
- New tests added to existing `HyperviewViewsTestCase` class
