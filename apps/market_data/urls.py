"""
Market data URLs — existing views + new focused API endpoints
"""
from django.urls import path
from apps.market_data import views
from apps.market_data.api_views import TickerAPIView, MoversAPIView, MostActiveAPIView

app_name = 'market_data'

urlpatterns = [
    # Existing HTML/legacy views
    path('indices/', views.market_indices_view, name='indices'),
    path('stocks/', views.popular_stocks_view, name='popular_stocks'),
    path('api/', views.market_data_api, name='api'),  # kept for backward compat
    path('update/', views.update_market_data_view, name='update'),

    # New focused JSON APIs
    path('api/ticker/', TickerAPIView.as_view(), name='api_ticker'),
    path('api/movers/', MoversAPIView.as_view(), name='api_movers'),
    path('api/active/', MostActiveAPIView.as_view(), name='api_active'),
]
