from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from apps.brokers.models import Broker
from apps.authentication.models import User


class ResearchCall(models.Model):
    """Stock research call with targets and stop-loss"""
    
    CALL_TYPE_CHOICES = [
        ('INTRADAY', 'Intraday'),
        ('SWING', 'Swing'),
        ('SHORT_TERM', 'Short Term'),
        ('MEDIUM_TERM', 'Medium Term'),
        ('LONG_TERM', 'Long Term'),
        ('POSITIONAL', 'Positional'),
    ]
    
    ACTION_CHOICES = [
        ('BUY', 'Buy'),
        ('SELL', 'Sell'),
    ]
    
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('PENDING_APPROVAL', 'Pending Approval'),
        ('APPROVED', 'Approved'),
        ('PUBLISHED', 'Published'),
        ('ACTIVE', 'Active'),
        ('TARGET_1_HIT', 'Target 1 Hit'),
        ('TARGET_2_HIT', 'Target 2 Hit'),
        ('TARGET_3_HIT', 'Target 3 Hit'),
        ('STOP_LOSS_HIT', 'Stop Loss Hit'),
        ('MANUALLY_EXITED', 'Manually Exited'),
        ('EXPIRED', 'Expired'),
        ('CLOSED', 'Closed'),
    ]
    
    INSTRUMENT_TYPE_CHOICES = [
        ('EQUITY', 'Equity'),
        ('FUTURES', 'Futures'),
        ('OPTIONS', 'Options'),
        ('COMMODITY', 'Commodity'),
    ]
    
    # Ownership
    broker = models.ForeignKey(Broker, on_delete=models.CASCADE, related_name='research_calls', db_constraint=False)
    created_by = models.ForeignKey(User, on_delete=models.RESTRICT, related_name='created_calls', default=1, db_constraint=False)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_calls', db_constraint=False)
    
    # Stock details
    symbol = models.CharField(max_length=50, db_index=True)
    exchange = models.CharField(max_length=10, default='NSE')
    company_name = models.CharField(max_length=255, null=True, blank=True)
    sector = models.CharField(max_length=100, null=True, blank=True, db_index=True)
    instrument_type = models.CharField(max_length=20, choices=INSTRUMENT_TYPE_CHOICES, default='EQUITY')
    
    # Call details
    call_type = models.CharField(max_length=20, choices=CALL_TYPE_CHOICES, db_index=True)
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    
    # Price levels
    entry_price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0.01)])
    target_1 = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0.01)])
    target_2 = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    target_3 = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    stop_loss = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0.01)])
    
    # Metadata
    timeframe_days = models.IntegerField(null=True, blank=True)
    expected_return_percentage = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    risk_reward_ratio = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    rationale = models.TextField(null=True, blank=True)
    
    # Lifecycle
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='DRAFT', db_index=True)
    published_at = models.DateTimeField(null=True, blank=True, db_index=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    
    # Performance
    actual_return_percentage = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_successful = models.BooleanField(null=True, blank=True)
    exit_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    exit_reason = models.CharField(max_length=100, null=True, blank=True)
    
    # Versioning
    version = models.IntegerField(default=1)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'research_calls'
        indexes = [
            models.Index(fields=['status', 'published_at']),
            models.Index(fields=['broker', 'status']),
            models.Index(fields=['symbol']),
            models.Index(fields=['call_type', 'status']),
        ]
        ordering = ['-published_at', '-created_at']
    
    def __str__(self):
        return f"{self.action} {self.symbol} @ {self.entry_price} ({self.call_type})"
    
    
    def clean(self):
        """Validate price levels based on action type"""
        # Only validate if all required price fields are provided
        if not self.entry_price or not self.target_1 or not self.stop_loss:
            return
        
        if self.action == 'BUY':
            if self.target_1 <= self.entry_price:
                raise ValidationError('Target 1 must be greater than entry price for BUY calls')
            if self.stop_loss >= self.entry_price:
                raise ValidationError('Stop loss must be less than entry price for BUY calls')
        
        elif self.action == 'SELL':
            if self.target_1 >= self.entry_price:
                raise ValidationError('Target 1 must be less than entry price for SELL calls')
            if self.stop_loss <= self.entry_price:
                raise ValidationError('Stop loss must be greater than entry price for SELL calls')
        
        # Validate progressive targets
        if self.target_2 and self.target_1:
            if self.action == 'BUY' and self.target_2 <= self.target_1:
                raise ValidationError('Target 2 must be greater than Target 1 for BUY calls')
            elif self.action == 'SELL' and self.target_2 >= self.target_1:
                raise ValidationError('Target 2 must be less than Target 1 for SELL calls')
        
        if self.target_3 and self.target_2:
            if self.action == 'BUY' and self.target_3 <= self.target_2:
                raise ValidationError('Target 3 must be greater than Target 2 for BUY calls')
            elif self.action == 'SELL' and self.target_3 >= self.target_2:
                raise ValidationError('Target 3 must be less than Target 2 for SELL calls')
    
    def save(self, *args, **kwargs):
        # Calculate expected return and risk-reward ratio
        if self.action == 'BUY':
            potential_gain = float(self.target_1) - float(self.entry_price)
            potential_loss = float(self.entry_price) - float(self.stop_loss)
        else:  # SELL
            potential_gain = float(self.entry_price) - float(self.target_1)
            potential_loss = float(self.stop_loss) - float(self.entry_price)
        
        if potential_loss > 0:
            self.risk_reward_ratio = round(potential_gain / potential_loss, 2)
        
        self.expected_return_percentage = round((potential_gain / float(self.entry_price)) * 100, 2)
        
        super().save(*args, **kwargs)


class ResearchCallEvent(models.Model):
    """Track lifecycle events for research calls"""
    
    EVENT_TYPE_CHOICES = [
        ('CREATED', 'Created'),
        ('SUBMITTED_FOR_APPROVAL', 'Submitted for Approval'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('PUBLISHED', 'Published'),
        ('TARGET_1_HIT', 'Target 1 Hit'),
        ('TARGET_2_HIT', 'Target 2 Hit'),
        ('TARGET_3_HIT', 'Target 3 Hit'),
        ('STOP_LOSS_HIT', 'Stop Loss Hit'),
        ('MANUALLY_EXITED', 'Manually Exited'),
        ('EXPIRED', 'Expired'),
        ('CLOSED', 'Closed'),
        ('UPDATED', 'Updated'),
    ]
    
    research_call = models.ForeignKey(ResearchCall, on_delete=models.CASCADE, related_name='events')
    event_type = models.CharField(max_length=50, choices=EVENT_TYPE_CHOICES)
    
    # Event details
    price_at_event = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    triggered_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, db_constraint=False)
    
    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'research_call_events'
        indexes = [
            models.Index(fields=['research_call', '-created_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.research_call.symbol} - {self.event_type} at {self.created_at}"


class ResearchCallVersion(models.Model):
    """Track version history of research call edits"""
    
    research_call = models.ForeignKey(ResearchCall, on_delete=models.CASCADE, related_name='versions')
    version_number = models.IntegerField()
    
    # Changed fields (stored as JSON)
    changes_json = models.JSONField()
    change_reason = models.TextField(null=True, blank=True)
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, db_constraint=False)
    
    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'research_call_versions'
        unique_together = [['research_call', 'version_number']]
        indexes = [
            models.Index(fields=['research_call', '-version_number']),
        ]
        ordering = ['-version_number']
    
    def __str__(self):
        return f"{self.research_call.symbol} - Version {self.version_number}"
