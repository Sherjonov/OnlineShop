"""Foydalanuvchi va kirish-chiqish jurnali."""
from __future__ import annotations

from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create(self, username, email, password, **extra):
        if not username:
            raise ValueError("username majburiy")
        email = self.normalize_email(email or "")
        user = self.model(username=username, email=email, **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email=None, password=None, **extra):
        extra.setdefault("is_staff", False)
        extra.setdefault("is_superuser", False)
        return self._create(username, email, password, **extra)

    def create_superuser(self, username, email=None, password=None, **extra):
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        extra.setdefault("is_active", True)
        return self._create(username, email, password, **extra)


class User(AbstractUser):
    username = models.CharField("Username", max_length=64, unique=True)
    email = models.EmailField("Email", unique=True)
    phone = models.CharField("Telefon", max_length=32, blank=True, default="")
    first_name = models.CharField("Ism", max_length=64, blank=True, default="")
    last_name = models.CharField("Familiya", max_length=64, blank=True, default="")
    is_email_verified = models.BooleanField("Email tasdiqlandi", default=False)

    # Sozlamalarda eski/yangi qiymatlarni ko'rsatish uchun
    previous_email = models.EmailField("Oldingi email", blank=True, default="")
    previous_username = models.CharField("Oldingi username", max_length=64, blank=True, default="")
    password_changed_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    class Meta:
        verbose_name = "Foydalanuvchi"
        verbose_name_plural = "Foydalanuvchilar"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.username

    @property
    def full_name(self) -> str:
        n = f"{self.first_name} {self.last_name}".strip()
        return n or self.username

    @property
    def is_admin(self) -> bool:
        return bool(self.is_superuser or self.is_staff)


class LoginActivity(models.Model):
    LOGIN = "login"
    LOGOUT = "logout"
    REGISTER = "register"
    FAILED = "failed"
    ACTIONS = [
        (LOGIN, "Kirdi"),
        (LOGOUT, "Chiqdi"),
        (REGISTER, "Ro'yxatdan o'tdi"),
        (FAILED, "Xato kirish"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="activities",
    )
    username_snapshot = models.CharField(max_length=64, blank=True, default="")
    full_name_snapshot = models.CharField(max_length=128, blank=True, default="")
    action = models.CharField(max_length=16, choices=ACTIONS, default=LOGIN)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Faollik"
        verbose_name_plural = "Kirish/Chiqish jadvali"

    def __str__(self) -> str:
        return f"{self.username_snapshot} — {self.get_action_display()} — {self.created_at:%Y-%m-%d %H:%M}"


class AdminNotification(models.Model):
    """Admin yangi mahsulot qo'shganda boshqalarga ko'rsatiladigan xabar."""
    title = models.CharField(max_length=160)
    body = models.CharField(max_length=400, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title
