"""
Serializers for the market_data app.
"""
from rest_framework import serializers
from apps.market_data.models import MarketIndex, StockPrice, PopularStock


class MarketIndexSerializer(serializers.ModelSerializer):
    """Serializer for market indices (NIFTY, SENSEX, etc.)."""

    class Meta:
        model = MarketIndex
        fields = [
            'id', 'symbol', 'name',
            'current_price', 'change', 'change_percent',
            'open_price', 'high', 'low', 'previous_close',
            'updated_at',
        ]
        read_only_fields = fields


class StockPriceSerializer(serializers.ModelSerializer):
    """Serializer for real-time stock prices."""

    class Meta:
        model = StockPrice
        fields = [
            'id', 'symbol', 'company_name',
            'current_price', 'change', 'change_percent',
            'volume', 'market_cap', 'updated_at',
        ]
        read_only_fields = fields


class PopularStockSerializer(serializers.ModelSerializer):
    """Serializer for popular stocks shown in sidebar/ticker."""

    class Meta:
        model = PopularStock
        fields = ['id', 'symbol', 'company_name', 'display_order', 'is_active']
        read_only_fields = ['id']
