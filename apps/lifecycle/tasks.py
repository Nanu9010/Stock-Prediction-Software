"""
Celery tasks for background processing
"""
from celery import shared_task
from apps.lifecycle.services import monitor_active_calls
from apps.brokers.services import update_broker_metrics
from apps.portfolios.services import get_portfolio_summary
from apps.notifications.services import create_notification
from django.contrib.auth import get_user_model

User = get_user_model()


@shared_task
def monitor_calls_task():
    """
    Periodic task to monitor active research calls
    Should run every 5-15 minutes during market hours
    """
    results = monitor_active_calls()
    return {
        'status': 'completed',
        'calls_checked': results['checked'],
        'targets_hit': results['targets_hit'],
        'stop_losses_hit': results['stop_losses_hit'],
        'expired': results['expired']
    }


@shared_task
def update_broker_metrics_task():
    """
    Daily task to update broker performance metrics
    Should run once daily after market close
    """
    from apps.brokers.models import Broker
    
    updated_count = 0
    for broker in Broker.objects.all():
        try:
            update_broker_metrics(broker)
            updated_count += 1
        except Exception as e:
            print(f"Error updating metrics for {broker.name}: {e}")
    
    return {
        'status': 'completed',
        'brokers_updated': updated_count
    }


@shared_task
def send_daily_summary_task():
    """
    Send daily portfolio summary to users
    Should run once daily
    """
    customers = User.objects.filter(role='CUSTOMER', is_active=True)
    
    sent_count = 0
    for customer in customers:
        try:
            summary = get_portfolio_summary(customer)
            
            if summary['active_positions'] > 0 or summary['closed_positions'] > 0:
                message = f"""
                Daily Portfolio Summary:
                
                Active Positions: {summary['active_positions']}
                Total Invested: ₹{summary['total_invested']}
                Unrealized P&L: ₹{summary['unrealized_pnl']}
                Realized P&L: ₹{summary['realized_pnl']}
                Win Rate: {summary['win_rate']}%
                """
                
                create_notification(
                    user=customer,
                    notification_type='SYSTEM',
                    title='Daily Portfolio Summary',
                    message=message
                )
                sent_count += 1
        except Exception as e:
            print(f"Error sending summary to {customer.email}: {e}")
    
    return {
        'status': 'completed',
        'summaries_sent': sent_count
    }


@shared_task
def cleanup_old_notifications_task():
    """
    Clean up old read notifications
    Should run weekly
    """
    from apps.notifications.models import Notification
    from datetime import timedelta
    from django.utils import timezone
    
    # Delete read notifications older than 30 days
    cutoff_date = timezone.now() - timedelta(days=30)
    deleted_count, _ = Notification.objects.filter(
        is_read=True,
        created_at__lt=cutoff_date
    ).delete()
    
    return {
        'status': 'completed',
        'notifications_deleted': deleted_count
    }
