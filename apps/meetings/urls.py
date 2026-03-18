from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import google_calendar_connect, CalendarConnectionViewSet, MeetingMemoryViewSet

router = DefaultRouter()
router.register("connections", CalendarConnectionViewSet, basename="meeting-connections")
router.register("items", MeetingMemoryViewSet, basename="meeting-items")

urlpatterns = [
    path("google/connect/", google_calendar_connect, name="google-calendar-connect"),
    path("", include(router.urls)),
]