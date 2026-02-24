"""
Serializers for the portfolios app.
"""
from rest_framework import serializers
from apps.portfolios.models import Portfolio, PortfolioItem
from apps.research_calls.serializers import ResearchCallListSerializer


class PortfolioItemSerializer(serializers.ModelSerializer):
    """Serializer for individual portfolio holdings."""

    research_call = ResearchCallListSerializer(read_only=True)
    research_call_id = serializers.PrimaryKeyRelatedField(
        queryset=__import__('apps.research_calls.models', fromlist=['ResearchCall']).ResearchCall.objects.all(),
        source='research_call',
        write_only=True,
    )

    class Meta:
        model = PortfolioItem
        fields = [
            'id', 'research_call', 'research_call_id',
            'entry_price', 'quantity', 'entry_date', 'invested_amount',
            'current_price', 'current_value',
            'profit_loss', 'profit_loss_percentage',
            'exit_price', 'exit_date', 'exit_reason',
            'status', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'invested_amount', 'current_value',
            'profit_loss', 'profit_loss_percentage', 'created_at', 'updated_at',
        ]


class PortfolioSerializer(serializers.ModelSerializer):
    """Serializer for user portfolio — includes item list."""

    items = PortfolioItemSerializer(many=True, read_only=True)
    owner_email = serializers.EmailField(source='user.email', read_only=True)
    active_item_count = serializers.SerializerMethodField()

    class Meta:
        model = Portfolio
        fields = [
            'id', 'owner_email', 'name', 'description',
            'total_invested', 'current_value', 'profit_loss', 'profit_loss_percentage',
            'active_item_count', 'items',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'owner_email', 'total_invested', 'current_value',
            'profit_loss', 'profit_loss_percentage', 'created_at', 'updated_at',
        ]

    def get_active_item_count(self, obj):
        return obj.items.filter(status='ACTIVE').count()


class PortfolioListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for portfolio list (no items)."""

    class Meta:
        model = Portfolio
        fields = [
            'id', 'name', 'total_invested', 'current_value',
            'profit_loss', 'profit_loss_percentage', 'created_at',
        ]
        read_only_fields = fields
