"""
URL configuration for the audit app.
"""
from django.urls import path
from apps.audit import views

app_name = 'audit'

urlpatterns = [
    # Admin: all logs
    path('logs/', views.AuditLogListView.as_view(), name='log-list'),
    path('logs/<int:pk>/', views.AuditLogDetailView.as_view(), name='log-detail'),

    # Customer: own logs
    path('my-logs/', views.MyAuditLogListView.as_view(), name='my-log-list'),
]
