from django.urls import path, re_path

from api import views


app_name = "api"

urlpatterns = [
    path("", views.api_view, name="index"),
    path("poll/current/", views.poll_current_view, name="poll-current"),
    path("poll/vote/", views.poll_vote_view, name="poll-vote"),
    re_path(r"^auth/?$", views.auth_view, name="auth"),
]
