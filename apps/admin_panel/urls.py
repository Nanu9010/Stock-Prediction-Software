"""
Admin Panel URLs
"""
from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    # Dashboard
    path('', views.AdminDashboardView.as_view(), name='dashboard'),
    
    # Research Calls
    path('calls/', views.CallListView.as_view(), name='calls_list'),
    path('calls/create/', views.CallCreateView.as_view(), name='call_create'),
    path('calls/<int:pk>/', views.CallDetailView.as_view(), name='call_detail'),
    path('calls/<int:pk>/edit/', views.CallUpdateView.as_view(), name='call_update'),
    path('calls/<int:pk>/delete/', views.CallDeleteView.as_view(), name='call_delete'),
    
    # Brokers
    path('brokers/', views.BrokerListView.as_view(), name='brokers_list'),
    path('brokers/create/', views.BrokerCreateView.as_view(), name='broker_create'),
    path('brokers/<int:pk>/', views.BrokerDetailView.as_view(), name='broker_detail'),
    path('brokers/<int:pk>/edit/', views.BrokerUpdateView.as_view(), name='broker_update'),
    
    # Users
    path('users/', views.UserListView.as_view(), name='users_list'),
    path('users/<int:pk>/', views.UserDetailView.as_view(), name='user_detail'),
    path('users/<int:pk>/edit/', views.UserUpdateView.as_view(), name='user_update'),
    path('users/<int:pk>/delete/', views.UserDeleteView.as_view(), name='user_delete'),
    
    # Portfolios
    path('portfolios/', views.PortfolioListView.as_view(), name='portfolios_list'),
    path('portfolios/<int:pk>/', views.PortfolioDetailView.as_view(), name='portfolio_detail'),
    path('portfolios/<int:pk>/delete/', views.PortfolioDeleteView.as_view(), name='portfolio_delete'),
    
    # Watchlists
    path('watchlists/', views.WatchlistListView.as_view(), name='watchlists_list'),
    path('watchlists/<int:pk>/', views.WatchlistDetailView.as_view(), name='watchlist_detail'),
    path('watchlists/<int:pk>/delete/', views.WatchlistDeleteView.as_view(), name='watchlist_delete'),
    
    # Subscription Plans
    path('subscriptions/', views.SubscriptionPlanListView.as_view(), name='subscriptions_list'),
    path('subscriptions/create/', views.SubscriptionPlanCreateView.as_view(), name='subscription_create'),
    path('subscriptions/<int:pk>/edit/', views.SubscriptionPlanUpdateView.as_view(), name='subscription_update'),
    path('subscriptions/<int:pk>/delete/', views.SubscriptionPlanDeleteView.as_view(), name='subscription_delete'),
    
    # Payments (read-only)
    path('payments/', views.PaymentListView.as_view(), name='payments_list'),
    path('payments/<int:pk>/', views.PaymentDetailView.as_view(), name='payment_detail'),
]
