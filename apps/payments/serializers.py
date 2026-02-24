"""
Serializers for the payments app.
"""
from rest_framework import serializers
from apps.payments.models import SubscriptionPlan, Payment, Subscription


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    """Serializer for payment subscription plans."""

    class Meta:
        model = SubscriptionPlan
        fields = [
            'id', 'name', 'plan_type',
            'price_monthly', 'price_yearly',
            'features', 'max_calls_per_month',
            'is_active', 'display_order',
        ]
        read_only_fields = ['id']


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for payment transactions (read-only for users)."""

    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id', 'user_email',
            'razorpay_order_id', 'razorpay_payment_id',
            'amount', 'currency', 'status', 'payment_method',
            'description', 'receipt',
            'created_at', 'paid_at',
        ]
        read_only_fields = [
            'id', 'user_email', 'razorpay_order_id', 'razorpay_payment_id',
            'razorpay_signature', 'status', 'created_at', 'paid_at',
        ]


class PaymentCreateSerializer(serializers.Serializer):
    """Serializer for initiating a new payment / order."""

    plan_type = serializers.ChoiceField(choices=['BASIC', 'PRO', 'PREMIUM'])
    billing_cycle = serializers.ChoiceField(choices=['MONTHLY', 'YEARLY'])


class SubscriptionSerializer(serializers.ModelSerializer):
    """Serializer for user subscriptions."""

    user_email = serializers.EmailField(source='user.email', read_only=True)
    is_currently_active = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = [
            'id', 'user_email', 'plan_type', 'billing_cycle',
            'amount', 'start_date', 'end_date',
            'status', 'auto_renew',
            'razorpay_subscription_id',
            'is_currently_active',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'user_email', 'status', 'created_at', 'updated_at']

    def get_is_currently_active(self, obj):
        return obj.is_active()
