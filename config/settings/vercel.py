from .production import *

# Vercel-specific settings
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['.vercel.app', 'localhost', '127.0.0.1', 'now.sh'])

# Logging to console for Vercel
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Use database for session if Redis is not available
if not os.environ.get('REDIS_URL'):
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    }
    SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# Database fallback for build time (Vercel build doesn't always have DB)
if os.environ.get('VERCEL'):
    # If DB vars are missing, use a dummy DB for build time
    if not os.environ.get('DB_NAME'):
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': BASE_DIR / 'db.sqlite3',
            }
        }

# Vercel handles SSL termination
SECURE_SSL_REDIRECT = os.environ.get('SECURE_SSL_REDIRECT', 'False') == 'True'
