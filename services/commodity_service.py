"""
Commodity Service — Live commodity prices via yfinance
Gold, Silver, Crude Oil, Natural Gas, Copper, etc.
"""
import yfinance as yf
import logging
from django.core.cache import cache

logger = logging.getLogger(__name__)

CACHE_TTL = 300  # 5 minutes

from apps.market_data.models import Commodity


def get_commodity_prices():
    """Get live commodity prices (global)"""
    cache_key = 'commodity_prices_global'
    cached = cache.get(cache_key)
    if cached:
        return cached

    results = []
    commodities = Commodity.objects.filter(is_active=True, is_global=True)
    
    results = []
    for item in commodities:
        try:
            ticker = yf.Ticker(item.symbol)
            hist = ticker.history(period='2d')
            if hist.empty:
                continue

            current = float(hist['Close'].iloc[-1])
            prev = float(hist['Close'].iloc[0]) if len(hist) > 1 else current
            change = current - prev
            change_pct = (change / prev * 100) if prev else 0

            results.append({
                'name': item.name,
                'symbol': item.symbol,
                'price': round(current, 2),
                'change': round(change, 2),
                'change_pct': round(change_pct, 2),
                'unit': item.unit,
                'icon': item.icon,
            })
        except Exception as e:
            logger.debug(f"Skipping commodity {item.name}: {e}")

    if not results:
        results = _fallback_commodities()

    cache.set(cache_key, results, CACHE_TTL)
    return results


def get_indian_commodity_prices():
    """Get commodity prices in INR-equivalent (MCX style)"""
    cache_key = 'commodity_prices_indian'
    cached = cache.get(cache_key)
    if cached:
        return cached

    # Get USD/INR rate
    inr_rate = _get_usd_inr_rate()

    indic_commodities = Commodity.objects.filter(is_active=True, is_global=False)

    results = []
    for item in indic_commodities:
        try:
            ticker = yf.Ticker(item.symbol)
            hist = ticker.history(period='2d')
            if hist.empty:
                continue

            current_usd = float(hist['Close'].iloc[-1])
            prev_usd = float(hist['Close'].iloc[0]) if len(hist) > 1 else current_usd

            multiplier = float(item.mcx_multiplier)
            current_inr = current_usd * multiplier * inr_rate
            prev_inr = prev_usd * multiplier * inr_rate

            change = current_inr - prev_inr
            change_pct = (change / prev_inr * 100) if prev_inr else 0

            results.append({
                'name': item.name,
                'price': round(current_inr, 2),
                'change': round(change, 2),
                'change_pct': round(change_pct, 2),
                'unit': item.unit,
                'icon': item.icon,
            })
        except Exception as e:
            logger.debug(f"Skipping Indian commodity {item.name}: {e}")

    if not results:
        results = _fallback_indian_commodities()

    cache.set(cache_key, results, CACHE_TTL)
    return results


def _get_usd_inr_rate():
    """Get current USD/INR exchange rate"""
    try:
        ticker = yf.Ticker('USDINR=X')
        info = ticker.info
        return info.get('regularMarketPrice', 83.0)
    except Exception:
        return 83.0  # Fallback rate


def _fallback_commodities():
    return []


def _fallback_indian_commodities():
    return []
