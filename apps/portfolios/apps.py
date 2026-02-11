from django.apps import AppConfig

class PortfoliosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.portfolios'
    verbose_name = 'Portfolios'

class WatchlistsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.watchlists'
    verbose_name = 'Watchlists'

class SubscriptionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.subscriptions'
    verbose_name = 'Subscriptions'

class NotificationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.notifications'
    verbose_name = 'Notifications'

class AnalyticsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.analytics'
    verbose_name = 'Analytics'

class DashboardConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.dashboard'
    verbose_name = 'Dashboard'

class AuditConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.audit'
    verbose_name = 'Audit'

class LifecycleConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.lifecycle'
    verbose_name = 'Lifecycle'

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.core'
    verbose_name = 'Core'
