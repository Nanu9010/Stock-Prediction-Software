"""
WSGI config for production deployment
"""
import os
try:
    import pkg_resources
    print("pkg_resources available")
except ImportError:
    print("pkg_resources NOT available")
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', os.environ.get('DJANGO_SETTINGS_MODULE', 'config.settings.production'))

application = get_wsgi_application()
