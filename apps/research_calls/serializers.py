"""
Serializers for the research_calls app.
"""
from rest_framework import serializers

from apps.brokers.serializers import BrokerSerializer
from apps.research_calls.models import ResearchCall, ResearchCallEvent, ResearchCallVersion


class ResearchCallEventSerializer(serializers.ModelSerializer):
    """Read-only serializer for call lifecycle events."""

    triggered_by_email = serializers.EmailField(source='triggered_by.email', read_only=True)

    class Meta:
        model = ResearchCallEvent
        fields = ['id', 'event_type', 'notes', 'triggered_by_email', 'created_at']
        read_only_fields = fields


class ResearchCallVersionSerializer(serializers.ModelSerializer):
    """Read-only serializer for research call edit history."""

    changed_by_email = serializers.EmailField(source='changed_by.email', read_only=True)

    class Meta:
        model = ResearchCallVersion
        fields = ['id', 'version_number', 'changes_json', 'change_reason', 'changed_by_email', 'created_at']
        read_only_fields = fields


class ResearchCallSerializer(serializers.ModelSerializer):
    """Detailed serializer for a single research call."""

    broker = BrokerSerializer(read_only=True)
    created_by_email = serializers.EmailField(source='created_by.email', read_only=True)
    events = ResearchCallEventSerializer(many=True, read_only=True)

    class Meta:
        model = ResearchCall
        fields = [
            'id', 'broker', 'created_by_email',
            'symbol', 'exchange', 'company_name', 'sector',
            'call_type', 'instrument_type', 'action',
            'entry_price', 'target_1', 'target_2', 'target_3', 'stop_loss',
            'timeframe_days', 'expected_return_percentage', 'risk_reward_ratio', 'rationale',
            'status', 'published_at', 'expires_at', 'closed_at',
            'actual_return_percentage', 'is_successful', 'exit_price', 'exit_reason',
            'version', 'created_at', 'updated_at', 'events',
        ]
        read_only_fields = [
            'id', 'created_by_email', 'expected_return_percentage', 'risk_reward_ratio',
            'published_at', 'closed_at', 'actual_return_percentage', 'is_successful',
            'version', 'created_at', 'updated_at', 'events',
        ]


class ResearchCallListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views."""

    broker_name = serializers.CharField(source='broker.name', read_only=True)

    class Meta:
        model = ResearchCall
        fields = [
            'id', 'symbol', 'company_name', 'broker_name',
            'call_type', 'instrument_type', 'action',
            'entry_price', 'target_1', 'stop_loss',
            'status', 'published_at',
        ]
        read_only_fields = fields


class ResearchCallCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new research call."""

    class Meta:
        model = ResearchCall
        fields = [
            'broker', 'symbol', 'exchange', 'company_name', 'sector',
            'call_type', 'instrument_type', 'action',
            'entry_price', 'target_1', 'target_2', 'target_3', 'stop_loss',
            'timeframe_days', 'rationale', 'expires_at',
        ]
