"""
Portfolio services - Business logic for portfolio operations
"""
from django.db import transaction
from django.utils import timezone
from decimal import Decimal
from apps.portfolios.models import Portfolio, PortfolioItem
from apps.audit.models import AuditLog


@transaction.atomic
def add_to_portfolio(user, research_call, entry_price, quantity, entry_date=None):
    """
    Add a research call to user's portfolio
    
    Args:
        user: User instance
        research_call: ResearchCall instance
        entry_price: Entry price
        quantity: Number of shares/units
        entry_date: Entry date (defaults to today)
    
    Returns:
        PortfolioItem: Created portfolio item
    """
    # Get or create portfolio
    portfolio, created = Portfolio.objects.get_or_create(
        user=user,
        defaults={'name': 'My Portfolio'}
    )
    
    # Check if already in portfolio
    existing = PortfolioItem.objects.filter(
        portfolio=portfolio,
        research_call=research_call,
        status='ACTIVE'
    ).first()
    
    if existing:
        raise ValueError('This call is already in your portfolio')
    
    # Create portfolio item
    item = PortfolioItem.objects.create(
        portfolio=portfolio,
        research_call=research_call,
        entry_price=entry_price,
        quantity=quantity,
        entry_date=entry_date or timezone.now().date(),
        invested_amount=Decimal(str(entry_price)) * quantity
    )
    
    # Audit log
    AuditLog.objects.create(
        user=user,
        action='ADD_TO_PORTFOLIO',
        entity_type='PortfolioItem',
        entity_id=item.id,
        new_values={
            'symbol': research_call.symbol,
            'entry_price': str(entry_price),
            'quantity': quantity
        }
    )
    
    return item


@transaction.atomic
def exit_position(portfolio_item, exit_price, exit_date=None, exit_by=None):
    """
    Exit a portfolio position
    
    Args:
        portfolio_item: PortfolioItem instance
        exit_price: Exit price
        exit_date: Exit date (defaults to today)
        exit_by: User exiting the position
    
    Returns:
        PortfolioItem: Updated portfolio item
    """
    if portfolio_item.status != 'ACTIVE':
        raise ValueError('Can only exit active positions')
    
    portfolio_item.exit_price = exit_price
    portfolio_item.exit_date = exit_date or timezone.now().date()
    portfolio_item.status = 'CLOSED'
    
    # Calculate P&L
    portfolio_item.calculate_pnl()
    portfolio_item.save()
    
    # Audit log
    if exit_by:
        AuditLog.objects.create(
            user=exit_by,
            action='EXIT_POSITION',
            entity_type='PortfolioItem',
            entity_id=portfolio_item.id,
            new_values={
                'exit_price': str(exit_price),
                'pnl': str(portfolio_item.profit_loss)
            }
        )
    
    return portfolio_item


def calculate_portfolio_summary(portfolio):
    """
    Calculate portfolio summary statistics
    
    Args:
        portfolio: Portfolio instance
    
    Returns:
        dict: Summary statistics
    """
    active_items = portfolio.items.filter(status='ACTIVE')
    closed_items = portfolio.items.filter(status='CLOSED')
    
    total_invested = sum(item.invested_amount for item in active_items)
    total_current_value = sum(item.current_value or 0 for item in active_items)
    total_pnl = sum(item.profit_loss or 0 for item in closed_items)
    
    winning_trades = closed_items.filter(profit_loss__gt=0).count()
    losing_trades = closed_items.filter(profit_loss__lt=0).count()
    total_trades = closed_items.count()
    
    win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
    
    return {
        'total_invested': total_invested,
        'total_current_value': total_current_value,
        'unrealized_pnl': total_current_value - total_invested,
        'realized_pnl': total_pnl,
        'total_pnl': (total_current_value - total_invested) + total_pnl,
        'active_positions': active_items.count(),
        'closed_positions': total_trades,
        'winning_trades': winning_trades,
        'losing_trades': losing_trades,
        'win_rate': round(win_rate, 2),
    }
