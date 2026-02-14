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

# ─── Curated IPO Data (admin-editable in future) ─────────────

UPCOMING_IPOS = [
    {
        'company': 'Hexaware Technologies',
        'sector': 'IT Services',
        'price_band': '₹674 - ₹708',
        'issue_size': '₹8,750 Cr',
        'open_date': '2026-02-12',
        'close_date': '2026-02-14',
        'status': 'OPEN',
        'lot_size': 21,
        'listing_date': '2026-02-19',
        'gmp': '+₹45',
    },
    {
        'company': 'Ajax Engineering',
        'sector': 'Capital Goods',
        'price_band': '₹599 - ₹629',
        'issue_size': '₹1,269 Cr',
        'open_date': '2026-02-10',
        'close_date': '2026-02-12',
        'status': 'CLOSED',
        'lot_size': 23,
        'listing_date': '2026-02-17',
        'gmp': '+₹32',
    },
    {
        'company': 'Quality Power Electrical',
        'sector': 'Electrical Equipment',
        'price_band': '₹401 - ₹425',
        'issue_size': '₹858 Cr',
        'open_date': '2026-02-14',
        'close_date': '2026-02-19',
        'status': 'UPCOMING',
        'lot_size': 35,
        'listing_date': '2026-02-24',
        'gmp': 'N/A',
    },
    {
        'company': 'Denta Water Solutions',
        'sector': 'Water Treatment',
        'price_band': '₹279 - ₹294',
        'issue_size': '₹220 Cr',
        'open_date': '2026-02-22',
        'close_date': '2026-02-26',
        'status': 'UPCOMING',
        'lot_size': 51,
        'listing_date': '2026-03-03',
        'gmp': 'N/A',
    },
]

RECENTLY_LISTED = [
    {
        'company': 'Swiggy Ltd',
        'symbol': 'SWIGGY',
        'listing_date': '2025-11-13',
        'issue_price': 390,
        'listing_price': 420,
        'sector': 'Internet / Food Tech',
    },
    {
        'company': 'Tata Technologies',
        'symbol': 'TATATECH',
        'listing_date': '2025-11-30',
        'issue_price': 500,
        'listing_price': 1200,
        'sector': 'IT Services',
    },
    {
        'company': 'IREDA',
        'symbol': 'IREDA',
        'listing_date': '2025-11-29',
        'issue_price': 32,
        'listing_price': 50,
        'sector': 'NBFC / Energy',
    },
]


def get_upcoming_ipos():
    """Get upcoming IPOs"""
    cache_key = 'ipo_upcoming'
    cached = cache.get(cache_key)
    if cached:
        return cached

    today = datetime.now().date()
    ipos = []
    for ipo in UPCOMING_IPOS:
        open_date = datetime.strptime(ipo['open_date'], '%Y-%m-%d').date()
        close_date = datetime.strptime(ipo['close_date'], '%Y-%m-%d').date()

        if open_date <= today <= close_date:
            ipo['status'] = 'OPEN'
        elif today < open_date:
            ipo['status'] = 'UPCOMING'
        else:
            ipo['status'] = 'CLOSED'

        ipos.append(ipo)

    cache.set(cache_key, ipos, CACHE_TTL)
    return ipos


def get_recently_listed():
    """Get recently listed IPOs with current performance"""
    cache_key = 'ipo_recently_listed'
    cached = cache.get(cache_key)
    if cached:
        return cached

    results = []
    for ipo in RECENTLY_LISTED:
        entry = dict(ipo)

        # Try to get current price from yfinance
        try:
            symbol = f"{ipo['symbol']}.NS"
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period='1d')
            if not hist.empty:
                current_price = float(hist['Close'].iloc[-1])
                entry['current_price'] = round(current_price, 2)
                entry['return_pct'] = round(
                    ((current_price - ipo['issue_price']) / ipo['issue_price']) * 100, 2
                )
                entry['listing_gain_pct'] = round(
                    ((ipo['listing_price'] - ipo['issue_price']) / ipo['issue_price']) * 100, 2
                )
            else:
                entry['current_price'] = ipo['listing_price']
                entry['return_pct'] = round(
                    ((ipo['listing_price'] - ipo['issue_price']) / ipo['issue_price']) * 100, 2
                )
                entry['listing_gain_pct'] = entry['return_pct']
        except Exception:
            entry['current_price'] = ipo['listing_price']
            entry['return_pct'] = round(
                ((ipo['listing_price'] - ipo['issue_price']) / ipo['issue_price']) * 100, 2
            )
            entry['listing_gain_pct'] = entry['return_pct']

        results.append(entry)

    cache.set(cache_key, results, CACHE_TTL)
    return results


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
