"""URL patterns do app Hyperview."""
from django.urls import path
from .views import (
    AboutView,
    DetailView,
    FormView,
    HomeView,
    IndexView,
    ListView,
    LoginView,
    ProfileView,
    SettingsView,
)

app_name = "hv"

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("home/", HomeView.as_view(), name="home"),
    path("list/", ListView.as_view(), name="list"),
    path("detail/<int:item_id>/", DetailView.as_view(), name="detail"),
    path("form/", FormView.as_view(), name="form"),
    path("login/", LoginView.as_view(), name="login"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("settings/", SettingsView.as_view(), name="settings"),
    path("about/", AboutView.as_view(), name="about"),
]
