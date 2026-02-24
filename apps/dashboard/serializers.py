"""
Serializers for the dashboard app.
The dashboard is view-only and aggregates data from other apps.
These serializers are used for API responses.
"""
from rest_framework import serializers


class DashboardStatsSerializer(serializers.Serializer):
    """Serializer for dashboard summary statistics."""

    total_calls = serializers.IntegerField()
    active_calls = serializers.IntegerField()
    successful_calls = serializers.IntegerField()
    accuracy_percentage = serializers.FloatField()
    total_brokers = serializers.IntegerField()
    total_customers = serializers.IntegerField()


class CustomerDashboardSerializer(serializers.Serializer):
    """Serializer for customer-specific dashboard data."""

    portfolio_value = serializers.DecimalField(max_digits=15, decimal_places=2)
    portfolio_pnl = serializers.DecimalField(max_digits=15, decimal_places=2)
    portfolio_pnl_percentage = serializers.DecimalField(max_digits=10, decimal_places=2)
    active_portfolio_items = serializers.IntegerField()
    watchlist_count = serializers.IntegerField()
    unread_notifications = serializers.IntegerField()
    active_subscription_plan = serializers.CharField(allow_null=True)
    subscription_end_date = serializers.DateField(allow_null=True)
