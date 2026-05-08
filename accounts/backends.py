"""Username yoki email orqali kirish backend-i."""
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

User = get_user_model()


class UsernameOrEmailBackend(ModelBackend):
    """Foydalanuvchi username, email yoki telefon orqali tizimga kira oladi."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get("username") or kwargs.get("email")
        if username is None or password is None:
            return None
        try:
            user = User.objects.filter(
                Q(email__iexact=username)
                | Q(username__iexact=username)
                | Q(phone=username)
            ).first()
        except User.DoesNotExist:
            return None
        if user is None:
            return None
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
