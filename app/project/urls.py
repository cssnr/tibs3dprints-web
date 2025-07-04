from django.conf import settings
from django.conf.urls import include
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, re_path

from . import views


urlpatterns = [
    path("", include("home.urls")),
    path("api/", include("api.urls")),
    path("oauth/", include("oauth.urls")),
    re_path(r"^tiktok.*\.txt$", views.tiktok_verify_view),
    path(".well-known/assetlinks.json", views.dal_view),
    path("flush-cache/", views.flush_cache_view, name="flush-cache"),
    path("app-health-check/", views.health_check_view, name="health-check"),
    # path("flower/", RedirectView.as_view(url="/flower/"), name="flower"),
    # path("redis/", RedirectView.as_view(url="/redis/"), name="redis"),
    # path("phpmyadmin/", RedirectView.as_view(url="/phpmyadmin/"), name="phpmyadmin"),
    path("preview/poll/", views.poll_preview_view, name="preview-poll"),
    path("admin/", admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler400 = "project.views.handler400_view"
handler403 = "project.views.handler403_view"
handler404 = "project.views.handler404_view"
handler500 = "project.views.handler500_view"

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [path("debug/", include(debug_toolbar.urls))] + urlpatterns
