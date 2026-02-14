"""
URL configuration for trades app
"""
from django.urls import path
from apps.trades import views

app_name = 'trades'

urlpatterns = [
    path('short-term/', views.trade_list_view, {'trade_type': 'short-term'}, name='short_term'),
    path('medium-term/', views.trade_list_view, {'trade_type': 'medium-term'}, name='medium_term'),
    path('long-term/', views.trade_list_view, {'trade_type': 'long-term'}, name='long_term'),
    path('futures/', views.trade_list_view, {'trade_type': 'futures'}, name='futures'),
    path('options/', views.trade_list_view, {'trade_type': 'options'}, name='options'),
    path('commodity/', views.trade_list_view, {'trade_type': 'commodity'}, name='commodity'),
]
