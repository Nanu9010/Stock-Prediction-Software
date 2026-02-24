"""
Serializers for the brokers app.
"""
from rest_framework import serializers
from apps.brokers.models import Broker, BrokerPerformanceMetrics


class BrokerPerformanceMetricsSerializer(serializers.ModelSerializer):
    """Serializer for broker daily performance metrics."""

    class Meta:
        model = BrokerPerformanceMetrics
        fields = [
            'id', 'metric_date',
            'total_closed_calls', 'successful_calls', 'accuracy_percentage',
            'avg_return_percentage',
            'intraday_accuracy', 'swing_accuracy', 'shortterm_accuracy', 'longterm_accuracy',
            'created_at',
        ]
        read_only_fields = fields


class BrokerSerializer(serializers.ModelSerializer):
    """Serializer for Broker — used for list and detail views."""

    class Meta:
        model = Broker
        fields = [
            'id', 'name', 'slug', 'description', 'logo',
            'website_url', 'sebi_registration_no',
            'overall_accuracy', 'total_calls_published', 'total_calls_closed',
            'avg_return_percentage', 'is_active', 'is_verified',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']


class BrokerCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating a Broker (admin only)."""

    class Meta:
        model = Broker
        fields = [
            'name', 'description', 'logo',
            'website_url', 'sebi_registration_no',
            'is_active', 'is_verified',
        ]
