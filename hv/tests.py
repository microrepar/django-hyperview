"""Testes para os endpoints Hyperview.

Usa reverse() para resolver URLs conforme recomendacao da
documentacao Django, em vez de hardcoding os paths.
"""
from django.test import TestCase
from django.urls import reverse


class HyperviewViewsTestCase(TestCase):
    """Testes para todas as views HXML."""

    def test_index(self):
        url = reverse("hv:index")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/xml")

    def test_home(self):
        url = reverse("hv:home")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/xml")

    def test_list(self):
        url = reverse("hv:list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/xml")

    def test_detail(self):
        url = reverse("hv:detail", kwargs={"item_id": 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/xml")

    def test_form_get(self):
        url = reverse("hv:form")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/xml")

    def test_form_post_valid(self):
        url = reverse("hv:form")
        response = self.client.post(url, {
            "name": "Teste", "email": "teste@email.com", "phone": "12345",
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "sucesso")

    def test_form_post_invalid(self):
        url = reverse("hv:form")
        response = self.client.post(url, {"name": "", "email": "", "phone": ""})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "obrigatorio")

    def test_login_get(self):
        url = reverse("hv:login")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/xml")

    def test_about(self):
        url = reverse("hv:about")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/xml")

    def test_profile(self):
        url = reverse("hv:profile")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/xml")

    def test_settings(self):
        url = reverse("hv:settings")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/xml")
