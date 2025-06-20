from django.urls import path, re_path

from api import views


app_name = "api"

urlpatterns = [
    path("", views.api_view, name="index"),
    path("poll/current/", views.poll_current_view, name="poll-current"),
    path("poll/vote/", views.poll_vote_view, name="poll-vote"),
    path("email/edit/", views.email_edit_view, name="email-edit"),
    path("email/verify/", views.email_verify_view, name="email-verify"),
    re_path(r"^auth/?$", views.auth_view, name="auth"),
]
