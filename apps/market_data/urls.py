"""
Market data URLs
"""
from django.urls import path
from apps.market_data import views

app_name = 'market_data'

urlpatterns = [
    path('indices/', views.market_indices_view, name='indices'),
    path('stocks/', views.popular_stocks_view, name='popular_stocks'),
    path('api/', views.market_data_api, name='api'),
    path('update/', views.update_market_data_view, name='update'),
]
