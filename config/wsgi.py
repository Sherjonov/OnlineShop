"""WSGI konfiguratsiyasi — Gunicorn / Vercel uchun."""
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

application = get_wsgi_application()
app = application  # Vercel deploy uchun alias
