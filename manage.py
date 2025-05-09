# Custom manage.py for development
import os
import sys
from pathlib import Path

import django
from django.conf import settings
from django.core.management import execute_from_command_line

BASE_DIR = Path(__file__).resolve().parent

settings.configure(
    BASE_DIR=BASE_DIR,
    SEGUIMIENTOLITE_IVA=1.16,
    SEGUIMIENTOLITE_PRECIO_UT=100,
    AVISO_PRIVACIDAD="",
    DEBUG=True,
    SECRET_KEY="citas-dinissan",
    LANGUAGE_CODE="es-MX",
    INSTALLED_APPS=[
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        "django.contrib.staticfiles",
        "django.contrib.humanize",
        "rest_framework",
        "django_drf_filepond",
        "django_q",
        # Third party apps
        "citas_dinissan",
        "tracker_pro_toyota_mx",
    ],
    TEMPLATES=[
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": [],
            "APP_DIRS": True,
            "OPTIONS": {
                "context_processors": [
                    "django.template.context_processors.debug",
                    "django.template.context_processors.request",
                    "django.contrib.auth.context_processors.auth",
                    "django.contrib.messages.context_processors.messages",
                ],
            },
        },
    ],
    MIDDLEWARE=[
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "django.contrib.messages.middleware.MessageMiddleware",
    ],
    ROOT_URLCONF="urls",
    STATIC_URL="/static/",
    ASGI_APPLICATION="asgi.application",
    DATABASES={
        "default": {
            "ENGINE": "mssql",  # No se modifica
            "HOST": "capnet3.ddns.net",  # Nombre de la instancia de SQL Server
            "NAME": "capnet-apps-vardi",  # Nombre de la base de datos
            "USER": "capnet_esp",  # Usuario
            "PASSWORD": ".5capnet",  # Contraseña
        }
    },
    ALLOWED_HOSTS=["*"],
    REST_FRAMEWORK={
        "DEFAULT_AUTHENTICATION_CLASSES": [
            "rest_framework.authentication.TokenAuthentication",
        ]
    },
    MEDIA_ROOT=BASE_DIR / "media",
    MEDIA_URL="/media/",
    LOGIN_URL='/citas/login',
    LOGIN_REDIRECT_URL='/citas/nuevacita/ /',
    LOGOUT_REDIRECT_URL='/citas/login',
    LOGIN_REQUIRED=True,
    # App settings
    AGENCIA="Vardi",
    COREAPI_INFORMACION="",
    COREAPI_MENSAJES="",
    COREAPI_DATOS_CLIENTE="",
    CITAS_TABLEROAPI="http://201.150.44.27:8705",
    RAZON_SOCIAL="Hyundai SA. DE CV",
    DIRECCION_AGENCIA="Dirección de la agencia",
    DOMINIO="capnet2.ddns.net",
    PUERTO="5100",
    TELEFONO="",  # Teléfono de la agencia
    IVA=1.16,
    SEGUIMIENTOLITE_CORREOS_REFACCIONES=[""],
    SEGUIMIENTOLITE_CORREOS_GERENCIA=[""],
    COREAPI="http://capnet.ddns.net:8021/api/v1.2/wa/msj/",
    DJANGO_DRF_FILEPOND_FILE_STORE_PATH=os.path.join(BASE_DIR, "media"),
    LOGO="https://wscapnet.com.mx:8310/media/LogoVardi.png",
    EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend',
    EMAIL_HOST="smtp.gmail.com",
    EMAIL_PORT=587,
    EMAIL_USE_SSL=False,
    EMAIL_USE_TLS=True,
    EMAIL_HOST_USER="angiecastaneda.capnet@gmail.com",
    EMAIL_HOST_PASSWORD="vplw nuol maen czpk",
    DEFAULT_FROM_EMAIL="citastallermazda@gmail.com",
    API_MAZDA=True,
    TIME_ZONE='America/Mexico_City',
    USE_TZ=True,
    # Django Q cluster configuration
    Q_CLUSTER={
        'name': 'DjangoQ',
        "timezone": "America/Mexico_City",
        'workers': 4,
        'recycle': 500,
        'timeout': 60,
        'retry': 120,
        'queue_limit': 50,
        'bulk': 10,
        'orm': 'default',
    },
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
            },
            'file': {
                'class': 'logging.FileHandler',
                'filename': os.path.join(BASE_DIR, 'django_q.log'),
                'level': 'DEBUG',
            },
        },
        'loggers': {
            'django_q': {
                'handlers': ['console', 'file'],
                'level': 'DEBUG',
            },
        },
    }
)

django.setup()

if __name__ == "__main__":
    execute_from_command_line(sys.argv)
