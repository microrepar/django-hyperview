---
type: skill
name: Test Generation
description: Generate tests for Django Hyperview views and endpoints. Use when adding new views, covering untested endpoints, or adding regression tests for bug fixes.
skillSlug: test-generation
phases: [P, E, V]
generated: 2026-05-25
status: filled
scaffoldVersion: "2.0.0"
---

## Workflow

1. Identify the view to test and its URL name (from `hv/urls.py`)
2. Determine test type: GET-only, GET+POST, or parameterized
3. Add test method(s) to `HyperviewViewsTestCase` in `hv/tests.py`
4. Follow existing test patterns exactly
5. Run: `docker compose exec web python manage.py test hv`

## Test Templates

### Read-only view (TemplateView)
```python
def test_<name>(self):
    url = reverse("hv:<name>")
    response = self.client.get(url)
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response["Content-Type"], "application/xml")
```

### Parameterized view
```python
def test_detail(self):
    url = reverse("hv:detail", kwargs={"item_id": 1})
    response = self.client.get(url)
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response["Content-Type"], "application/xml")
```

### Form view (GET + valid POST + invalid POST)
```python
def test_<name>_get(self):
    url = reverse("hv:<name>")
    response = self.client.get(url)
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response["Content-Type"], "application/xml")

def test_<name>_post_valid(self):
    url = reverse("hv:<name>")
    response = self.client.post(url, {<valid_data>})
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, "<success_message>")

def test_<name>_post_invalid(self):
    url = reverse("hv:<name>")
    response = self.client.post(url, {<invalid_data>})
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, "<error_message>")
```

## Priority Test Coverage

| Priority | Views Needing Tests |
|----------|-------------------|
| High | `test_login_post_valid`, `test_login_post_invalid` |
| High | `test_delete_post` |
| High | `test_profile_edit_post_valid`, `test_profile_edit_post_invalid` |
| High | `test_logout_post` |
| Medium | `test_share`, `test_delete_get`, `test_profile_edit_get`, `test_logout_get` |
| Low | `test_list_items` (fragment endpoint, covered by `test_list`) |

## Quality Bar

- All new tests use `reverse("hv:name")`
- Content-Type assertion present on every HXML test
- Form tests cover both valid and invalid submissions
- Test method name follows `test_<snake_case>` convention
- Added to existing `HyperviewViewsTestCase` class
- `docker compose exec web python manage.py test hv` passes
