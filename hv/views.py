
"""Views que servem HXML (Hyperview XML) para o app mobile.

Usa Class-Based Views conforme recomendação da documentação Django:
views com múltiplos métodos HTTP (GET+POST) implementam get()/post()
em vez de if request.method == "POST".

csrf_exempt é usado nos endpoints que recebem POST do app mobile,
que não usa cookies de sessão. A documentação Django recomenda isso
para "API endpoints that use alternative authentication methods".
"""
from datetime import date

from django.conf import settings
from django.contrib.auth import authenticate
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import TemplateView


def _base_url(request: HttpRequest) -> str:
    """URL base para links HXML. Usa HYPERVIEW_BASE_URL se configurado."""
    base = getattr(settings, "HYPERVIEW_BASE_URL", None)
    if base:
        return base.rstrip("/")
    scheme = "https" if request.is_secure() else "http"
    return f"{scheme}://{request.get_host()}"


class IndexView(TemplateView):
    """Entrypoint: navigator principal com tabs."""
    template_name = "hv/index.xml"
    content_type = "application/xml"

    def get_context_data(self, **kwargs):
        return {"base_url": _base_url(self.request)}


class HomeView(TemplateView):
    """Dashboard com cards de navegacao e atualizacoes."""
    template_name = "hv/home.xml"
    content_type = "application/xml"

    def get_context_data(self, **kwargs):
        request = self.request
        return {
            "base_url": _base_url(request),
            "hoje": timezone.localdate(),
            "user": request.user if request.user.is_authenticated else None,
            "updates": [
                {"id": 1, "title": "Bem-vindo ao Hyperview!",
                 "description": "Explore as funcionalidades do app server-driven."},
                {"id": 2, "title": "Novo formulario disponivel",
                 "description": "Teste o envio de dados com validacao server-side."},
                {"id": 3, "title": "Listas com infinite scroll",
                 "description": "Listas nativas com pull-to-refresh e paginacao."},
            ],
        }


class ListView(TemplateView):
    """Lista com pull-to-refresh e infinite scroll."""
    template_name = "hv/list.xml"
    content_type = "application/xml"

    def get_context_data(self, **kwargs):
        request = self.request
        page = int(request.GET.get("page", 1))
        per_page = 20
        total_items = 50

        all_items = [
            {"id": i, "name": f"Item {i}",
             "subtitle": f"Descricao do item {i}",
             "category": "Grupo A" if i % 3 == 0 else ("Grupo B" if i % 3 == 1 else "Grupo C"),
             "badge": "Novo" if i <= 3 else None,
             "avatar_url": None}
            for i in range(1, total_items + 1)
        ]

        start = (page - 1) * per_page
        end = start + per_page
        page_items = all_items[start:end]

        return {
            "base_url": _base_url(request),
            "items": page_items,
            "has_next": end < total_items,
            "next_page": page + 1 if end < total_items else None,
            "page": page,
        }


class DetailView(TemplateView):
    """Detalhes de um item."""
    template_name = "hv/detail.xml"
    content_type = "application/xml"

    def get_context_data(self, **kwargs):
        item_id = self.kwargs["item_id"]
        item = {
            "id": item_id, "name": f"Item {item_id}",
            "description": f"Detalhes completos do item {item_id}.",
            "category": "Grupo A" if item_id % 3 == 0 else ("Grupo B" if item_id % 3 == 1 else "Grupo C"),
            "avatar_url": None,
            "fields": [
                {"label": "ID", "value": str(item_id)},
                {"label": "Status", "value": "Ativo"},
                {"label": "Criado em", "value": timezone.now().strftime("%d/%m/%Y %H:%M")},
                {"label": "Prioridade", "value": "Alta" if item_id % 2 == 0 else "Media"},
            ],
        }
        related = [
            {"id": item_id + 1, "name": f"Item {item_id + 1}"},
            {"id": item_id + 2, "name": f"Item {item_id + 2}"},
        ]
        return {
            "base_url": _base_url(self.request),
            "item": item,
            "related_items": related,
        }


@method_decorator(csrf_exempt, name="dispatch")
class FormView(View):
    """Formulario com validacao server-side (GET + POST)."""

    def get(self, request, *args, **kwargs):
        return self._render(request)

    def post(self, request, *args, **kwargs):
        return self._render(request, is_post=True)

    def _render(self, request: HttpRequest, is_post: bool = False):
        base_url = _base_url(request)
        categories = [
            {"value": "tech", "label": "Tecnologia", "selected": False},
            {"value": "business", "label": "Negocios", "selected": False},
            {"value": "design", "label": "Design", "selected": False},
            {"value": "marketing", "label": "Marketing", "selected": False},
        ]

        context: dict = {
            "base_url": base_url, "form_data": {}, "errors": {},
            "categories": categories, "success_message": "", "error_message": "",
        }

        if is_post:
            name = request.POST.get("name", "").strip()
            email = request.POST.get("email", "").strip()
            phone = request.POST.get("phone", "").strip()
            category = request.POST.get("category", "").strip()

            errors = {}
            if not name:
                errors["name"] = "Nome eh obrigatorio."
            if not email:
                errors["email"] = "Email eh obrigatorio."
            elif "@" not in email:
                errors["email"] = "Email invalido."
            if not phone:
                errors["phone"] = "Telefone eh obrigatorio."

            context["form_data"] = {"name": name, "email": email, "phone": phone}
            for cat in categories:
                cat["selected"] = (cat["value"] == category)
            context["errors"] = errors
            if not errors:
                context["success_message"] = "Formulario enviado com sucesso!"

        return render(request, "hv/form.xml", context, content_type="application/xml")


@method_decorator(csrf_exempt, name="dispatch")
class LoginView(View):
    """Login (GET + POST)."""

    def get(self, request, *args, **kwargs):
        return render(request, "hv/login.xml", {
            "base_url": _base_url(request), "error_message": "",
        }, content_type="application/xml")

    def post(self, request, *args, **kwargs):
        username = request.POST.get("username", "")
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        error = "" if user is not None else "Usuario ou senha invalidos."
        return render(request, "hv/login.xml", {
            "base_url": _base_url(request), "error_message": error,
        }, content_type="application/xml")


class ProfileView(TemplateView):
    """Perfil do usuario."""
    template_name = "hv/profile.xml"
    content_type = "application/xml"

    def get_context_data(self, **kwargs):
        request = self.request
        return {
            "base_url": _base_url(request),
            "user": request.user if request.user.is_authenticated else None,
            "stats": {"items_count": 42, "followers": 128, "following": 56},
        }


class SettingsView(TemplateView):
    """Configuracoes."""
    template_name = "hv/settings.xml"
    content_type = "application/xml"

    def get_context_data(self, **kwargs):
        return {"base_url": _base_url(self.request)}


class AboutView(TemplateView):
    """Sobre o app."""
    template_name = "hv/about.xml"
    content_type = "application/xml"

    def get_context_data(self, **kwargs):
        return {
            "base_url": _base_url(self.request),
            "app_name": "Django Hyperview",
            "app_version": "1.0.0",
            "year": date.today().year,
        }
