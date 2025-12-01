from pathlib import Path
import os
from dotenv import load_dotenv
from dotenv import load_dotenv
from celery.schedules import crontab  # para Celery Beat

# Cargar entorno
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# ====== Seguridad ======
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-key-no-segura")
DEBUG = os.getenv("DEBUG", "1") == "1"
ALLOWED_HOSTS = ["*"]
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ====== Static Files ======
STATIC_URL = "/static/"

# En desarrollo Django lee de: /static/css y /static/js
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

# En producción runserver no usa esto, pero collectstatic SÍ lo necesita
STATIC_ROOT = BASE_DIR / "staticfiles"

# ====== MEDIA ======
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ====== Apps instaladas ======
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "rest_framework",
    "channels",

    "pedidos.apps.PedidosConfig", 
]

# ====== Middlewares ======
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "Cevicheria.urls"
WSGI_APPLICATION = "Cevicheria.wsgi.application"
ASGI_APPLICATION = "Cevicheria.asgi.application"

# ====== Plantillas ======
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

WEBPAY = { 
    "COMMERCE_CODE": os.getenv("WEBPAY_COMMERCE_CODE"),
    "API_KEY": os.getenv("WEBPAY_API_KEY"),
    "ENVIRONMENT": os.getenv("WEBPAY_ENV", "TEST"),
    "RETURN_URL": "http://127.0.0.1:8000/api/webpay/return/", # ✅ debe coincidir con urls.py 
    "FINAL_URL": "http://127.0.0.1:8000/pago-finalizado/", }
# ====== Base de datos ======
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


CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    }
}
# ====== Validadores de contraseña ======
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ====== Rest Framework & schema ======
REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_RENDERER_CLASSES": ("rest_framework.renderers.JSONRenderer",),
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Cevichería API",
    "VERSION": "1.0.0",
}

# ====== Email ======
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv("EMAIL_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_PASS")
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# ====== Celery Beat (ahora solo una configuración) ======
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
