from django.urls import path

from . import views


app_name = "home"

urlpatterns = [
    path("", views.home_view, name="index"),
    path("news/", views.news_view, name="news"),
    path("message/", views.message_view, name="message"),
    path("contact/", views.contact_view, name="contact"),
    path("contact/<slug:view>/<uuid:uuid>", views.contact_html_view, name="contact_html"),
]
