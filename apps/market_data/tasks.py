"""
Celery tasks for market data updates (FREE - no paid APIs)
"""
from celery import shared_task
from apps.market_data.services import update_index_prices, update_popular_stocks


@shared_task
def update_market_data_task():
    """
    Update market indices and popular stocks
    Run every 5-15 minutes during market hours
    """
    indices_updated = update_index_prices()
    stocks_updated = update_popular_stocks()
    
    return {
        'status': 'completed',
        'indices_updated': indices_updated,
        'stocks_updated': stocks_updated
    }
