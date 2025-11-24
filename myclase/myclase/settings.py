from pathlib import Path
import environ
import dj_database_url  # 👈 necesario para Render (PostgreSQL)
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# Inicializar entorno
env = environ.Env(
    DEBUG=(bool, False)
)

# Leer archivo .env local (en Render se usan variables del panel)
environ.Env.read_env(BASE_DIR / ".env")

# Variables de entorno
SECRET_KEY = env("SECRET_KEY", default="dev-secret-no-usar-en-prod")
DEBUG = env("DEBUG", default=False)
MERCADOPAGO_ACCESS_TOKEN = env("MERCADOPAGO_ACCESS_TOKEN", default="")
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])

# --------------------------------------------------------------------
# APLICACIONES
# --------------------------------------------------------------------
INSTALLED_APPS = [
    # Django
    "cloudinary_storage",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",

    # Terceros
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "allauth.socialaccount.providers.github",
    'cloudinary', # <-- Agregar esto

    # Apps propias
    "core",
    "market",
    'profiles.apps.PerfilConfig',
    "chat",
    "scanner",
    "dashboard",
]

SITE_ID = 1

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

LOGIN_REDIRECT_URL = "home"
LOGOUT_REDIRECT_URL = "home"

ACCOUNT_LOGIN_METHODS = {"email", "username"}
ACCOUNT_SIGNUP_FIELDS = ["email*", "username*", "password1*", "password2*"]
ACCOUNT_EMAIL_VERIFICATION = "none"
ACCOUNT_EMAIL_REQUIRED = False

# --------------------------------------------------------------------
# MIDDLEWARE
# --------------------------------------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # 👈 necesario para static en Render
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    'market.middleware.AutoLogoutMiddleware',
]

ROOT_URLCONF = "myclase.urls"
AUTO_LOGOUT_DELAY = 300
# --------------------------------------------------------------------
# TEMPLATES
# --------------------------------------------------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "market.context_processors.user_avatar",
                'profiles.context_processors.avatar',
                "market.context_processors.product_notifications",
                "core.context_processors.navbar_notifications"
            ],
        },
    },
]

WSGI_APPLICATION = "myclase.wsgi.application"

# --------------------------------------------------------------------
# BASE DE DATOS
# --------------------------------------------------------------------

if DEBUG:
    # Estamos en desarrollo (local), usamos SQLite
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
else:
    # Estamos en producción (Render), usamos la DATABASE_URL
    # dj_database_url leerá automáticamente la variable de entorno DATABASE_URL
    DATABASES = {
        "default": dj_database_url.config(
            # Forzamos SSL, es requerido por Render
            conn_max_age=600,
            ssl_require=True,
        )
    }
# --------------------------------------------------------------------
# ARCHIVOS ESTÁTICOS Y MEDIA
# --------------------------------------------------------------------

# Rutas de archivos estáticos (CSS, JS, Img del diseño)
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"  # Carpeta donde Render recolecta todo
STATICFILES_DIRS = [BASE_DIR / "static"] # Carpeta donde tú guardas tus estilos

# WhiteNoise: Usamos esta versión "segura" que no rompe si falta un archivo
STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"

# Rutas de archivos Media (Subidos por usuarios)
MEDIA_URL = "/media/"
DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"
# Configuración de Cloudinary
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': env('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': env('CLOUDINARY_API_KEY'),
    'API_SECRET': env('CLOUDINARY_API_SECRET'),
}
# --------------------------------------------------------------------
# CSRF Y ORÍGENES CONFIABLES
# --------------------------------------------------------------------
CSRF_TRUSTED_ORIGINS = [
    "https://filling-lined-timber-inherited.trycloudflare.com",
    "https://*.onrender.com",  # 👈 necesario para Render
]

# --------------------------------------------------------------------
# EMAIL (desarrollo)
# --------------------------------------------------------------------
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# --------------------------------------------------------------------
# LOGGING (opcional pero útil)
# --------------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "INFO"},
}

SOCIALACCOUNT_LOGIN_ON_GET = True
ACCOUNT_LOGOUT_ON_GET = True
LOGOUT_REDIRECT_URL = '/'
# Configuración de Email para Gmail
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'mirendarodrigo@gmail.com' 
EMAIL_HOST_PASSWORD = 'qlaj sfsi sgpv qbdi'  
