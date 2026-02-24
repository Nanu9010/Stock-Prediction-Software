from django.urls import path
from apps.dashboard import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.landing_page_view, name='landing'),  # redirects to /app/
    path('app/', views.dashboard_home_view, name='dashboard'),
    path('markets/', views.markets_view, name='markets'),
    path('pro-trades/', views.pro_trades_view, name='pro_trades'),
    path('pro-baskets/', views.pro_baskets_view, name='pro_baskets'),
    path('ipo/', views.ipo_view, name='ipo'),
    path('explore/', views.explore_view, name='explore'),

    # New market sections
    path('sip/', views.sip_view, name='sip'),
    path('mutual-funds/', views.mutual_funds_view, name='mutual_funds'),
    path('etf/', views.etf_view, name='etf'),
    path('bonds/', views.bonds_view, name='bonds'),
    path('liquidity/', views.liquidity_view, name='liquidity'),
    path('commodity/', views.commodity_view, name='commodity'),
    path('trades-dashboard/', views.trades_dashboard_view, name='trades_dashboard'),
    path('gainers-losers/', views.gainers_losers_view, name='gainers_losers'),
    path('recently-listed/', views.recently_listed_view, name='recently_listed'),
    path('top-brokers/', views.top_brokers_view, name='top_brokers'),
]
