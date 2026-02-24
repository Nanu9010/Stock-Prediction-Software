"""
URL configuration for the brokers app.
"""
from django.urls import path
from apps.brokers import views

app_name = 'brokers'

urlpatterns = [
    # Public endpoints
    path('', views.BrokerListView.as_view(), name='broker-list'),
    path('<int:pk>/', views.BrokerDetailView.as_view(), name='broker-detail'),
    path('<int:pk>/metrics/', views.BrokerPerformanceMetricsView.as_view(), name='broker-metrics'),

    # Admin endpoints
    path('admin/', views.AdminBrokerListCreateView.as_view(), name='admin-broker-list'),
    path('admin/<int:pk>/', views.AdminBrokerDetailView.as_view(), name='admin-broker-detail'),
]
