"""
Payment models for subscription and transaction management
"""
from django.db import models
from django.utils import timezone
from apps.authentication.models import User


class SubscriptionPlan(models.Model):
    """Available subscription plans"""
    
    PLAN_TYPES = [
        ('BASIC', 'Basic'),
        ('PRO', 'PRO'),
        ('PREMIUM', 'Premium'),
    ]
    
    name = models.CharField(max_length=50)
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPES, unique=True)
    
    price_monthly = models.DecimalField(max_digits=10, decimal_places=2)
    price_yearly = models.DecimalField(max_digits=10, decimal_places=2)
    
    features = models.JSONField(default=list)  # List of features
    max_calls_per_month = models.IntegerField(default=10)
    
    is_active = models.BooleanField(default=True)
    display_order = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'payment_subscription_plans'
        ordering = ['display_order']
    
    def __str__(self):
        return f"{self.name} - ₹{self.price_monthly}/month"


class Payment(models.Model):
    """Track all payment transactions"""
    
    PAYMENT_STATUS = [
        ('CREATED', 'Created'),
        ('AUTHORIZED', 'Authorized'),
        ('CAPTURED', 'Captured'),
        ('REFUNDED', 'Refunded'),
        ('FAILED', 'Failed'),
    ]
    
    PAYMENT_METHOD = [
        ('CARD', 'Card'),
        ('UPI', 'UPI'),
        ('NETBANKING', 'Net Banking'),
        ('WALLET', 'Wallet'),
        ('EMI', 'EMI'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    razorpay_order_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    razorpay_payment_id = models.CharField(max_length=100, null=True, blank=True)
    razorpay_signature = models.CharField(max_length=255, null=True, blank=True)
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='INR')
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='CREATED')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD, null=True, blank=True)
    
    description = models.CharField(max_length=255)
    receipt = models.CharField(max_length=100, unique=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'payments'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - ₹{self.amount} - {self.status}"


class Subscription(models.Model):
    """User subscription management"""
    
    PLAN_TYPES = [
        ('BASIC', 'Basic'),
        ('PRO', 'PRO'),
        ('PREMIUM', 'Premium'),
    ]
    
    BILLING_CYCLE = [
        ('MONTHLY', 'Monthly'),
        ('YEARLY', 'Yearly'),
    ]
    
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('EXPIRED', 'Expired'),
        ('CANCELLED', 'Cancelled'),
        ('PAUSED', 'Paused'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payment_subscriptions')
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPES)
    billing_cycle = models.CharField(max_length=20, choices=BILLING_CYCLE)
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField()
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    auto_renew = models.BooleanField(default=True)
    
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True, blank=True)
    razorpay_subscription_id = models.CharField(max_length=100, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'payment_subscriptions'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.plan_type} ({self.status})"
    
    def is_active(self):
        """Check if subscription is currently active"""
        return self.status == 'ACTIVE' and self.end_date > timezone.now()
