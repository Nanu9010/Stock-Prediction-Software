"""
Serializers for the trades app.
Trades are read from research_calls; this app provides trade-tracking views.
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
            'actual_entry_price', 'actual_exit_price', 'actual_return_percentage',
            'status', 'is_successful',
            'published_at', 'closed_at', 'duration',
        ]
        read_only_fields = fields

    def get_duration(self, obj):
        if obj.published_at and obj.closed_at:
            delta = obj.closed_at - obj.published_at
            return delta.days
        return None


class TradeFilterSerializer(serializers.Serializer):
    """Serializer for filtering trades."""

    call_type = serializers.ChoiceField(
        choices=['INTRADAY', 'SWING', 'SHORT_TERM', 'MEDIUM_TERM', 'LONG_TERM'],
        required=False,
    )
    status = serializers.ChoiceField(
        choices=['DRAFT', 'PENDING_APPROVAL', 'APPROVED', 'ACTIVE', 'CLOSED', 'REJECTED', 'EXPIRED'],
        required=False,
    )
    broker_id = serializers.IntegerField(required=False)
    from_date = serializers.DateField(required=False)
    to_date = serializers.DateField(required=False)
