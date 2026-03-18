from django.conf import settings
from django.db import models
from apps.core.models import BaseModel


class CalendarProvider(models.TextChoices):
    GOOGLE = "GOOGLE", "Google"


class ConnectionStatus(models.TextChoices):
    ACTIVE = "ACTIVE", "Active"
    REVOKED = "REVOKED", "Revoked"
    ERROR = "ERROR", "Error"


class SyncStatus(models.TextChoices):
    IDLE = "IDLE", "Idle"
    RUNNING = "RUNNING", "Running"
    ERROR = "ERROR", "Error"


class CalendarConnection(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="calendar_connections",
    )
    provider = models.CharField(
        max_length=20,
        choices=CalendarProvider.choices,
        default=CalendarProvider.GOOGLE,
    )
    provider_account_email = models.EmailField(blank=True, null=True)

    access_token = models.TextField(blank=True, null=True)
    refresh_token = models.TextField(blank=True, null=True)
    token_expiry = models.DateTimeField(blank=True, null=True)
    scope = models.TextField(blank=True, null=True)

    status = models.CharField(
        max_length=20,
        choices=ConnectionStatus.choices,
        default=ConnectionStatus.ACTIVE,
    )
    sync_status = models.CharField(
        max_length=20,
        choices=SyncStatus.choices,
        default=SyncStatus.IDLE,
    )
    last_synced_at = models.DateTimeField(blank=True, null=True)
    last_sync_error = models.TextField(blank=True, null=True)

    watch_channel_id = models.CharField(max_length=255, blank=True, null=True)
    watch_resource_id = models.CharField(max_length=255, blank=True, null=True)
    watch_expiration = models.DateTimeField(blank=True, null=True)

    next_sync_token = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.email} - {self.provider}"


class MeetingStatus(models.TextChoices):
    CONFIRMED = "confirmed", "Confirmed"
    TENTATIVE = "tentative", "Tentative"
    CANCELLED = "cancelled", "Cancelled"


class MeetingMemory(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="meeting_memories",
    )
    connection = models.ForeignKey(
        CalendarConnection,
        on_delete=models.CASCADE,
        related_name="meetings",
    )

    remote_event_id = models.CharField(max_length=255)
    title = models.CharField(max_length=500, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    location = models.TextField(blank=True, null=True)
    html_link = models.URLField(blank=True, null=True)

    status = models.CharField(
        max_length=20,
        choices=MeetingStatus.choices,
        default=MeetingStatus.CONFIRMED,
    )

    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    is_all_day = models.BooleanField(default=False)
    organizer_email = models.EmailField(blank=True, null=True)
    organizer_name = models.CharField(max_length=255, blank=True, null=True)

    attendees_json = models.JSONField(default=list, blank=True)
    raw_payload = models.JSONField(default=dict, blank=True)

    is_cancelled = models.BooleanField(default=False)
    is_deleted_remotely = models.BooleanField(default=False)

    class Meta:
        unique_together = ("connection", "remote_event_id")
        ordering = ["start_at"]

    def __str__(self):
        return self.title or self.remote_event_id