"""
Serializers for the watchlists app.
"""
from rest_framework import serializers
from apps.watchlists.models import Watchlist, WatchlistItem
from apps.research_calls.serializers import ResearchCallListSerializer


class WatchlistItemSerializer(serializers.ModelSerializer):
    """Serializer for a single watchlist item."""

    research_call = ResearchCallListSerializer(read_only=True)

    class Meta:
        model = WatchlistItem
        fields = ['id', 'research_call', 'notes', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class WatchlistSerializer(serializers.ModelSerializer):
    """Full serializer for a watchlist including its items."""

    items = WatchlistItemSerializer(many=True, read_only=True)
    owner_email = serializers.EmailField(source='user.email', read_only=True)
    item_count = serializers.SerializerMethodField()

    class Meta:
        model = Watchlist
        fields = [
            'id', 'owner_email', 'name', 'description',
            'item_count', 'items',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'owner_email', 'created_at', 'updated_at']

    def get_item_count(self, obj):
        return obj.items.filter(is_active=True).count()


class WatchlistListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for watchlist listings."""

    item_count = serializers.SerializerMethodField()

    class Meta:
        model = Watchlist
        fields = ['id', 'name', 'item_count', 'created_at']
        read_only_fields = fields

    def get_item_count(self, obj):
        return obj.items.filter(is_active=True).count()
