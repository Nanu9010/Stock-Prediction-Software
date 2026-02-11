from django.db import models
from apps.authentication.models import User
from apps.research_calls.models import ResearchCall


class Watchlist(models.Model):
    """User's watchlist for tracking interesting calls"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watchlists')
    name = models.CharField(max_length=255, default='My Watchlist')
    description = models.TextField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'watchlists'
        indexes = [
            models.Index(fields=['user']),
        ]
    
    def __str__(self):
        return f"{self.user.get_full_name()}'s {self.name}"


class WatchlistItem(models.Model):
    """Individual items in a watchlist"""
    
    watchlist = models.ForeignKey(
        Watchlist,
        on_delete=models.CASCADE,
        related_name='items'
    )
    research_call = models.ForeignKey(
        'research_calls.ResearchCall',
        on_delete=models.CASCADE
    )
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'watchlist_items'
        unique_together = ['watchlist', 'research_call']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.watchlist.user.email} - {self.research_call.symbol}"
