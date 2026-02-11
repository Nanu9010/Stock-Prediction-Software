"""
Lifecycle services for monitoring research calls
"""
from apps.research_calls.models import ResearchCall, ResearchCallEvent
from apps.notifications.services import notify_target_hit, notify_stop_loss_hit, notify_call_expired
from django.utils import timezone
from decimal import Decimal


def check_price_levels(research_call, current_price):
    """
    Check if current price has hit target or stop loss
    
    Args:
        research_call: ResearchCall instance
        current_price: Current market price
    
    Returns:
        dict with hit_type and level
    """
    current_price = Decimal(str(current_price))
    
    if research_call.action == 'BUY':
        # Check targets (price going up)
        if current_price >= research_call.target_1:
            if research_call.target_3 and current_price >= research_call.target_3:
                return {'hit_type': 'TARGET', 'level': 3}
            elif research_call.target_2 and current_price >= research_call.target_2:
                return {'hit_type': 'TARGET', 'level': 2}
            else:
                return {'hit_type': 'TARGET', 'level': 1}
        
        # Check stop loss (price going down)
        if current_price <= research_call.stop_loss:
            return {'hit_type': 'STOP_LOSS', 'level': None}
    
    else:  # SELL
        # Check targets (price going down)
        if current_price <= research_call.target_1:
            if research_call.target_3 and current_price <= research_call.target_3:
                return {'hit_type': 'TARGET', 'level': 3}
            elif research_call.target_2 and current_price <= research_call.target_2:
                return {'hit_type': 'TARGET', 'level': 2}
            else:
                return {'hit_type': 'TARGET', 'level': 1}
        
        # Check stop loss (price going up)
        if current_price >= research_call.stop_loss:
            return {'hit_type': 'STOP_LOSS', 'level': None}
    
    return None


def process_target_hit(research_call, level):
    """Process target hit event"""
    # Create event
    ResearchCallEvent.objects.create(
        research_call=research_call,
        event_type='TARGET_HIT',
        notes=f'Target {level} hit'
    )
    
    # Send notifications
    notify_target_hit(research_call, level)
    
    # If final target hit, close the call
    if level == 3 or (level == 2 and not research_call.target_3) or (level == 1 and not research_call.target_2):
        close_call(research_call, 'TARGET_ACHIEVED')


def process_stop_loss_hit(research_call):
    """Process stop loss hit event"""
    # Create event
    ResearchCallEvent.objects.create(
        research_call=research_call,
        event_type='STOP_LOSS_HIT',
        notes='Stop loss triggered'
    )
    
    # Send notifications
    notify_stop_loss_hit(research_call)
    
    # Close the call
    close_call(research_call, 'STOP_LOSS_HIT')


def check_expiry(research_call):
    """Check if call has expired"""
    if research_call.expiry_date and research_call.expiry_date <= timezone.now().date():
        if research_call.status == 'ACTIVE':
            # Create event
            ResearchCallEvent.objects.create(
                research_call=research_call,
                event_type='EXPIRED',
                notes='Call expired'
            )
            
            # Send notifications
            notify_call_expired(research_call)
            
            # Close the call
            close_call(research_call, 'EXPIRED')
            
            return True
    
    return False


def close_call(research_call, reason):
    """
    Close a research call
    
    Args:
        research_call: ResearchCall instance
        reason: Reason for closing (TARGET_ACHIEVED, STOP_LOSS_HIT, EXPIRED, MANUAL)
    """
    research_call.status = 'CLOSED'
    research_call.closed_at = timezone.now()
    research_call.save()
    
    # Create closing event
    ResearchCallEvent.objects.create(
        research_call=research_call,
        event_type='CLOSED',
        notes=f'Call closed: {reason}'
    )


def monitor_active_calls():
    """
    Monitor all active calls for price movements
    This function should be called periodically by Celery
    
    Note: This is a placeholder. In production, you would:
    1. Fetch current prices from a market data API
    2. Check each active call against current price
    3. Process hits accordingly
    """
    active_calls = ResearchCall.objects.filter(status='ACTIVE')
    
    results = {
        'checked': 0,
        'targets_hit': 0,
        'stop_losses_hit': 0,
        'expired': 0
    }
    
    for call in active_calls:
        results['checked'] += 1
        
        # Check expiry first
        if check_expiry(call):
            results['expired'] += 1
            continue
        
        # In production, fetch current price from API
        # current_price = fetch_current_price(call.symbol)
        # For now, skip price checking
        # hit = check_price_levels(call, current_price)
        # if hit:
        #     if hit['hit_type'] == 'TARGET':
        #         process_target_hit(call, hit['level'])
        #         results['targets_hit'] += 1
        #     elif hit['hit_type'] == 'STOP_LOSS':
        #         process_stop_loss_hit(call)
        #         results['stop_losses_hit'] += 1
    
    return results
