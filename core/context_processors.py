from django.conf import settings


def site_settings(request):
    return {
        "SITE_NAME": settings.SITE_NAME,
        "DELIVERY_FEE": settings.DELIVERY_FEE,
        "FREE_DELIVERY_FROM": settings.FREE_DELIVERY_FROM,
        "TELEGRAM_USERNAME": "Sherjonov_011",
        "INSTAGRAM_USERNAME": "sherjonov.011",
    }
