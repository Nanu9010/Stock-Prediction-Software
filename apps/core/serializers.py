"""
Serializers for the core app.
Core provides utilities — no database models — so these are utility serializers.
"""
from rest_framework import serializers


class HealthCheckSerializer(serializers.Serializer):
    """Serializer for the API health check response."""

    status = serializers.CharField(default='ok')
    version = serializers.CharField()
    timestamp = serializers.DateTimeField()


class PaginationSerializer(serializers.Serializer):
    """Generic serializer representing a paginated API response shape."""

    count = serializers.IntegerField()
    next = serializers.URLField(allow_null=True)
    previous = serializers.URLField(allow_null=True)
    results = serializers.ListField()


class ErrorResponseSerializer(serializers.Serializer):
    """Standard error response shape used across all apps."""

    error = serializers.CharField()
    detail = serializers.CharField(required=False)
    code = serializers.CharField(required=False)
