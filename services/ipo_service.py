"""
IPO Service — Upcoming and recently listed IPOs
No free real-time API for NSE IPOs, so we use curated data
Admin can update via admin panel in the future
"""
import yfinance as yf
import logging
from datetime import datetime, timedelta
from django.core.cache import cache

logger = logging.getLogger(__name__)

# Suppress noisy yfinance download-level error logs
logging.getLogger('yfinance').setLevel(logging.CRITICAL)

CACHE_TTL = 3600  # 1 hour (IPO data changes infrequently)

from apps.market_data.models import IPO


def get_upcoming_ipos():
    """Get upcoming IPOs from database"""
    cache_key = 'ipo_upcoming_db'
    cached = cache.get(cache_key)
    if cached:
        return cached

    today = datetime.now().date()
    # Query database for unlisted IPOs
    ipos_qs = IPO.objects.filter(is_listed=False).order_by('open_date')
    
    ipos = []
    for ipo in ipos_qs:
        ipo_dict = {
            'id': ipo.id,
            'company': ipo.company_name,
            'sector': ipo.sector,
            'price_band': ipo.price_band,
            'issue_size': ipo.issue_size,
            'open_date': ipo.open_date.strftime('%Y-%m-%d'),
            'close_date': ipo.close_date.strftime('%Y-%m-%d'),
            'lot_size': ipo.lot_size,
            'listing_date': ipo.listing_date.strftime('%Y-%m-%d') if ipo.listing_date else 'TBD',
            'gmp': ipo.gmp,
        }

        if ipo.open_date <= today <= ipo.close_date:
            ipo_dict['status'] = 'OPEN'
        elif today < ipo.open_date:
            ipo_dict['status'] = 'UPCOMING'
        else:
            ipo_dict['status'] = 'CLOSED'

        ipos.append(ipo_dict)

    cache.set(cache_key, ipos, CACHE_TTL)
    return ipos


def get_recently_listed():
    """Get recently listed IPOs from database with current performance"""
    cache_key = 'ipo_recently_listed_db'
    cached = cache.get(cache_key)
    if cached:
        return cached

    ipos_qs = IPO.objects.filter(is_listed=True).order_by('-listing_date')
    
    results = []
    for ipo in ipos_qs:
        entry = {
            'id': ipo.id,
            'company': ipo.company_name,
            'symbol': ipo.symbol,
            'listing_date': ipo.listing_date.strftime('%Y-%m-%d') if ipo.listing_date else '',
            'issue_price': float(ipo.issue_price) if ipo.issue_price else 0,
            'listing_price': float(ipo.listing_price) if ipo.listing_price else 0,
            'sector': ipo.sector,
        }

        # Try to get current price from yfinance if symbol exists
        if ipo.symbol and entry['issue_price'] > 0:
            try:
                symbol = f"{ipo.symbol}.NS"
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period='1d')
                if not hist.empty:
                    current_price = float(hist['Close'].iloc[-1])
                    entry['current_price'] = round(current_price, 2)
                    entry['return_pct'] = round(
                        ((current_price - entry['issue_price']) / entry['issue_price']) * 100, 2
                    )
                    if entry['listing_price'] > 0:
                        entry['listing_gain_pct'] = round(
                            ((entry['listing_price'] - entry['issue_price']) / entry['issue_price']) * 100, 2
                        )
                    else:
                        entry['listing_gain_pct'] = 0
                else:
                    _fallback_live_price(entry)
            except Exception:
                _fallback_live_price(entry)
        else:
            _fallback_live_price(entry)

        results.append(entry)

    cache.set(cache_key, results, CACHE_TTL)
    return results


def _fallback_live_price(entry):
    """Fallback if yfinance fails or symbol missing"""
    if entry.get('listing_price') and entry.get('issue_price'):
        entry['current_price'] = entry['listing_price']
        entry['return_pct'] = round(
            ((entry['listing_price'] - entry['issue_price']) / entry['issue_price']) * 100, 2
        )
        entry['listing_gain_pct'] = entry['return_pct']
    else:
        entry['current_price'] = 0
        entry['return_pct'] = 0
        entry['listing_gain_pct'] = 0


def get_ipo_stats():
    """Get overall IPO market stats"""
    listed = get_recently_listed()
    upcoming = get_upcoming_ipos()

    positive = sum(1 for ipo in listed if ipo.get('return_pct', 0) > 0)
    total = len(listed) or 1
    avg_return = sum(ipo.get('return_pct', 0) for ipo in listed) / total

    return {
        'total_upcoming': len([i for i in upcoming if i['status'] in ('UPCOMING', 'OPEN')]),
        'total_listed': len(listed),
        'avg_listing_return': round(avg_return, 1),
        'total_open': len([i for i in upcoming if i['status'] == 'OPEN']),
    }
