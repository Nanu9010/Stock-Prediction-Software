"""
Market data app for fetching real-time stock prices using free APIs
"""
from django.apps import AppConfig


class MarketDataConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.market_data'
    verbose_name = 'Market Data'
