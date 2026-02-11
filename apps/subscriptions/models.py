from django.db import models
from apps.authentication.models import User


class SubscriptionPlan(models.Model):
    """Subscription plans for access control"""
    
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True, db_index=True)
    description = models.TextField(null=True, blank=True)
    
    # Pricing
    price_monthly = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    price_yearly = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Access permissions
    access_intraday = models.BooleanField(default=True)
    access_swing = models.BooleanField(default=True)
    access_shortterm = models.BooleanField(default=True)
    access_longterm = models.BooleanField(default=True)
    access_futures = models.BooleanField(default=True)
    access_options = models.BooleanField(default=True)
    
    # Features (stored as JSON for flexibility)
    features_json = models.JSONField(default=list)
    
    # Display
    display_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'subscription_plans'
        ordering = ['display_order', 'price_monthly']
    
    def __str__(self):
        return self.name


class UserSubscription(models.Model):
    """User's subscription to a plan"""
    
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('EXPIRED', 'Expired'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.RESTRICT, related_name='subscriptions')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    
    # Subscription period
    start_date = models.DateField()
    end_date = models.DateField()
    
    # Payment details (for future integration)
    payment_id = models.CharField(max_length=255, null=True, blank=True)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Auto-renewal
    auto_renewal = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_subscriptions'
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['end_date']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.plan.name} ({self.status})"
