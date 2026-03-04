"""
Celery scheduled tasks for market data background updates
"""
from celery import shared_task
import logging

from apps.market_data.services import (
    update_index_prices,
    fetch_and_cache_gainers_losers,
    get_most_active,
    update_popular_stocks
)

logger = logging.getLogger(__name__)

@shared_task
def task_update_indices():
    """Updates the 5 main indices in background"""
    logger.info("Executing periodic task: task_update_indices")
    try:
        updated = update_index_prices()
        logger.info(f"Successfully updated {updated} indices")
        return updated
    except Exception as e:
        logger.error(f"Error in task_update_indices: {e}")
        return 0

@shared_task
def task_update_gainers_active():
    """Updates top gainers, losers, and most active stocks"""
    logger.info("Executing periodic task: task_update_gainers_active")
    try:
        # Fetch gainers/losers (which caches and writes to GainersLosers model)
        fetch_and_cache_gainers_losers(limit=20)
        # Fetch most active (which caches result)
        get_most_active(limit=20)
        logger.info("Successfully updated gainers, losers, and active stocks")
        return True
    except Exception as e:
        logger.error(f"Error in task_update_gainers_active: {e}")
        return False

@shared_task
def task_update_popular_stocks():
    """Updates the user's popular stocks list"""
    logger.info("Executing periodic task: task_update_popular_stocks")
    try:
        updated = update_popular_stocks()
        logger.info(f"Successfully updated {updated} popular stocks")
        return updated
    except Exception as e:
        logger.error(f"Error in task_update_popular_stocks: {e}")
        return 0
