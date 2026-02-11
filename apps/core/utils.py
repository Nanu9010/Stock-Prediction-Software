"""
Core utility functions
"""
from django.utils import timezone
from datetime import timedelta


def get_date_range(days=30):
    """
    Get date range for the last N days
    
    Args:
        days: Number of days to look back
    
    Returns:
        tuple: (start_date, end_date)
    """
    end_date = timezone.now()
    start_date = end_date - timedelta(days=days)
    return start_date, end_date


def format_currency(amount, currency='₹'):
    """
    Format amount as currency
    
    Args:
        amount: Numeric amount
        currency: Currency symbol
    
    Returns:
        str: Formatted currency string
    """
    if amount is None:
        return f"{currency}0.00"
    
    return f"{currency}{amount:,.2f}"


def calculate_percentage_change(old_value, new_value):
    """
    Calculate percentage change between two values
    
    Args:
        old_value: Original value
        new_value: New value
    
    Returns:
        float: Percentage change
    """
    if old_value == 0:
        return 0
    
    return ((new_value - old_value) / old_value) * 100


def truncate_text(text, max_length=100, suffix='...'):
    """
    Truncate text to maximum length
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
    
    Returns:
        str: Truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix
