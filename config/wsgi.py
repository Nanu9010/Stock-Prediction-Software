"""
WSGI config for production deployment
"""
import os
import sys
from types import ModuleType

# Mock pkg_resources for razorpay and other old libraries
if 'pkg_resources' not in sys.modules:
    mock_pkg_resources = ModuleType('pkg_resources')
    class MockDistribution:
        def __init__(self): self.version = '1.4.1'
    def get_distribution(name): return MockDistribution()
    mock_pkg_resources.get_distribution = get_distribution
    sys.modules['pkg_resources'] = mock_pkg_resources
    print("pkg_resources mocked successfully")

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', os.environ.get('DJANGO_SETTINGS_MODULE', 'config.settings.production'))

application = get_wsgi_application()
