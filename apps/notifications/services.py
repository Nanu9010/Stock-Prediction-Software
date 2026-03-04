"""
Notification services for sending alerts.
"""
from django.conf import settings
from django.core.mail import send_mail

from apps.authentication.models import User
from apps.notifications.models import Notification


def create_notification(user, notification_type, title, message, related_object=None):
    """
    Create a notification for a user and optionally send an email.
    """
    related_type = None
    related_id = None
    if related_object is not None:
        related_type = related_object.__class__.__name__
        related_id = getattr(related_object, 'id', None)

    notification = Notification.objects.create(
        user=user,
        type=notification_type,
        title=title,
        message=message,
        related_type=related_type,
        related_id=related_id,
    )

    if hasattr(user, 'notification_preferences'):
        prefs = user.notification_preferences
        should_email = (
            (notification_type == 'CALL_PUBLISHED' and prefs.email_call_published) or
            (notification_type == 'TARGET_HIT' and prefs.email_target_hit) or
            (notification_type == 'STOP_LOSS_HIT' and prefs.email_stop_loss_hit) or
            (notification_type == 'CALL_EXPIRED' and prefs.email_call_updated)
        )
        if should_email:
            send_email_notification(user, title, message)

    return notification


def send_email_notification(user, title, message):
    """Send email notification to user."""
    try:
        send_mail(
            subject=title,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=True,
        )
    except Exception:
        # Notifications should not fail request/worker flow.
        return None


def notify_call_published(research_call):
    """Notify users when a new call is published."""
    customers = User.objects.filter(role='CUSTOMER', is_active=True)

    title = f"New {research_call.action} Call: {research_call.symbol}"
    message = f"""
    A new research call has been published:

    Symbol: {research_call.symbol}
    Action: {research_call.action}
    Entry Price: Rs {research_call.entry_price}
    Target: Rs {research_call.target_1}
    Stop Loss: Rs {research_call.stop_loss}
    Broker: {research_call.broker.name}

    View details: /calls/{research_call.id}/
    """

    for customer in customers:
        create_notification(
            user=customer,
            notification_type='CALL_PUBLISHED',
            title=title,
            message=message,
            related_object=research_call,
        )


def notify_target_hit(research_call, target_level):
    """Notify users when target is hit."""
    from apps.portfolios.models import PortfolioItem

    portfolio_items = PortfolioItem.objects.filter(
        research_call=research_call,
        status='ACTIVE',
    ).select_related('portfolio__user')

    title = f"Target Hit: {research_call.symbol}"
    message = f"""
    Target {target_level} has been hit for {research_call.symbol}!

    Entry Price: Rs {research_call.entry_price}
    Target Price: Rs {getattr(research_call, f'target_{target_level}')}

    Consider booking profits.
    """

    for item in portfolio_items:
        create_notification(
            user=item.portfolio.user,
            notification_type='TARGET_HIT',
            title=title,
            message=message,
            related_object=research_call,
        )


def notify_stop_loss_hit(research_call):
    """Notify users when stop loss is hit."""
    from apps.portfolios.models import PortfolioItem

    portfolio_items = PortfolioItem.objects.filter(
        research_call=research_call,
        status='ACTIVE',
    ).select_related('portfolio__user')

    title = f"Stop Loss Hit: {research_call.symbol}"
    message = f"""
    Stop loss has been hit for {research_call.symbol}.

    Entry Price: Rs {research_call.entry_price}
    Stop Loss: Rs {research_call.stop_loss}

    Consider exiting the position to limit losses.
    """

    for item in portfolio_items:
        create_notification(
            user=item.portfolio.user,
            notification_type='STOP_LOSS_HIT',
            title=title,
            message=message,
            related_object=research_call,
        )


def notify_call_expired(research_call):
    """Notify users when call expires."""
    from apps.portfolios.models import PortfolioItem

    portfolio_items = PortfolioItem.objects.filter(
        research_call=research_call,
        status='ACTIVE',
    ).select_related('portfolio__user')

    title = f"Call Expired: {research_call.symbol}"
    message = f"""
    The research call for {research_call.symbol} has expired.

    Duration: {research_call.timeframe_days or '-'} days
    Expiry Date: {research_call.expires_at or '-'}

    Please review your position.
    """

    for item in portfolio_items:
        create_notification(
            user=item.portfolio.user,
            notification_type='CALL_EXPIRED',
            title=title,
            message=message,
            related_object=research_call,
        )


def mark_as_read(notification_id, user):
    """Mark notification as read."""
    try:
        notification = Notification.objects.get(id=notification_id, user=user)
        notification.is_read = True
        notification.save(update_fields=['is_read'])
        return notification
    except Notification.DoesNotExist:
        return None


def get_unread_count(user):
    """Get count of unread notifications for user."""
    return Notification.objects.filter(user=user, is_read=False).count()
