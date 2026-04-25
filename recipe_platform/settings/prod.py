from .base import *
import os
import dj_database_url

DEBUG = False

ALLOWED_HOSTS = [
    'recipe-platform-production-f8c7.up.railway.app',
    'localhost',
    '127.0.0.1',
]

DATABASE_URL = os.environ.get('DATABASE_URL')

if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL)
    }
else:
    DATABASES = {
        'default': {
            'ENGINE'  : 'django.db.backends.postgresql',
            'NAME'    : config('DB_NAME'),
            'USER'    : config('DB_USER'),
            'PASSWORD': config('DB_PASSWORD'),
            'HOST'    : config('DB_HOST'),
            'PORT'    : config('DB_PORT', default='5432'),
        }
    }

CORS_ALLOWED_ORIGINS = [
    'https://recipe-platform-production-f8c7.up.railway.app',
]

CORS_ALLOW_ALL_ORIGINS = True

CSRF_TRUSTED_ORIGINS = [
    'https://recipe-platform-production-f8c7.up.railway.app',
]

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
STATIC_ROOT = BASE_DIR / 'staticfiles'