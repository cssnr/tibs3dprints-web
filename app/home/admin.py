from django.contrib import admin

from .models import Contact, Message, MyNews


admin.site.register(Message)

admin.site.site_header = "My App Administration"


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = (
        "email",
        "subject",
        "created_at",
    )
    search_fields = (
        "email",
        "subject",
        "message",
    )
    readonly_fields = (
        "send_copy",
        "uuid",
        "created_at",
    )
    ordering = ("-pk",)

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(MyNews)
class MyNewsAdmin(admin.ModelAdmin):
    list_display = ("title", "display_name", "published", "created_at")
    list_filter = ("published",)
    search_fields = ("title",)
    ordering = ("-created_at",)
