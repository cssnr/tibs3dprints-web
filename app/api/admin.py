from django.contrib import admin

from .models import TikTokUser


@admin.register(TikTokUser)
class TikTokUserAdmin(admin.ModelAdmin):
    list_display = ("display_name", "open_id")
    list_filter = ("display_name",)
    search_fields = ("display_name",)
    ordering = ("display_name",)
    readonly_fields = (
        "display_name",
        "open_id",
        "avatar_url",
        "access_token",
        "refresh_token",
        "expires_in",
    )

    # def has_delete_permission(self, request, obj=None):
    #     return False

    # def has_add_permission(self, request, obj=None):
    #     return False
