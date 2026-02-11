from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify


class Broker(models.Model):
    """Stock broker/research house"""
    
    # Basic Information
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True, db_index=True)
    description = models.TextField(null=True, blank=True)
    logo = models.ImageField(upload_to='broker_logos/', null=True, blank=True)
    
    # Contact & Legal
    website_url = models.URLField(max_length=500, null=True, blank=True)
    sebi_registration_no = models.CharField(max_length=50, unique=True, null=True, blank=True)
    
    # Performance Metrics (denormalized for quick access)
    overall_accuracy = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0.00,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    total_calls_published = models.IntegerField(default=0)
    total_calls_closed = models.IntegerField(default=0)
    avg_return_percentage = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'app_brokers'
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active']),
            models.Index(fields=['-overall_accuracy']),
        ]
        ordering = ['-overall_accuracy', 'name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)



class BrokerPerformanceMetrics(models.Model):
    """Daily performance metrics for brokers"""
    
    broker = models.ForeignKey(
        Broker, 
        on_delete=models.CASCADE, 
        related_name='performance_metrics'
    )
    metric_date = models.DateField(db_index=True)
    
    # Overall Metrics
    total_closed_calls = models.IntegerField(default=0)
    successful_calls = models.IntegerField(default=0)
    accuracy_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    avg_return_percentage = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Category-wise Metrics (stored as JSON for flexibility)
    intraday_accuracy = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    swing_accuracy = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    shortterm_accuracy = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    longterm_accuracy = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    intraday_avg_return = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    swing_avg_return = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    shortterm_avg_return = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    longterm_avg_return = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'broker_performance_metrics'
        unique_together = [['broker', 'metric_date']]
        indexes = [
            models.Index(fields=['broker', '-metric_date']),
        ]
        ordering = ['-metric_date']
    
    def __str__(self):
        return f"{self.broker.name} - {self.metric_date}"
