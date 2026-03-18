from django.contrib import admin
from .models import CalendarConnection, MeetingMemory


@admin.register(CalendarConnection)
class CalendarConnectionAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "provider",
        "provider_account_email",
        "status",
        "sync_status",
        "last_synced_at",
        "created_at",
    )
    search_fields = ("user__email", "provider_account_email")
    list_filter = ("provider", "status", "sync_status")
    readonly_fields = ("id", "created_at", "updated_at")


@admin.register(MeetingMemory)
class MeetingMemoryAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "user",
        "start_at",
        "end_at",
        "status",
        "is_cancelled",
        "is_all_day",
    )
    search_fields = ("title", "user__email", "organizer_email", "organizer_name")
    list_filter = ("status", "is_cancelled", "is_all_day")
    readonly_fields = ("id", "created_at", "updated_at")