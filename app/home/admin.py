from django.contrib import admin

from .models import BetaUser, Choice, Poll, TikTokUser, Vote


admin.site.site_header = "Tibs3DPrints Administration"


class ChoiceInline(admin.TabularInline):
    model = Choice
    # extra = 1
    readonly_fields = ("votes",)

    def get_extra(self, request, obj=None, **kwargs):
        if obj is None:
            return 2
        count = obj.choice_set.count()
        if count >= 2:
            return 0
        return 2 - count


@admin.action(description="Add selected to Beta Test")
def mark_as_added(modeladmin, request, queryset):
    queryset.update(added=True)


@admin.register(TikTokUser)
class TikTokUserAdmin(admin.ModelAdmin):
    list_display = ("display_name", "email_address", "created_at")
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

    def has_delete_permission(self, request, obj=None):
        return False

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


@admin.register(Poll)
class PollAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "start_at",
        "end_at",
    )
    search_fields = ("title",)

    inlines = [ChoiceInline]


@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "poll",
        "votes",
    )
    list_filter = ("poll",)
    search_fields = ("name",)
    readonly_fields = ("votes",)


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "poll",
        "choice",
        "voted_at",
    )
    list_filter = (
        "poll",
        "choice",
    )
    readonly_fields = (
        "user",
        "poll",
        "choice",
        "voted_at",
        "notify_on_result",
    )

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False
