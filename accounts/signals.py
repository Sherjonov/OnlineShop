"""Kirish/chiqishni LoginActivity jadvaliga yozadi."""
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver

from .models import LoginActivity


def _ip(request):
    if request is None:
        return None
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def _ua(request):
    if request is None:
        return ""
    return request.META.get("HTTP_USER_AGENT", "")[:255]


@receiver(user_logged_in)
def on_login(sender, request, user, **kwargs):
    LoginActivity.objects.create(
        user=user,
        username_snapshot=user.username,
        full_name_snapshot=user.full_name,
        action=LoginActivity.LOGIN,
        ip_address=_ip(request),
        user_agent=_ua(request),
    )


@receiver(user_logged_out)
def on_logout(sender, request, user, **kwargs):
    if user is None:
        return
    LoginActivity.objects.create(
        user=user,
        username_snapshot=user.username,
        full_name_snapshot=user.full_name,
        action=LoginActivity.LOGOUT,
        ip_address=_ip(request),
        user_agent=_ua(request),
    )


@receiver(user_login_failed)
def on_failed(sender, credentials, request, **kwargs):
    LoginActivity.objects.create(
        username_snapshot=str(credentials.get("username") or "")[:64],
        action=LoginActivity.FAILED,
        ip_address=_ip(request),
        user_agent=_ua(request),
    )
