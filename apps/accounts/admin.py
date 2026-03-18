from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ("email", "username", "full_name", "is_staff", "is_active")
    search_fields = ("email", "username", "full_name")
    ordering = ("email",)

    fieldsets = UserAdmin.fieldsets + (
        ("Additional Info", {"fields": ("phone", "full_name", "id", "created_at", "updated_at")}),
    )
    readonly_fields = ("id", "created_at", "updated_at")