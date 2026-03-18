from rest_framework import serializers
from .models import CalendarConnection, MeetingMemory


class CalendarConnectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CalendarConnection
        fields = [
            "id",
            "provider",
            "provider_account_email",
            "status",
            "sync_status",
            "last_synced_at",
            "last_sync_error",
            "watch_expiration",
            "created_at",
            "updated_at",
        ]


class MeetingMemorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MeetingMemory
        fields = [
            "id",
            "user",
            "connection",
            "remote_event_id",
            "title",
            "description",
            "location",
            "html_link",
            "status",
            "start_at",
            "end_at",
            "is_all_day",
            "organizer_email",
            "organizer_name",
            "attendees_json",
            "raw_payload",
            "is_cancelled",
            "is_deleted_remotely",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "user",
            "created_at",
            "updated_at",
        ]