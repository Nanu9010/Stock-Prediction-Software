"""
Serializers for the subscriptions app.
"""
from rest_framework import serializers

from apps.payments.models import Subscription, SubscriptionPlan


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    """Serializer for public/admin subscription plan display."""

    class Meta:
        model = SubscriptionPlan
        fields = [
            'id', 'name', 'plan_type',
            'price_monthly', 'price_yearly',
            'features', 'max_calls_per_month',
            'display_order', 'is_active',
        ]
        read_only_fields = ['id']


class SubscriptionRecordSerializer(serializers.ModelSerializer):
    """Serializer for a user's subscription record."""

    user_email = serializers.EmailField(source='user.email', read_only=True)
    payment_id = serializers.IntegerField(source='payment_id', read_only=True)
    is_currently_active = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = [
            'id', 'user_email', 'plan_type', 'billing_cycle',
            'amount', 'status', 'start_date', 'end_date',
            'payment_id', 'auto_renew',
            'is_currently_active',
            'created_at',
        ]
        read_only_fields = ['id', 'user_email', 'created_at']

    def get_is_currently_active(self, obj):
        return obj.is_active()
