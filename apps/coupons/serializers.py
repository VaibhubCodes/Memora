from rest_framework import serializers
from .models import CouponMemory


class CouponMemorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CouponMemory
        fields = "__all__"
        read_only_fields = ["id", "user", "created_at", "updated_at", "reminder_sent"]