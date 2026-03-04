"""
Serializers for the trades app.
Trades are represented by ResearchCall records.
"""
from rest_framework import serializers

from apps.research_calls.models import ResearchCall


class TradeSerializer(serializers.ModelSerializer):
    """Serializer exposing research calls as trade records."""

    broker_name = serializers.CharField(source='broker.name', read_only=True)
    duration = serializers.SerializerMethodField()

    class Meta:
        model = ResearchCall
        fields = [
            'id', 'symbol', 'company_name', 'broker_name',
            'call_type', 'instrument_type', 'action', 'sector',
            'entry_price', 'target_1', 'target_2', 'target_3', 'stop_loss',
            'exit_price', 'actual_return_percentage',
            'status', 'is_successful',
            'published_at', 'closed_at', 'duration',
        ]
        read_only_fields = fields

    def get_duration(self, obj):
        if obj.published_at and obj.closed_at:
            return (obj.closed_at - obj.published_at).days
        return None


class TradeFilterSerializer(serializers.Serializer):
    """Serializer for filtering trades."""

    call_type = serializers.ChoiceField(
        choices=['INTRADAY', 'SWING', 'SHORT_TERM', 'MEDIUM_TERM', 'LONG_TERM', 'POSITIONAL'],
        required=False,
    )
    status = serializers.ChoiceField(
        choices=[
            'DRAFT', 'PENDING_APPROVAL', 'APPROVED', 'PUBLISHED', 'ACTIVE',
            'TARGET_1_HIT', 'TARGET_2_HIT', 'TARGET_3_HIT',
            'STOP_LOSS_HIT', 'MANUALLY_EXITED', 'EXPIRED', 'CLOSED',
        ],
        required=False,
    )
    broker_id = serializers.IntegerField(required=False)
    from_date = serializers.DateField(required=False)
    to_date = serializers.DateField(required=False)
