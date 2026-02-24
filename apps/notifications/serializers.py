"""
Serializers for the notifications app.
"""
from rest_framework import serializers
from apps.notifications.models import Notification, NotificationPreferences


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for user notifications."""

    class Meta:
        model = Notification
        fields = [
            'id', 'type', 'title', 'message',
            'related_type', 'related_id',
            'is_read', 'read_at', 'created_at',
        ]
        read_only_fields = ['id', 'type', 'title', 'message', 'related_type', 'related_id', 'read_at', 'created_at']


class NotificationMarkReadSerializer(serializers.Serializer):
    """Serializer to mark one or many notifications as read."""

    notification_ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False,
    )


class NotificationPreferencesSerializer(serializers.ModelSerializer):
    """Serializer for user notification preferences."""

    class Meta:
        model = NotificationPreferences
        fields = [
            'email_call_published', 'email_target_hit',
            'email_stop_loss_hit', 'email_call_updated', 'email_portfolio_alert',
            'app_call_published', 'app_target_hit',
            'app_stop_loss_hit', 'app_call_updated', 'app_portfolio_alert',
            'sms_target_hit', 'sms_stop_loss_hit',
            'updated_at',
        ]
        read_only_fields = ['updated_at']
