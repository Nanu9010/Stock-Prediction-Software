from django.urls import path
from apps.dashboard import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('dashboard/', views.dashboard_home_view, name='dashboard'),
    path('markets/', views.markets_view, name='markets'),
    path('pro-trades/', views.pro_trades_view, name='pro_trades'),
    path('pro-baskets/', views.pro_baskets_view, name='pro_baskets'),
    path('ipo/', views.ipo_view, name='ipo'),
    path('explore/', views.explore_view, name='explore'),
]
