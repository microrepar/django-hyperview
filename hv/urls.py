"""URL patterns do app Hyperview."""
from django.urls import path
from .views import (
    AboutView,
    DeleteView,
    ListItemsView,
    DetailView,
    FormView,
    HomeView,
    IndexView,
    ListView,
    LoginView,
    LogoutView,
    ProfileEditView,
    ProfileView,
    SettingsView,
    ShareView,
)

app_name = "hv"

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("home/", HomeView.as_view(), name="home"),
    path("list/", ListView.as_view(), name="list"),
    path("list/items/", ListItemsView.as_view(), name="list_items"),
    path("detail/<int:item_id>/", DetailView.as_view(), name="detail"),
    path("form/", FormView.as_view(), name="form"),
    path("login/", LoginView.as_view(), name="login"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("settings/", SettingsView.as_view(), name="settings"),
    path("about/", AboutView.as_view(), name="about"),
    path("detail/<int:item_id>/share/", ShareView.as_view(), name="detail_share"),
    path("detail/<int:item_id>/delete/", DeleteView.as_view(), name="detail_delete"),
    path("profile/edit/", ProfileEditView.as_view(), name="profile_edit"),
    path("logout/", LogoutView.as_view(), name="logout"),
]
