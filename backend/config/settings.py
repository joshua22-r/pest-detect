import os
from pathlib import Path
from datetime import timedelta
from decouple import config
from django.core.exceptions import ImproperlyConfigured
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

# Sentry Configuration
sentry_sdk.init(
    dsn=config('SENTRY_DSN', default=''),
    integrations=[DjangoIntegration()],
    traces_sample_rate=1.0,
    send_default_pii=True,
    environment=config('ENVIRONMENT', default='development'),
)

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY', default='django-insecure-your-secret-key-change-in-production')

DEBUG = config('DEBUG', default=True, cast=bool)
USE_HTTPS = config('USE_HTTPS', default=False, cast=bool)
ENVIRONMENT = config('ENVIRONMENT', default='development').lower()
FRONTEND_URL = config('FRONTEND_URL', default='http://localhost:3000')

if ENVIRONMENT == 'production':
    if DEBUG:
        raise ImproperlyConfigured('DEBUG must be False in production.')
    if not USE_HTTPS:
        raise ImproperlyConfigured('USE_HTTPS must be True in production.')
    if not SECRET_KEY or SECRET_KEY.startswith('django-insecure'):
        raise ImproperlyConfigured(
            'A secure SECRET_KEY must be set in production. Do not use the default insecure key.'
        )

ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS',
    default='localhost,127.0.0.1,bioguard-backend.onrender.com,bioguard-backend-7vik.onrender.com,*.onrender.com',
    cast=lambda v: [s.strip() for s in v.split(',')],
)

# Check if Redis is available for rate limiting
REDIS_URL = config('REDIS_URL', default='')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'djcelery_email',
    'django_otp',
    'django_otp.plugins.otp_totp',
    'django_otp.plugins.otp_static',
    'api',
]

# Only include django_ratelimit if Redis is available (required for shared cache)
if REDIS_URL:
    INSTALLED_APPS.insert(7, 'django_ratelimit')

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django_otp.middleware.OTPMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'api.middleware.SecurityHeadersMiddleware',
    'api.middleware.SessionManagementMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Only include RatelimitMiddleware if Redis is available
if REDIS_URL:
    MIDDLEWARE.insert(9, 'django_ratelimit.middleware.RatelimitMiddleware')

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database Configuration - PostgreSQL in production, SQLite locally
import re

if ENVIRONMENT == 'production':
    # Try DATABASE_URL first (Render provides this)
    database_url = config('DATABASE_URL', default='')
    if database_url:
        # Check if it's a SQLite URL (for testing/development)
        if database_url.startswith('sqlite'):
            match = re.match(r'sqlite:///(.+)$', database_url)
            if match:
                db_path = match.group(1)
                DATABASES = {
                    'default': {
                        'ENGINE': 'django.db.backends.sqlite3',
                        'NAME': BASE_DIR / db_path if not db_path.startswith('/') else db_path,
                    }
                }
            else:
                DATABASES = {
                    'default': {
                        'ENGINE': 'django.db.backends.sqlite3',
                        'NAME': BASE_DIR / 'db.sqlite3',
                    }
                }
        else:
            # Parse PostgreSQL DATABASE_URL format: postgres://user:password@host:port/dbname
            match = re.match(r'postgres(?:\+psycopg2)?://(?:([^:@]+)(?::([^@]*))?@)?([^:@/]+)(?::(\d+))?/(.+)$', database_url)
            if match:
                db_user, db_password, db_host, db_port, db_name = match.groups()
                DATABASES = {
                    'default': {
                        'ENGINE': 'django.db.backends.postgresql',
                        'NAME': db_name,
                        'USER': db_user or 'postgres',
                        'PASSWORD': db_password or '',
                        'HOST': db_host,
                        'PORT': db_port or '5432',
                        'CONN_MAX_AGE': 600,
                        'OPTIONS': {'sslmode': 'require'},
                    }
                }
            else:
                raise ImproperlyConfigured(f'Invalid DATABASE_URL format: {database_url}')
    else:
        # Fallback to individual env vars
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': config('DB_NAME', default='pestdetect'),
                'USER': config('DB_USER', default='postgres'),
                'PASSWORD': config('DB_PASSWORD', default=''),
                'HOST': config('DB_HOST', default='localhost'),
                'PORT': config('DB_PORT', default='5432'),
                'CONN_MAX_AGE': 600,
                'OPTIONS': {'sslmode': 'require'},
            }
        }
else:
    # SQLite for local development
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
        'OPTIONS': {
            'user_attributes': ('username', 'first_name', 'last_name', 'email'),
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 12,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
    {
        'NAME': 'api.validators.CustomPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Ensure logs directory exists
LOGS_DIR = BASE_DIR / 'logs'
try:
    LOGS_DIR.mkdir(exist_ok=True)
except Exception:
    pass  # May not have permission on production

# Logging Configuration - with console output for production
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGS_DIR / 'django.log',
            'maxBytes': 1024 * 1024 * 10,
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'security_file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGS_DIR / 'security.log',
            'maxBytes': 1024 * 1024 * 10,
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'] if ENVIRONMENT == 'production' else ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django.security': {
            'handlers': ['console'] if ENVIRONMENT == 'production' else ['console', 'security_file'],
            'level': 'WARNING',
            'propagate': False,
        },
        'api': {
            'handlers': ['console'] if ENVIRONMENT == 'production' else ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Caching Configuration - Try Redis in production, fallback to dummy cache
redis_url = config('REDIS_URL', default='')
has_redis = bool(redis_url)

if ENVIRONMENT == 'production' and has_redis:
    # Use Redis if available (Render paid tier, recommended for production)
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': redis_url,
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                'IGNORE_EXCEPTIONS': False,
                'SOCKET_CONNECT_TIMEOUT': 10,
                'SOCKET_TIMEOUT': 10,
            },
        }
    }
    RATELIMIT_ENABLE = True
    RATELIMIT_FAIL_OPEN = False
else:
    # Fallback to dummy cache when Redis not available (free tier)
    # Dummy cache doesn't actually cache anything, which is safe but inefficient
    # Rate limiting will be disabled below
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
    }
    RATELIMIT_ENABLE = False  # Disable rate limiting without Redis
    RATELIMIT_FAIL_OPEN = True  # Safe default

# Rate limiting configuration
RATELIMIT_USE_CACHE = 'default'

# Security Settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=USE_HTTPS, cast=bool)
SESSION_COOKIE_SECURE = config('SESSION_COOKIE_SECURE', default=USE_HTTPS, cast=bool)
CSRF_COOKIE_SECURE = config('CSRF_COOKIE_SECURE', default=USE_HTTPS, cast=bool)
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SAMESITE = 'Lax'
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
SECURE_HSTS_SECONDS = config('SECURE_HSTS_SECONDS', default=31536000 if USE_HTTPS else 0, cast=int)
SECURE_HSTS_INCLUDE_SUBDOMAINS = config('SECURE_HSTS_INCLUDE_SUBDOMAINS', default=USE_HTTPS, cast=bool)
SECURE_HSTS_PRELOAD = config('SECURE_HSTS_PRELOAD', default=USE_HTTPS, cast=bool)
if USE_HTTPS:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
else:
    SECURE_PROXY_SSL_HEADER = None

# Session Management Settings
SESSION_COOKIE_AGE = 3600  # 1 hour session timeout
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_SAVE_EVERY_REQUEST = True
MAX_CONCURRENT_SESSIONS = 3  # Maximum concurrent sessions per user

# Password History (keep last 5 passwords)
PASSWORD_HISTORY_COUNT = 5

# REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# JWT Configuration
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
}

# CORS Configuration
CORS_ALLOWED_ORIGINS = [
    origin.strip() for origin in config(
        'CORS_ALLOWED_ORIGINS',
        default='http://localhost:3000,http://127.0.0.1:3000,http://localhost:8000,http://127.0.0.1:8000',
    ).split(',') if origin.strip()
]
CORS_ALLOWED_ORIGIN_REGEXES = [
    r'^https://.*\.stripe\.com$',
]
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]
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

CSRF_TRUSTED_ORIGINS = [FRONTEND_URL] if FRONTEND_URL else []

# Stripe Configuration
STRIPE_PUBLIC_KEY = config('STRIPE_PUBLIC_KEY', default='')
STRIPE_SECRET_KEY = config('STRIPE_SECRET_KEY', default='')
STRIPE_WEBHOOK_SECRET = config('STRIPE_WEBHOOK_SECRET', default='')

# Email Configuration
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_USE_SSL = config('EMAIL_USE_SSL', default=False, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@pestdetect.com')

# Frontend and social auth configuration
GOOGLE_CLIENT_ID = config('GOOGLE_CLIENT_ID', default='')
FACEBOOK_APP_ID = config('FACEBOOK_APP_ID', default='')
FACEBOOK_APP_SECRET = config('FACEBOOK_APP_SECRET', default='')

# Encryption key for data-at-rest protection
ENCRYPTION_KEY = config('ENCRYPTION_KEY', default=None)

# Celery Configuration (for background email sending)
# Only use Celery if Redis is available
if config('REDIS_URL', default=''):
    CELERY_BROKER_URL = config('REDIS_URL')
    CELERY_RESULT_BACKEND = config('REDIS_URL')
else:
    # Fallback to database backend if Redis not available
    CELERY_BROKER_URL = 'sqla+sqlite:///celery.db'
    CELERY_RESULT_BACKEND = 'db+sqlite:///celery.db'

CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_ALWAYS_EAGER = not config('REDIS_URL', default='')  # Run tasks sync if no Redis

# File Upload Configuration
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
