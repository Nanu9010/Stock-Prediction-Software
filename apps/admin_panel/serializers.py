"""
Serializers for the admin_panel app.
Admin panel manages all entities — these serializers power its API endpoints.
"""
from rest_framework import serializers
from apps.authentication.models import User
from apps.brokers.models import Broker
from apps.research_calls.models import ResearchCall


class AdminUserSerializer(serializers.ModelSerializer):
    """Admin view of a user — includes role and all status flags."""

    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'email', 'full_name', 'first_name', 'last_name', 'mobile',
            'role', 'is_active', 'is_staff', 'is_email_verified',
            'last_login_at', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def get_full_name(self, obj):
        return obj.get_full_name()


class AdminBrokerSerializer(serializers.ModelSerializer):
    """Admin view of a broker (includes all fields)."""

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


class AdminCallApprovalSerializer(serializers.ModelSerializer):
    """Serializer for admin to approve/reject a research call."""

    class Meta:
        model = ResearchCall
        fields = ['status']

    def validate_status(self, value):
        allowed = ['APPROVED', 'REJECTED']
        if value not in allowed:
            raise serializers.ValidationError(f'Status must be one of {allowed}')
        return value


class AdminStatsSerializer(serializers.Serializer):
    """Summary stats for the admin dashboard."""

    total_users = serializers.IntegerField()
    total_brokers = serializers.IntegerField()
    total_calls = serializers.IntegerField()
    active_calls = serializers.IntegerField()
    pending_approval_calls = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=15, decimal_places=2)
