"""
Research call validators
"""
from django.core.exceptions import ValidationError
from decimal import Decimal


def validate_price_levels(action, entry_price, target_1, target_2, target_3, stop_loss):
    """
    Validate that price levels are logical based on action (BUY/SELL)
    
    Args:
        action: 'BUY' or 'SELL'
        entry_price: Entry price
        target_1: First target
        target_2: Second target (optional)
        target_3: Third target (optional)
        stop_loss: Stop loss price
    
    Raises:
        ValidationError: If price levels are invalid
    """
    entry = Decimal(str(entry_price))
    t1 = Decimal(str(target_1))
    sl = Decimal(str(stop_loss))
    
    if action == 'BUY':
        # For BUY: targets should be above entry, stop loss below
        if t1 <= entry:
            raise ValidationError('Target 1 must be greater than entry price for BUY calls')
        
        if target_2 and Decimal(str(target_2)) <= t1:
            raise ValidationError('Target 2 must be greater than Target 1')
        
        if target_3 and Decimal(str(target_3)) <= Decimal(str(target_2 or t1)):
            raise ValidationError('Target 3 must be greater than Target 2')
        
        if sl >= entry:
            raise ValidationError('Stop loss must be less than entry price for BUY calls')
    
    elif action == 'SELL':
        # For SELL: targets should be below entry, stop loss above
        if t1 >= entry:
            raise ValidationError('Target 1 must be less than entry price for SELL calls')
        
        if target_2 and Decimal(str(target_2)) >= t1:
            raise ValidationError('Target 2 must be less than Target 1')
        
        if target_3 and Decimal(str(target_3)) >= Decimal(str(target_2 or t1)):
            raise ValidationError('Target 3 must be less than Target 2')
        
        if sl <= entry:
            raise ValidationError('Stop loss must be greater than entry price for SELL calls')


def validate_call_duration(duration_days):
    """
    Validate call duration is within acceptable range
    
    Args:
        duration_days: Duration in days
    
    Raises:
        ValidationError: If duration is invalid
    """
    if duration_days < 1:
        raise ValidationError('Call duration must be at least 1 day')
    
    if duration_days > 365:
        raise ValidationError('Call duration cannot exceed 365 days')
