"""
Views for the notifications app.
Authenticated users can list, read, and mark notifications as read.
They can also manage their notification preferences.
"""
from django.utils import timezone
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.notifications.models import Notification, NotificationPreferences
from apps.notifications.serializers import (
    NotificationSerializer,
    NotificationMarkReadSerializer,
    NotificationPreferencesSerializer,
)


@method_decorator(login_required, name='dispatch')
class NotificationsPageView(View):
    """
    GET /notifications/
    Renders the HTML notifications page. Data is loaded via JS → REST API.
    """
    def get(self, request):
        return render(request, 'notifications/list.html')


class NotificationListView(generics.ListAPIView):
    """
    GET /api/notifications/
    Returns current user's notifications (paginated), newest first.
    """
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Notification.objects.filter(user=self.request.user)
        # Optional ?unread=1 filter
        if self.request.query_params.get('unread') == '1':
            qs = qs.filter(is_read=False)
        return qs


class NotificationMarkReadView(APIView):
    """
    POST /api/notifications/mark-read/
    Body: { "notification_ids": [1, 2, 3] }
    Marks the specified notifications as read.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = NotificationMarkReadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ids = serializer.validated_data['notification_ids']
        updated = Notification.objects.filter(
            id__in=ids,
            user=request.user,
            is_read=False,
        ).update(is_read=True, read_at=timezone.now())
        return Response({'marked_read': updated})


class NotificationMarkAllReadView(APIView):
    """
    POST /api/notifications/mark-all-read/
    Marks all unread notifications for the current user as read.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        updated = Notification.objects.filter(
            user=request.user,
            is_read=False,
        ).update(is_read=True, read_at=timezone.now())
        return Response({'marked_read': updated})


class NotificationPreferencesView(generics.RetrieveUpdateAPIView):
    """
    GET   /api/notifications/preferences/  — retrieve user's preferences
    PATCH /api/notifications/preferences/  — update user's preferences
    """
    serializer_class = NotificationPreferencesSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        prefs, _ = NotificationPreferences.objects.get_or_create(user=self.request.user)
        return prefs


class UnreadNotificationCountView(APIView):
    """
    GET /api/notifications/unread-count/
    Returns count of unread notifications for the current user.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        count = Notification.objects.filter(user=request.user, is_read=False).count()
        return Response({'unread_count': count})
