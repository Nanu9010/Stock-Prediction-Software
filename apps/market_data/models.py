"""
Market data models for storing index and stock data
"""
from django.db import models
from django.utils import timezone


class MarketIndex(models.Model):
    """Store market index data (NIFTY, SENSEX, etc.)"""
    
    INDEX_CHOICES = [
        ('NIFTY50', 'NIFTY 50'),
        ('SENSEX', 'SENSEX'),
        ('BANKNIFTY', 'BANK NIFTY'),
        ('NIFTYIT', 'NIFTY IT'),
        ('NIFTYPHARMA', 'NIFTY PHARMA'),
    ]
    
    symbol = models.CharField(max_length=20, choices=INDEX_CHOICES, unique=True)
    name = models.CharField(max_length=100)
    current_price = models.DecimalField(max_digits=12, decimal_places=2)
    change = models.DecimalField(max_digits=12, decimal_places=2)
    change_percent = models.DecimalField(max_digits=6, decimal_places=2)
    open_price = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    high = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    low = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    previous_close = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'market_indices'
        ordering = ['symbol']
    
    def __str__(self):
        return f"{self.name} - ₹{self.current_price}"


class StockPrice(models.Model):
    """Store real-time stock prices"""
    
    symbol = models.CharField(max_length=20, db_index=True)
    company_name = models.CharField(max_length=200)
    current_price = models.DecimalField(max_digits=12, decimal_places=2)
    change = models.DecimalField(max_digits=12, decimal_places=2)
    change_percent = models.DecimalField(max_digits=6, decimal_places=2)
    volume = models.BigIntegerField(default=0)
    market_cap = models.BigIntegerField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'stock_prices'
        ordering = ['-volume']
    
    def __str__(self):
        return f"{self.symbol} - ₹{self.current_price}"


class PopularStock(models.Model):
    """Track popular stocks for sidebar display"""
    
    symbol = models.CharField(max_length=20, unique=True)
    company_name = models.CharField(max_length=200)
    display_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'popular_stocks'
        ordering = ['display_order', 'symbol']
    
    def __str__(self):
        return self.symbol
