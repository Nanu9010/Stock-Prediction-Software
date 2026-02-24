"""
URL configuration for the core app.
"""
from django.urls import path
from apps.core import views
from apps.core.ticker_views import LiveTickerView

app_name = 'core'

urlpatterns = [
    # Utility endpoints
    path('health/', views.HealthCheckView.as_view(), name='health-check'),
    path('info/', views.APIInfoView.as_view(), name='api-info'),
    # Live market ticker (uses yfinance, 60s cache)
    path('live-ticker/', LiveTickerView.as_view(), name='live-ticker'),
]

