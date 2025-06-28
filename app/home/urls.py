from django.urls import path, re_path

from . import views


app_name = "home"

urlpatterns = [
    path("", views.home_view, name="index"),
    re_path(r"^app/.*$", views.app_view, name="app"),
    path("beta/", views.beta_view, name="beta"),
    # path("verify/<str:base64_str>/", views.verify_view, name="verify"),
]
