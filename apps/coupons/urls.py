from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import CouponMemoryViewSet

router = DefaultRouter()
router.register("", CouponMemoryViewSet, basename="coupons")

urlpatterns = [
    path("", include(router.urls)),
]