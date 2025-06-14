from django.contrib import admin

from .models import BetaUser, Choice, Poll, TikTokUser, Vote


admin.site.site_header = "Tibs3DPrints Administration"


admin.site.register(Choice)
admin.site.register(Poll)


@admin.action(description="Add selected to Beta Test")
def mark_as_added(modeladmin, request, queryset):
    queryset.update(added=True)


@admin.register(TikTokUser)
class TikTokUserAdmin(admin.ModelAdmin):
    list_display = ("display_name", "updated_at", "created_at")
    list_filter = ("display_name",)
    search_fields = ("display_name",)
    ordering = ("display_name",)
    readonly_fields = (
        "display_name",
        "authorization",
        "open_id",
        "avatar_url",
        "updated_at",
        "created_at",
        "access_token",
        "refresh_token",
        "expires_in",
    )

    # def has_delete_permission(self, request, obj=None):
    #     return False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(BetaUser)
class BetaUserAdmin(admin.ModelAdmin):
    list_display = (
        "added",
        "email",
        "name",
        "created_at",
    )
    list_filter = (
        "added",
        "email",
        "name",
    )
    search_fields = (
        "email",
        "name",
    )
    list_display_links = ("email",)
    ordering = ("-created_at",)
    actions = [mark_as_added]

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False
