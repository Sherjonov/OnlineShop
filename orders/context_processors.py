"""Cart count va admin notifikatsiyalarini har bir templatega o'tkazish."""
from accounts.models import AdminNotification

from .services import cart_summary


def cart(request):
    try:
        s = cart_summary(request.session)
        return {
            "cart_total_items": s["total_items"],
            "cart_subtotal": s["subtotal"],
            "cart_total": s["total"],
        }
    except Exception:
        return {"cart_total_items": 0, "cart_subtotal": 0, "cart_total": 0}


def notifications(request):
    try:
        return {"latest_notifications": AdminNotification.objects.all()[:5]}
    except Exception:
        return {"latest_notifications": []}
