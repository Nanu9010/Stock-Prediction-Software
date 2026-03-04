"""
Market data models for storing index and stock data
"""
from django.db import models
from django.utils import timezone


class MarketIndex(models.Model):
    """Store market index data (NIFTY, SENSEX, etc.)"""
    
    INDEX_CHOICES = [
        ('NIFTY50',     'NIFTY 50'),
        ('SENSEX',      'SENSEX'),
        ('BANKNIFTY',   'BANK NIFTY'),
        ('FINNIFTY',    'FIN NIFTY'),
        ('MIDCPNIFTY',  'MIDCAP NIFTY'),
        ('NIFTYIT',     'NIFTY IT'),
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


class IPO(models.Model):
    """Store Upcoming and Recently Listed IPOs"""
    
    company_name = models.CharField(max_length=200)
    symbol = models.CharField(max_length=50, blank=True, null=True, help_text="NSE Symbol for fetching live price when listed")
    sector = models.CharField(max_length=100)
    
    # Issue Details
    price_band = models.CharField(max_length=100, help_text="e.g. ₹674 - ₹708")
    issue_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    issue_size = models.CharField(max_length=100, help_text="e.g. ₹8,750 Cr")
    lot_size = models.IntegerField()
    
    # Dates
    open_date = models.DateField()
    close_date = models.DateField()
    listing_date = models.DateField(null=True, blank=True)
    
    # Performance
    gmp = models.CharField(max_length=50, blank=True, null=True, help_text="Grey Market Premium, e.g. +₹45")
    listing_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_listed = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ipos'
        ordering = ['-open_date']

    def __str__(self):
        return self.company_name


class Commodity(models.Model):
    """Store Commodity configuration for fetching live prices via yfinance"""
    
    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=50, help_text="yfinance symbol, e.g. GC=F")
    unit = models.CharField(max_length=20, help_text="e.g. $/oz, ₹")
    icon = models.CharField(max_length=10, blank=True, null=True, help_text="Emoji icon, e.g. 🥇")
    
    is_global = models.BooleanField(default=True, help_text="True = USD Global prices, False = INR MCX-equivalent")
    mcx_multiplier = models.DecimalField(max_digits=10, decimal_places=4, default=1.0, help_text="Multiplier to convert global price to Indian equivalent (e.g. 0.322 for Gold 10g)")
    
    is_active = models.BooleanField(default=True)
    display_order = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'commodities'
        ordering = ['display_order', 'name']

    def __str__(self):
        return f"{self.name} ({self.symbol})"


class ETF(models.Model):
    """Store ETF configuration for fetching live prices via yfinance"""
    
    name = models.CharField(max_length=150)
    symbol = models.CharField(max_length=50, help_text="yfinance symbol, e.g. NIFTYBEES.NS")
    short_name = models.CharField(max_length=50, help_text="Short name for badges, e.g. NIFTYBEES")
    category = models.CharField(max_length=50, help_text="e.g. Index, Gold, Sectoral")
    
    is_active = models.BooleanField(default=True)
    display_order = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'etfs'
        ordering = ['display_order', 'name']

    def __str__(self):
        return f"{self.short_name} ({self.symbol})"


class SIP(models.Model):
    """Store curated curated SIP funds for the platform"""
    name = models.CharField(max_length=150)
    category = models.CharField(max_length=100, help_text="e.g. Index Fund, Large Cap")
    min_sip = models.IntegerField(help_text="Minimum SIP Amount in INR")
    
    returns_1y = models.DecimalField(max_digits=5, decimal_places=2, help_text="1Y Return %")
    returns_3y = models.DecimalField(max_digits=5, decimal_places=2, help_text="3Y Return %")
    returns_5y = models.DecimalField(max_digits=5, decimal_places=2, help_text="5Y Return %")
    
    popularity = models.CharField(max_length=100, help_text="e.g. Most Popular, Trending")
    
    is_active = models.BooleanField(default=True)
    display_order = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'sips'
        ordering = ['display_order', 'name']

    def __str__(self):
        return f"{self.name} - {self.category}"


class GainersLosers(models.Model):
    """Cache table for top gainers, losers, and most active stocks"""

    CATEGORY_CHOICES = [
        ('GAINER', 'Top Gainer'),
        ('LOSER',  'Top Loser'),
        ('ACTIVE', 'Most Active'),
    ]

    symbol       = models.CharField(max_length=30)
    company_name = models.CharField(max_length=200, blank=True)
    ltp          = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    change       = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    change_pct   = models.DecimalField(max_digits=7,  decimal_places=2, default=0)
    volume       = models.BigIntegerField(default=0)
    category     = models.CharField(max_length=10, choices=CATEGORY_CHOICES)
    rank         = models.SmallIntegerField(default=0, help_text='Position in the sorted list')
    fetched_at   = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'gainers_losers_cache'
        ordering = ['category', 'rank']
        unique_together = [('symbol', 'category')]
        indexes = [models.Index(fields=['category', 'rank'])]

    def __str__(self):
        return f"{self.symbol} [{self.category}] {self.change_pct}%"
