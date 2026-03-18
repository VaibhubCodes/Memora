from urllib.parse import urlencode

from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import redirect
from django.utils import timezone

from rest_framework import permissions, viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .google_calendar import GoogleCalendarClient
from .models import CalendarConnection, CalendarProvider, MeetingMemory
from .serializers import CalendarConnectionSerializer, MeetingMemorySerializer


User = get_user_model()


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def google_calendar_connect(request):
    client_id = getattr(settings, "GOOGLE_OAUTH_CLIENT_ID", "") or ""
    redirect_uri = getattr(settings, "GOOGLE_OAUTH_REDIRECT_URI", "") or ""

    if not client_id:
        return Response(
            {"detail": "GOOGLE_OAUTH_CLIENT_ID is missing in backend settings."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    if not redirect_uri:
        return Response(
            {"detail": "GOOGLE_OAUTH_REDIRECT_URI is missing in backend settings."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "openid email profile https://www.googleapis.com/auth/calendar.readonly",
        "access_type": "offline",
        "prompt": "consent",
        "state": str(request.user.id),
    }

    auth_url = "https://accounts.google.com/o/oauth2/v2/auth?" + urlencode(params)

    return Response(
        {
            "auth_url": auth_url,
            "client_id_present": True,
            "redirect_uri": redirect_uri,
        }
    )


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def google_calendar_callback(request):
    code = request.GET.get("code")
    state = request.GET.get("state")
    error = request.GET.get("error")

    if error:
        return Response({"detail": f"Google OAuth error: {error}"}, status=400)

    if not code or not state:
        return Response({"detail": "Missing code or state."}, status=400)

    try:
        user = User.objects.get(id=state)
    except User.DoesNotExist:
        return Response({"detail": "Invalid user state."}, status=400)

    temp_client = GoogleCalendarClient()
    token_data = temp_client.exchange_code_for_tokens(code)

    expires_in = token_data.get("expires_in", 3600)
    token_expiry = timezone.now() + timezone.timedelta(seconds=expires_in)

    connection, _ = CalendarConnection.objects.update_or_create(
        user=user,
        provider=CalendarProvider.GOOGLE,
        defaults={
            "access_token": token_data.get("access_token"),
            "refresh_token": token_data.get("refresh_token"),
            "token_expiry": token_expiry,
            "scope": token_data.get("scope"),
            "status": CalendarConnection._meta.get_field("status").default,
            "last_sync_error": None,
        },
    )

    client = GoogleCalendarClient(connection=connection)
    userinfo = client.get_userinfo()

    connection.provider_account_email = userinfo.get("email")
    connection.save(update_fields=["provider_account_email", "updated_at"])

    return redirect(settings.FRONTEND_CALENDAR_CONNECTED_REDIRECT_URL)


class CalendarConnectionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CalendarConnectionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CalendarConnection.objects.filter(user=self.request.user)


class MeetingMemoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = MeetingMemorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = MeetingMemory.objects.filter(user=self.request.user)

        upcoming = self.request.query_params.get("upcoming")
        today = self.request.query_params.get("today")

        if upcoming == "1":
            queryset = queryset.filter(start_at__gte=timezone.now())

        if today == "1":
            start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timezone.timedelta(days=1)
            queryset = queryset.filter(start_at__gte=start, start_at__lt=end)

        return queryset