"""
URL configuration for trades app
"""
from django.urls import path
from apps.trades import views

app_name = 'trades'

urlpatterns = [
    path('short-term/', views.short_term_trades_view, name='short_term'),
    path('medium-term/', views.medium_term_trades_view, name='medium_term'),
    path('long-term/', views.long_term_trades_view, name='long_term'),
    path('futures/', views.futures_trades_view, name='futures'),
    path('options/', views.options_trades_view, name='options'),
    path('commodity/', views.commodity_trades_view, name='commodity'),
]
