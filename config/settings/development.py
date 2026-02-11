# Configure pymysql to work as MySQLdb
import pymysql
pymysql.install_as_MySQLdb()

from .base import *

# Development settings
DEBUG = True

# Allow all hosts in development
ALLOWED_HOSTS = ['*']

# Use MySQL database from base.py (no override needed)

# Use console email backend in development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Django Debug Toolbar
INSTALLED_APPS += ['debug_toolbar']
MIDDLEWARE = ['debug_toolbar.middleware.DebugToolbarMiddleware'] + MIDDLEWARE

INTERNAL_IPS = [
    '127.0.0.1',
    'localhost',
]

# Disable security features in development
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
