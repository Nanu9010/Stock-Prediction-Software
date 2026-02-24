"""
URL configuration for the notifications app.
"""
from django.urls import path
from apps.notifications import views

app_name = 'notifications'

urlpatterns = [
    # ── HTML page ──
    path('inbox/', views.NotificationsPageView.as_view(), name='inbox'),

    # ── REST API ──
    # Notification list (supports ?unread=1 filter)
    path('', views.NotificationListView.as_view(), name='notification-list'),
    # Mark read actions
    path('mark-read/', views.NotificationMarkReadView.as_view(), name='mark-read'),
    path('mark-all-read/', views.NotificationMarkAllReadView.as_view(), name='mark-all-read'),
    # Unread count
    path('unread-count/', views.UnreadNotificationCountView.as_view(), name='unread-count'),
    # Preferences
    path('preferences/', views.NotificationPreferencesView.as_view(), name='preferences'),
]
