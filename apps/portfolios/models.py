from django.db import models
from django.core.validators import MinValueValidator
from apps.authentication.models import User
from apps.research_calls.models import ResearchCall


class Portfolio(models.Model):
    """User's investment portfolio"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='portfolios')
    name = models.CharField(max_length=255, default='My Portfolio')
    description = models.TextField(null=True, blank=True)
    
    # Aggregated metrics (denormalized for performance)
    total_invested = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    current_value = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    profit_loss = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    profit_loss_percentage = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'portfolios'
        indexes = [
            models.Index(fields=['user']),
        ]
    
    def __str__(self):
        return f"{self.user.get_full_name()}'s {self.name}"


class PortfolioItem(models.Model):
    """Individual holding in a portfolio"""
    
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('EXITED', 'Exited'),
    ]
    
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='items')
    research_call = models.ForeignKey(ResearchCall, on_delete=models.RESTRICT, related_name='portfolio_items')
    
    # Entry details
    entry_price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0.01)])
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    entry_date = models.DateField()
    invested_amount = models.DecimalField(max_digits=15, decimal_places=2)
    
    # Current status
    current_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    current_value = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    profit_loss = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    profit_loss_percentage = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Exit details
    exit_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    exit_date = models.DateField(null=True, blank=True)
    exit_reason = models.CharField(max_length=100, null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'portfolio_items'
        indexes = [
            models.Index(fields=['portfolio', 'status']),
            models.Index(fields=['research_call']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.research_call.symbol} - {self.quantity} @ {self.entry_price}"
    
    def save(self, *args, **kwargs):
        # Calculate invested amount
        self.invested_amount = self.entry_price * self.quantity
        
        # Calculate current value and P&L if current price is available
        if self.current_price:
            self.current_value = self.current_price * self.quantity
            self.profit_loss = self.current_value - self.invested_amount
            if self.invested_amount > 0:
                self.profit_loss_percentage = (self.profit_loss / self.invested_amount) * 100
        
        super().save(*args, **kwargs)
