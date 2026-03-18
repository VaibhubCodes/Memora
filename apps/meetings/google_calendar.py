from datetime import timedelta
import requests

from django.conf import settings
from django.utils import timezone


GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"
GOOGLE_CALENDAR_LIST_URL = "https://www.googleapis.com/calendar/v3/users/me/calendarList"


class GoogleCalendarClient:
    def __init__(self, connection=None, access_token=None):
        self.connection = connection
        self._manual_access_token = access_token

    def exchange_code_for_tokens(self, code: str) -> dict:
        response = requests.post(
            GOOGLE_TOKEN_URL,
            data={
                "code": code,
                "client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
                "client_secret": settings.GOOGLE_OAUTH_CLIENT_SECRET,
                "redirect_uri": settings.GOOGLE_OAUTH_REDIRECT_URI,
                "grant_type": "authorization_code",
            },
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    def refresh_access_token(self) -> str:
        if not self.connection or not self.connection.refresh_token:
            raise ValueError("Connection or refresh token is missing.")

        response = requests.post(
            GOOGLE_TOKEN_URL,
            data={
                "client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
                "client_secret": settings.GOOGLE_OAUTH_CLIENT_SECRET,
                "refresh_token": self.connection.refresh_token,
                "grant_type": "refresh_token",
            },
            timeout=30,
        )
        response.raise_for_status()
        payload = response.json()

        self.connection.access_token = payload["access_token"]
        expires_in = payload.get("expires_in", 3600)
        self.connection.token_expiry = timezone.now() + timedelta(seconds=expires_in)
        self.connection.save(update_fields=["access_token", "token_expiry", "updated_at"])

        return self.connection.access_token

    def get_access_token(self) -> str:
        if self._manual_access_token:
            return self._manual_access_token

        if not self.connection:
            raise ValueError("Connection is required to get stored access token.")

        if (
            not self.connection.access_token
            or not self.connection.token_expiry
            or self.connection.token_expiry <= timezone.now()
        ):
            return self.refresh_access_token()

        return self.connection.access_token

    def headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.get_access_token()}",
            "Accept": "application/json",
        }

    def get_userinfo(self) -> dict:
        response = requests.get(
            GOOGLE_USERINFO_URL,
            headers=self.headers(),
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    def list_calendars(self) -> dict:
        response = requests.get(
            GOOGLE_CALENDAR_LIST_URL,
            headers=self.headers(),
            timeout=30,
        )
        response.raise_for_status()
        return response.json()