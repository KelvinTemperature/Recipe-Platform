from .base import *
import os
import dj_database_url
import cloudinary
import cloudinary.uploader
import cloudinary.api

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

# ── Static files ──
STATIC_URL  = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# ── Cloudinary for media files ──
cloudinary.config(
    cloud_name = config('CLOUDINARY_CLOUD_NAME', default=''),
    api_key    = config('CLOUDINARY_API_KEY',    default=''),
    api_secret = config('CLOUDINARY_API_SECRET', default=''),
    secure     = True,
)

CLOUDINARY_STORAGE = {
    'CLOUD_NAME' : config('CLOUDINARY_CLOUD_NAME', default=''),
    'API_KEY'    : config('CLOUDINARY_API_KEY',    default=''),
    'API_SECRET' : config('CLOUDINARY_API_SECRET', default=''),
}


STORAGES = {
    "default": {
        "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# ── Fallback for older packages that check these directly ──
DEFAULT_FILE_STORAGE  = 'cloudinary_storage.storage.MediaCloudinaryStorage'
STATICFILES_STORAGE   = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

SECURE_BROWSER_XSS_FILTER  = True
SECURE_CONTENT_TYPE_NOSNIFF = True