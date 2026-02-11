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
    'monitor-active-calls': {
        'task': 'apps.lifecycle.tasks.monitor_active_calls',
        'schedule': 300.0,  # Every 5 minutes
    },
    'update-portfolio-values': {
        'task': 'apps.portfolios.tasks.update_all_portfolio_values',
        'schedule': 300.0,  # Every 5 minutes
    },
    'calculate-daily-broker-metrics': {
        'task': 'apps.analytics.tasks.calculate_daily_broker_metrics',
        'schedule': crontab(hour=23, minute=0),  # Daily at 11 PM IST
    },
    'expire-old-calls': {
        'task': 'apps.research_calls.tasks.expire_old_calls',
        'schedule': crontab(hour=0, minute=0),  # Daily at midnight
    },
}

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
