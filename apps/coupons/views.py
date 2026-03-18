from django.utils import timezone
from rest_framework import permissions, viewsets
from .models import CouponMemory, CouponStatus
from .serializers import CouponMemorySerializer


class CouponMemoryViewSet(viewsets.ModelViewSet):
    serializer_class = CouponMemorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = CouponMemory.objects.filter(user=self.request.user)

        active = self.request.query_params.get("active")
        expiring = self.request.query_params.get("expiring")

        if active == "1":
            queryset = queryset.filter(status=CouponStatus.ACTIVE)

        if expiring == "1":
            now = timezone.now()
            next_week = now + timezone.timedelta(days=7)
            queryset = queryset.filter(
                status=CouponStatus.ACTIVE,
                expiry_at__isnull=False,
                expiry_at__gte=now,
                expiry_at__lte=next_week,
            )

        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)