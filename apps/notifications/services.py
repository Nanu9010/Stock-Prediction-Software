"""
Notification services for sending alerts
"""
from apps.notifications.models import Notification
from apps.authentication.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string


def create_notification(user, notification_type, title, message, related_object=None):
    """
    Create a notification for a user
    
    Args:
        user: User to notify
        notification_type: Type of notification
        title: Notification title
        message: Notification message
        related_object: Optional related object (call, portfolio item, etc.)
    
    Returns:
        Notification instance
    """
    notification = Notification.objects.create(
        user=user,
        notification_type=notification_type,
        title=title,
        message=message
    )
    
    # Send email if user has email notifications enabled
    if hasattr(user, 'notification_preferences'):
        prefs = user.notification_preferences
        
        if notification_type == 'CALL_PUBLISHED' and prefs.call_published:
            send_email_notification(user, title, message)
        elif notification_type == 'TARGET_HIT' and prefs.target_hit:
            send_email_notification(user, title, message)
        elif notification_type == 'STOP_LOSS_HIT' and prefs.stop_loss_hit:
            send_email_notification(user, title, message)
        elif notification_type == 'CALL_EXPIRED' and prefs.call_expired:
            send_email_notification(user, title, message)
    
    return notification


def send_email_notification(user, title, message):
    """Send email notification to user"""
    try:
        send_mail(
            subject=title,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=True,
        )
    except Exception as e:
        print(f"Failed to send email notification: {e}")


def notify_call_published(research_call):
    """Notify users when a new call is published"""
    # Get all active customers
    customers = User.objects.filter(role='CUSTOMER', is_active=True)
    
    title = f"New {research_call.action} Call: {research_call.symbol}"
    message = f"""
    A new research call has been published:
    
    Symbol: {research_call.symbol}
    Action: {research_call.action}
    Entry Price: ₹{research_call.entry_price}
    Target: ₹{research_call.target_1}
    Stop Loss: ₹{research_call.stop_loss}
    Broker: {research_call.broker.name}
    
    View details: /calls/{research_call.id}/
    """
    
    for customer in customers:
        create_notification(
            user=customer,
            notification_type='CALL_PUBLISHED',
            title=title,
            message=message,
            related_object=research_call
        )


def notify_target_hit(research_call, target_level):
    """Notify users when target is hit"""
    # Get users who have this call in portfolio
    from apps.portfolios.models import PortfolioItem
    
    portfolio_items = PortfolioItem.objects.filter(
        research_call=research_call,
        status='ACTIVE'
    ).select_related('portfolio__user')
    
    title = f"Target Hit: {research_call.symbol}"
    message = f"""
    Target {target_level} has been hit for {research_call.symbol}!
    
    Entry Price: ₹{research_call.entry_price}
    Target Price: ₹{getattr(research_call, f'target_{target_level}')}
    
    Consider booking profits.
    """
    
    for item in portfolio_items:
        create_notification(
            user=item.portfolio.user,
            notification_type='TARGET_HIT',
            title=title,
            message=message,
            related_object=research_call
        )


def notify_stop_loss_hit(research_call):
    """Notify users when stop loss is hit"""
    from apps.portfolios.models import PortfolioItem
    
    portfolio_items = PortfolioItem.objects.filter(
        research_call=research_call,
        status='ACTIVE'
    ).select_related('portfolio__user')
    
    title = f"Stop Loss Hit: {research_call.symbol}"
    message = f"""
    Stop loss has been hit for {research_call.symbol}.
    
    Entry Price: ₹{research_call.entry_price}
    Stop Loss: ₹{research_call.stop_loss}
    
    Consider exiting the position to limit losses.
    """
    
    for item in portfolio_items:
        create_notification(
            user=item.portfolio.user,
            notification_type='STOP_LOSS_HIT',
            title=title,
            message=message,
            related_object=research_call
        )


def notify_call_expired(research_call):
    """Notify users when call expires"""
    from apps.portfolios.models import PortfolioItem
    
    portfolio_items = PortfolioItem.objects.filter(
        research_call=research_call,
        status='ACTIVE'
    ).select_related('portfolio__user')
    
    title = f"Call Expired: {research_call.symbol}"
    message = f"""
    The research call for {research_call.symbol} has expired.
    
    Duration: {research_call.duration_days} days
    Expiry Date: {research_call.expiry_date}
    
    Please review your position.
    """
    
    for item in portfolio_items:
        create_notification(
            user=item.portfolio.user,
            notification_type='CALL_EXPIRED',
            title=title,
            message=message,
            related_object=research_call
        )


def mark_as_read(notification_id, user):
    """Mark notification as read"""
    try:
        notification = Notification.objects.get(id=notification_id, user=user)
        notification.is_read = True
        notification.save()
        return notification
    except Notification.DoesNotExist:
        return None


def get_unread_count(user):
    """Get count of unread notifications for user"""
    return Notification.objects.filter(user=user, is_read=False).count()
