"""
Django settings for attendance_system project.
"""

import os
import sys

# Use PyMySQL as MySQL driver
import pymysql
pymysql.version_info = (2, 2, 1, 'final', 0)
pymysql.install_as_MySQLdb()

# Bypass MariaDB version check for local development
from django.db.backends.mysql.base import DatabaseWrapper
DatabaseWrapper.check_database_version_supported = lambda self: None

# Disable RETURNING clause on INSERT statements for compatibility with MariaDB < 10.5
from django.db.backends.mysql.features import DatabaseFeatures
DatabaseFeatures.can_return_columns_from_insert = property(lambda self: False)

from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

SECRET_KEY = 'django-insecure-y%b=$z^jmh@$tjrvs0e!2_idbr5y--!e=9jn_c@jd*vgdomzjj'

DEBUG = os.getenv('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1,testserver').split(',')

INSTALLED_APPS = [
    'daphne',       # ← Doit être en premier pour runserver ASGI
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'rest_framework_simplejwt',   # ← Très important
    'corsheaders',  # ← CORS pour communication frontend
    'channels',     # ← Django Channels WebSocket
    
    # Système core principal uniquement
    'core.apps.CoreConfig',
    'users',  # Gardé pour le modèle User

]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # ← CORS en premier
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # ← WhiteNoise pour les fichiers statiques
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'attendance_system.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'attendance_system.wsgi.application'

import dj_database_url

DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv('DATABASE_URL', 'mysql://root:@127.0.0.1:3306/pointage'),
        conn_max_age=600,
        conn_health_checks=True,
    )
}
# Support custom mysql init commands for local dev if needed
if DATABASES['default']['ENGINE'] == 'django.db.backends.mysql':
    if 'OPTIONS' not in DATABASES['default']:
        DATABASES['default']['OPTIONS'] = {}
    DATABASES['default']['OPTIONS']['charset'] = 'utf8mb4'
    DATABASES['default']['OPTIONS']['init_command'] = "SET sql_mode='STRICT_TRANS_TABLES'"

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Europe/Paris'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ====================== AUTHENTICATION ======================
AUTH_USER_MODEL = 'users.User'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': False,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# ====================== CORS CONFIGURATION ======================
CORS_ALLOW_ALL_ORIGINS = os.getenv('CORS_ALLOW_ALL_ORIGINS', 'True') == 'True'

# Autoriser le frontend Vite (port 5173) et autres origines de développement
_cors_origins = os.getenv('CORS_ALLOWED_ORIGINS', 'http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000').split(',')
CORS_ALLOWED_ORIGINS = [origin.strip() for origin in _cors_origins if origin.strip()]

# Autoriser les credentials (cookies, headers d'authentification)
CORS_ALLOW_CREDENTIALS = True

# Autoriser tous les headers nécessaires pour l'authentification JWT
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# Autoriser toutes les méthodes HTTP
CORS_ALLOW_METHODS = [
    'GET',
    'POST',
    'PUT',
    'PATCH',
    'DELETE',
    'OPTIONS',
]

# ====================== EMAIL CONFIGURATION ======================
# Charge les configurations depuis le fichier .env (se rabat sur la console en développement)
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'TRACKTIME <noreply@unipro.com>')
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:5173')

# ====================== REDIS & CACHE ======================
REDIS_URL = os.getenv('REDIS_URL', 'redis://127.0.0.1:6379/0')

if os.getenv('RENDER') == 'true' and ('127.0.0.1' in REDIS_URL or 'localhost' in REDIS_URL):
    # En production sur Render, si Redis n'est pas configuré, on utilise le cache en mémoire pour éviter les crashs
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "tracktime-locmem",
        }
    }
    
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels.layers.InMemoryChannelLayer",
        },
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": REDIS_URL,
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
                "IGNORE_EXCEPTIONS": True,  # Si Redis est indisponible, pas de crash
                "CONNECTION_POOL_KWARGS": {
                    "protocol": 2,  # Requis pour compatibilité avec Redis 3.0.504 (pas de HELLO)
                }
            },
            "TIMEOUT": 30,  # TTL par défaut : 30 secondes
            "KEY_PREFIX": "tracktime",
        }
    }

    # ====================== DJANGO CHANNELS (WebSocket) ======================
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {
                "hosts": [
                    {
                        "address": REDIS_URL,
                        "protocol": 2,  # Requis pour compatibilité avec Redis 3.0.504 (pas de HELLO)
                    }
                ],
                "capacity": 1500,
                "expiry": 10,
            },
        },
    }

ASGI_APPLICATION = 'attendance_system.asgi.application'

