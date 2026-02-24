"""
Serializers for the audit app.
"""
from rest_framework import serializers
from apps.audit.models import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
    """Read-only serializer for audit log entries."""

    user_email = serializers.EmailField(source='user.email', read_only=True, default=None)

    class Meta:
        model = AuditLog
        fields = [
            'id', 'user_email', 'action',
            'model_name', 'object_id', 'object_repr',
            'changes_json', 'ip_address',
            'created_at',
        ]
        read_only_fields = fields
