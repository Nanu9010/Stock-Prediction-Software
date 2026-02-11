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
]
