from django.contrib import admin
from .models import CouponMemory


@admin.register(CouponMemory)
class CouponMemoryAdmin(admin.ModelAdmin):
    list_display = ("title", "brand", "status", "expiry_at", "user")
    search_fields = ("title", "brand", "code", "user__email")
    list_filter = ("status", "coupon_type")