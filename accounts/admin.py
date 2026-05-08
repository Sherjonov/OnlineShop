from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import AdminNotification, LoginActivity, User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = ("username", "email", "first_name", "last_name", "is_staff", "is_active", "created_at")
    list_filter = ("is_staff", "is_active", "is_email_verified")
    search_fields = ("username", "email", "first_name", "last_name", "phone")
    ordering = ("-created_at",)
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Shaxsiy", {"fields": ("first_name", "last_name", "email", "phone")}),
        ("Tarix", {"fields": ("previous_username", "previous_email", "password_changed_at")}),
        ("Ruxsatlar", {"fields": ("is_active", "is_staff", "is_superuser", "is_email_verified", "groups", "user_permissions")}),
        ("Sanalar", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("username", "email", "password1", "password2")}),
    )


@admin.register(LoginActivity)
class LoginActivityAdmin(admin.ModelAdmin):
    list_display = ("created_at", "username_snapshot", "full_name_snapshot", "action", "ip_address")
    list_filter = ("action",)
    search_fields = ("username_snapshot", "full_name_snapshot", "ip_address")
    readonly_fields = ("user", "username_snapshot", "full_name_snapshot", "action", "ip_address", "user_agent", "created_at")


@admin.register(AdminNotification)
class AdminNotificationAdmin(admin.ModelAdmin):
    list_display = ("title", "created_at")
    search_fields = ("title", "body")
