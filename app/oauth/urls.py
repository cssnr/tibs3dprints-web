from django.urls import path

from . import views


app_name = "oauth"

urlpatterns = [
    path("", views.oauth_start, name="login"),
    path("logout/", views.oauth_logout, name="logout"),
    path("callback/", views.oauth_callback, name="callback"),
]
