from pathlib import Path
import os
from dotenv import load_dotenv
from celery.schedules import crontab

# Base
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# Seguridad
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-key-no-segura")
DEBUG = os.getenv("DEBUG", "1") == "1"
ALLOWED_HOSTS = ["*"]

# Static (desarrollo + producción)
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

# Media
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Apps
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "channels",
    "pedidos",
]

# BD
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB"),
        "USER": os.getenv("POSTGRES_USER"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD"),
        "HOST": os.getenv("POSTGRES_HOST", "localhost"),
        "PORT": os.getenv("POSTGRES_PORT", "5432"),
    }
}

# ====== CHANNEL LAYERS (desarrollo sin Redis) ======
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer"
    }
}

# Celery
CELERY_BROKER_URL = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0")
CELERY_RESULT_BACKEND = CELERY_BROKER_URL
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "America/Santiago"
CELERY_BEAT_SCHEDULE = {
    "daily-report": {
        "task": "pedidos.tasks.generate_daily_report",
        "schedule": crontab(hour=23, minute=59),
    }
}

# Email
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv("EMAIL_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_PASS")
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
WEBPAY = { 
    "COMMERCE_CODE": os.getenv("WEBPAY_COMMERCE_CODE"),
    "API_KEY": os.getenv("WEBPAY_API_KEY"),
    "ENVIRONMENT": os.getenv("WEBPAY_ENV", "TEST"),
    "RETURN_URL": "http://127.0.0.1:8000/api/webpay/return/", # ✅ debe coincidir con urls.py 
    "FINAL_URL": "http://127.0.0.1:8000/pago-finalizado/", }