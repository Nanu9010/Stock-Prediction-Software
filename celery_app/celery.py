import os
from celery import Celery
from celery.schedules import crontab

# Set default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('stock_research_platform')

# Load configuration from Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in all installed apps
app.autodiscover_tasks()

# Periodic tasks schedule
app.conf.beat_schedule = {
    'update-market-indices': {
        'task': 'apps.market_data.tasks.task_update_indices',
        'schedule': 180.0,  # 3 minutes
    },
    'update-gainers-losers-active': {
        'task': 'apps.market_data.tasks.task_update_gainers_active',
        'schedule': 300.0,  # 5 minutes
    },
    'update-popular-stocks': {
        'task': 'apps.market_data.tasks.task_update_popular_stocks',
        'schedule': 600.0,  # 10 minutes
    },
}

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
