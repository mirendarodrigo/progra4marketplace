from pathlib import Path
import environ
env = environ.Env(DEBUG=(bool, True))
environ.Env.read_env()  # lee .env si existe

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = env("SECRET_KEY", default="dev-secret-no-usar-en-prod")
DEBUG = env("DEBUG", default=True)
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",           # <-- requerido por allauth

    # Terceros
    "allauth",                        # núcleo
    "allauth.account",                # cuentas locales (si querés)
    "allauth.socialaccount",          # social login
    "allauth.socialaccount.providers.google",
    "allauth.socialaccount.providers.github",

    # Apps propias
    "core",
    "market",
    "perfil",

]

SITE_ID = 1

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

LOGIN_REDIRECT_URL = "home"
LOGOUT_REDIRECT_URL = "home"

# (opcional) Config de allauth
ACCOUNT_LOGIN_METHODS = {"email", "username"}
ACCOUNT_SIGNUP_FIELDS = ["email*", "username*", "password1*", "password2*"]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
 "allauth.account.middleware.AccountMiddleware", #necesario para auth

]

ROOT_URLCONF = "myclase.urls"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],     # <-- carpeta de templates
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",  # <-- requerido por allauth
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                'market.context_processors.user_avatar',
            ],
        },
    },
]

WSGI_APPLICATION = "myclase.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "APP": {
            "client_id": "947489055391-ofuacjidccei07seej4lkntjeojp9nus.apps.googleusercontent.com",      # si preferís cargar desde settings en vez de admin
            "secret": "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",
        },
        "SCOPE": ["profile", "email"],
        "AUTH_PARAMS": {"access_type": "online"},
    },
    "github": {
        "APP": {
            "client_id": "Ov23liHcSano1rVvGrTU",
            "secret": "dcbbc7ed56cc59d77fde1121ddc42d443d52aa98",
        },
        "SCOPE": ["user:email"],
    },
}

CSRF_TRUSTED_ORIGINS = [
   "https://factory-strengths-signing-unit.trycloudflare.com"
]


STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "static"]



