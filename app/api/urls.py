from django.urls import path, re_path

from api import views


app_name = "api"

urlpatterns = [
    path("", views.api_view, name="index"),
    path("poll/current/", views.poll_current_view, name="poll-current"),
    path("poll/vote/", views.poll_vote_view, name="poll-vote"),
    path("user/current/", views.user_current_view, name="user-current"),
    path("user/edit/", views.user_edit_view, name="user-edit"),
    path("auth/start/", views.auth_start_view, name="auth-start"),
    path("auth/login/", views.auth_login_view, name="auth-login"),
    # path("auth/register/", views.auth_register_view, name="auth-register"),
    # path("email/check/", views.email_check_view, name="email-check"),
    # path("email/edit/", views.email_edit_view, name="email-edit"),
    # path("email/verify/", views.email_verify_view, name="email-verify"),
    # re_path(r"^auth/?$", views.auth_view, name="auth"),
]
