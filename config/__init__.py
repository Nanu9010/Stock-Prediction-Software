# Configure pymysql to work as MySQLdb for Django
import pymysql
pymysql.install_as_MySQLdb()

# This will make sure the Celery app is always imported when
# Django starts so that shared_task will use this app.
try:
    from celery_app import celery_app
    __all__ = ('celery_app',)
except ImportError:
    # Celery not installed or configured
    pass

