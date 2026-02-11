from django.db import models
from apps.authentication.models import User


class Notification(models.Model):
    """User notifications"""
    
    TYPE_CHOICES = [
        ('CALL_PUBLISHED', 'Call Published'),
        ('TARGET_HIT', 'Target Hit'),
        ('STOP_LOSS_HIT', 'Stop Loss Hit'),
        ('CALL_UPDATED', 'Call Updated'),
        ('CALL_EXPIRED', 'Call Expired'),
        ('PORTFOLIO_ALERT', 'Portfolio Alert'),
        ('SYSTEM', 'System Notification'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    
    type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    
    # Related object (generic relation)
    related_type = models.CharField(max_length=50, null=True, blank=True)
    related_id = models.IntegerField(null=True, blank=True)
    
    # Status
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'notifications'
        indexes = [
            models.Index(fields=['user', 'is_read', '-created_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.title}"


class NotificationPreferences(models.Model):
    """User's notification preferences"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_preferences')
    
    # Email notifications
    email_call_published = models.BooleanField(default=True)
    email_target_hit = models.BooleanField(default=True)
    email_stop_loss_hit = models.BooleanField(default=True)
    email_call_updated = models.BooleanField(default=False)
    email_portfolio_alert = models.BooleanField(default=True)
    
    # In-app notifications
    app_call_published = models.BooleanField(default=True)
    app_target_hit = models.BooleanField(default=True)
    app_stop_loss_hit = models.BooleanField(default=True)
    app_call_updated = models.BooleanField(default=True)
    app_portfolio_alert = models.BooleanField(default=True)
    
    # SMS notifications (future)
    sms_target_hit = models.BooleanField(default=False)
    sms_stop_loss_hit = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'notification_preferences'
    
    def __str__(self):
        return f"Preferences for {self.user.email}"
