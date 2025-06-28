from django.contrib import admin

from .models import AppUser, BetaUser, Choice, Point, Poll, Vote


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


@admin.register(AppUser)
class AppUserAdmin(admin.ModelAdmin):
    list_display = (
        "email",
        "name",
        "verified",
    )
    list_filter = ("email",)
    search_fields = ("email",)
    # ordering = ("name",)
    readonly_fields = (
        "email",
        "verified",
        "name",
        "points",
        "last_login",
        "updated_at",
        "created_at",
    )
    exclude = ("authorization",)

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

    # def has_delete_permission(self, request, obj=None):
    #     return False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Point)
class PointAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "points",
        "reason",
    )
    list_filter = (
        "user",
        "points",
    )
    readonly_fields = (
        "user",
        "points",
        "reason",
    )

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False
