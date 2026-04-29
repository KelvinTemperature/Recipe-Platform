from pathlib import Path
from decouple import config
import cloudinary

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = config('SECRET_KEY')

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'cloudinary',                
    'cloudinary_storage',            

    # Local
    'accounts',
    'recipes',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'recipe_platform.urls'

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

JAZZMIN_SETTINGS = {
    # ── Branding ──────────────────────────────────────
    "site_title"        : "Recipe Platform Admin",
    "site_header"       : "Recipe Platform",
    "site_brand"        : "🍽️ RecipePlatform",
    "site_logo"         : None,
    "welcome_sign"      : "Welcome to Recipe Platform Admin",
    "copyright"         : "Recipe Platform",

    # ── Top Navigation ────────────────────────────────
    "topmenu_links": [
        {"name": "🏠 Home",     "url": "admin:index"},
        {"name": "🌍 View Site", "url": "/api/recipes/"},
    ],

    # ── Side Menu ─────────────────────────────────────
    "show_sidebar"              : True,
    "navigation_expanded"       : True,
    "hide_apps"                 : [],
    "hide_models"               : [],

    "icons": {
        "accounts.User"    : "fas fa-users",
        "recipes.Recipe"   : "fas fa-utensils",
        "recipes.Tag"      : "fas fa-tags",
        "recipes.Ingredient" : "fas fa-list",
        "recipes.RecipeStep" : "fas fa-shoe-prints",
        "recipes.Bookmark" : "fas fa-bookmark",
        "recipes.Rating"   : "fas fa-star",
    },

    "default_icon_parents"  : "fas fa-folder",
    "default_icon_children" : "fas fa-circle",

    # ── UI Tweaks ─────────────────────────────────────
    "related_modal_active"      : True,
    "custom_css"                : None,
    "custom_js"                 : None,
    "use_google_fonts_cdn"      : True,
    "show_ui_builder"           : False,
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text"     : False,
    "footer_small_text"     : False,
    "body_small_text"       : False,
    "brand_small_text"      : False,
    "brand_colour"          : "navbar-warning",
    "accent"                : "accent-warning",
    "navbar"                : "navbar-dark",
    "no_navbar_border"      : False,
    "navbar_fixed"          : True,
    "layout_boxed"          : False,
    "footer_fixed"          : False,
    "sidebar_fixed"         : True,
    "sidebar"               : "sidebar-dark-warning",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent" : True,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style" : False,
    "sidebar_nav_flat_style"   : False,
    "theme"                 : "flatly",
    "dark_mode_theme"       : "darkly",
    "button_classes": {
        "primary"  : "btn-primary",
        "secondary": "btn-secondary",
        "info"     : "btn-outline-info",
        "warning"  : "btn-warning",
        "danger"   : "btn-danger",
        "success"  : "btn-success",
    },
}

WSGI_APPLICATION = 'recipe_platform.wsgi.application'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'accounts.User'

# DRF global config
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# SimpleJWT config
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# Cloudinary config
CLOUDINARY_STORAGE = {
    'CLOUD_NAME' : config('CLOUDINARY_CLOUD_NAME', default=''),
    'API_KEY'    : config('CLOUDINARY_API_KEY', default=''),
    'API_SECRET' : config('CLOUDINARY_API_SECRET', default=''),
}

# Tell Django to use Cloudinary for media files
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'