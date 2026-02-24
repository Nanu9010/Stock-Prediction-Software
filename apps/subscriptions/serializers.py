"""
Serializers for the subscriptions app.
"""
from rest_framework import serializers
from apps.subscriptions.models import SubscriptionPlan, UserSubscription


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    """Serializer for subscription plan display."""

    class Meta:
        model = SubscriptionPlan
        fields = [
            'id', 'name', 'slug', 'description',
            'price_monthly', 'price_yearly',
            'access_intraday', 'access_swing', 'access_shortterm',
            'access_longterm', 'access_futures', 'access_options',
            'features_json', 'display_order',
            'is_active', 'is_featured',
        ]
        read_only_fields = ['id', 'slug']


class UserSubscriptionSerializer(serializers.ModelSerializer):
    """Serializer for a user's subscription record."""

    plan = SubscriptionPlanSerializer(read_only=True)
    plan_id = serializers.PrimaryKeyRelatedField(
        queryset=SubscriptionPlan.objects.filter(is_active=True),
        source='plan',
        write_only=True,
    )
    user_email = serializers.EmailField(source='user.email', read_only=True)
    is_expired = serializers.SerializerMethodField()

    class Meta:
        model = UserSubscription
        fields = [
            'id', 'user_email', 'plan', 'plan_id',
            'status', 'start_date', 'end_date',
            'payment_id', 'amount_paid',
            'auto_renewal', 'is_expired',
            'created_at',
        ]
        read_only_fields = ['id', 'user_email', 'status', 'created_at']

    def get_is_expired(self, obj):
        from django.utils import timezone
        return obj.end_date < timezone.now().date() if obj.end_date else True
