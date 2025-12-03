from pathlib import Path
import os
import dj_database_url
from dotenv import load_dotenv
from celery.schedules import crontab

BASE_DIR = Path(__file__).resolve().parent.parent

# Cargar .env
load_dotenv(BASE_DIR / ".env")

# ===========================
#        SEGURIDAD
# ===========================
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-key")
DEBUG = os.getenv("DEBUG", "0") == "1"

# Railway te da un dominio automático → por eso "*"
ALLOWED_HOSTS = ["*"]

CSRF_TRUSTED_ORIGINS = [
    "https://*.railway.app",
    "http://localhost",
    "http://127.0.0.1",
]

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ===========================
#        STATIC FILES
# ===========================
STATIC_URL = "/static/"

STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

# WhiteNoise para producción
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# ===========================
#        MEDIA
# ===========================
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ===========================
#        APPS
# ===========================
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

# ===========================
#     MIDDLEWARE
# ===========================
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",

    # WhiteNoise habilitación
    "whitenoise.middleware.WhiteNoiseMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# ===========================
#       ASGI / WSGI
# ===========================
ROOT_URLCONF = "cevicheria.urls"
WSGI_APPLICATION = "Cevicheria.wsgi.application"
ASGI_APPLICATION = "Cevicheria.asgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# ===========================
#      BASE DE DATOS
# ===========================

# Railway usa DATABASE_URL
DATABASES = {
    "default": dj_database_url.config(
        default=os.getenv("DATABASE_URL"),
        conn_max_age=600,
        ssl_require=not DEBUG,
    )
}

# ===========================
#   CHANNELS (WebSockets)
# ===========================
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0")],
        },
    }
}
# ===========================
#       WEBPAY
# ===========================
WEBPAY = {
    "COMMERCE_CODE": os.getenv("WEBPAY_COMMERCE_CODE"),
    "API_KEY": os.getenv("WEBPAY_API_KEY"),
    "ENVIRONMENT": os.getenv("WEBPAY_ENV", "TEST"),
    "RETURN_URL": os.getenv("WEBPAY_RETURN_URL", ""),
    "FINAL_URL": os.getenv("WEBPAY_FINAL_URL", ""),
}

# ===========================
#     VALIDADORES PASSWORD
# ===========================
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ===========================
#     REST FRAMEWORK
# ===========================
REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_RENDERER_CLASSES": ("rest_framework.renderers.JSONRenderer",),
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Cevichería API",
    "VERSION": "1.0.0",
}

# ===========================
#       EMAIL
# ===========================
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv("EMAIL_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_PASS")
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# ===========================
#       CELERY
# ===========================
CELERY_BROKER_URL = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0")
CELERY_RESULT_BACKEND = CELERY_BROKER_URL

CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "America/Santiago"

CELERY_BEAT_SCHEDULE = {
    "daily-report": {
        "task": "pedidos.tasks.generate_daily_report",
        "schedule": crontab(hour=23, minute=59),
    },
}
