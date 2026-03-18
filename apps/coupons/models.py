from django.conf import settings
from django.db import models
from apps.core.models import BaseModel


class CouponStatus(models.TextChoices):
    ACTIVE = "ACTIVE", "Active"
    USED = "USED", "Used"
    EXPIRED = "EXPIRED", "Expired"
    ARCHIVED = "ARCHIVED", "Archived"


class CouponType(models.TextChoices):
    CODE = "CODE", "Code"
    AUTO_APPLY = "AUTO_APPLY", "Auto Apply"
    VOUCHER = "VOUCHER", "Voucher"
    CASHBACK = "CASHBACK", "Cashback"


class CouponMemory(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="coupon_memories",
    )
    title = models.CharField(max_length=255)
    brand = models.CharField(max_length=255, blank=True, null=True)
    coupon_type = models.CharField(max_length=20, choices=CouponType.choices, default=CouponType.CODE)
    code = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    terms = models.TextField(blank=True, null=True)
    discount_text = models.CharField(max_length=100, blank=True, null=True)
    min_order_value = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    expiry_at = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=CouponStatus.choices, default=CouponStatus.ACTIVE)
    remind_before_minutes = models.IntegerField(default=1440)
    reminder_sent = models.BooleanField(default=False)

    class Meta:
        ordering = ["expiry_at", "-created_at"]

    def __str__(self):
        return self.title