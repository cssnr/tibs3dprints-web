from django.urls import path, re_path

from api import views


app_name = "api"

urlpatterns = [
    path("", views.api_view, name="index"),
    re_path(r"^auth/?$", views.auth_view, name="auth"),
]
