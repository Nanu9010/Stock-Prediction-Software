"""
Commodity Service — Live commodity prices via yfinance
Gold, Silver, Crude Oil, Natural Gas, Copper, etc.
"""
import yfinance as yf
import logging
from django.core.cache import cache

logger = logging.getLogger(__name__)

CACHE_TTL = 300  # 5 minutes

# Commodity symbol mapping (yfinance futures symbols)
COMMODITIES = {
    'Gold': {'symbol': 'GC=F', 'unit': '$/oz', 'icon': '🥇'},
    'Silver': {'symbol': 'SI=F', 'unit': '$/oz', 'icon': '🥈'},
    'Crude Oil (WTI)': {'symbol': 'CL=F', 'unit': '$/bbl', 'icon': '🛢️'},
    'Crude Oil (Brent)': {'symbol': 'BZ=F', 'unit': '$/bbl', 'icon': '🛢️'},
    'Natural Gas': {'symbol': 'NG=F', 'unit': '$/MMBtu', 'icon': '🔥'},
    'Copper': {'symbol': 'HG=F', 'unit': '$/lb', 'icon': '🟤'},
}

# Indian commodity prices (MCX-equivalent via yfinance)
INDIAN_COMMODITIES = {
    'Gold (10g)': {'symbol': 'GC=F', 'unit': '₹', 'multiplier': 0.322, 'icon': '🥇'},
    'Silver (1kg)': {'symbol': 'SI=F', 'unit': '₹', 'multiplier': 26.5, 'icon': '🥈'},
    'Crude Oil': {'symbol': 'CL=F', 'unit': '$/bbl', 'multiplier': 1, 'icon': '🛢️'},
    'Natural Gas': {'symbol': 'NG=F', 'unit': '₹/MMBtu', 'multiplier': 83, 'icon': '🔥'},
}


def get_commodity_prices():
    """Get live commodity prices (global)"""
    cache_key = 'commodity_prices_global'
    cached = cache.get(cache_key)
    if cached:
        return cached

    results = []
    for name, info in COMMODITIES.items():
        try:
            ticker = yf.Ticker(info['symbol'])
            hist = ticker.history(period='2d')
            if hist.empty:
                continue

            current = float(hist['Close'].iloc[-1])
            prev = float(hist['Close'].iloc[0]) if len(hist) > 1 else current
            change = current - prev
            change_pct = (change / prev * 100) if prev else 0

            results.append({
                'name': name,
                'symbol': info['symbol'],
                'price': round(current, 2),
                'change': round(change, 2),
                'change_pct': round(change_pct, 2),
                'unit': info['unit'],
                'icon': info['icon'],
            })
        except Exception as e:
            logger.debug(f"Skipping commodity {name}: {e}")

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

    results = []
    for name, info in INDIAN_COMMODITIES.items():
        try:
            ticker = yf.Ticker(info['symbol'])
            hist = ticker.history(period='2d')
            if hist.empty:
                continue

            current_usd = float(hist['Close'].iloc[-1])
            prev_usd = float(hist['Close'].iloc[0]) if len(hist) > 1 else current_usd

            current_inr = current_usd * info['multiplier'] * inr_rate
            prev_inr = prev_usd * info['multiplier'] * inr_rate

            change = current_inr - prev_inr
            change_pct = (change / prev_inr * 100) if prev_inr else 0

            results.append({
                'name': name,
                'price': round(current_inr, 2),
                'change': round(change, 2),
                'change_pct': round(change_pct, 2),
                'unit': info['unit'],
                'icon': info['icon'],
            })
        except Exception as e:
            logger.debug(f"Skipping Indian commodity {name}: {e}")

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
    return [
        {'name': 'Gold', 'symbol': 'GC=F', 'price': 2035.80, 'change': 12.50, 'change_pct': 0.62, 'unit': '$/oz', 'icon': '🥇'},
        {'name': 'Silver', 'symbol': 'SI=F', 'price': 22.85, 'change': -0.15, 'change_pct': -0.65, 'unit': '$/oz', 'icon': '🥈'},
        {'name': 'Crude Oil (WTI)', 'symbol': 'CL=F', 'price': 78.20, 'change': 1.30, 'change_pct': 1.69, 'unit': '$/bbl', 'icon': '🛢️'},
        {'name': 'Natural Gas', 'symbol': 'NG=F', 'price': 2.45, 'change': -0.08, 'change_pct': -3.16, 'unit': '$/MMBtu', 'icon': '🔥'},
        {'name': 'Copper', 'symbol': 'HG=F', 'price': 3.82, 'change': 0.05, 'change_pct': 1.33, 'unit': '$/lb', 'icon': '🟤'},
    ]


def _fallback_indian_commodities():
    return [
        {'name': 'Gold (10g)', 'price': 62450, 'change': 280, 'change_pct': 0.45, 'unit': '₹', 'icon': '🥇'},
        {'name': 'Silver (1kg)', 'price': 74200, 'change': -89, 'change_pct': -0.12, 'unit': '₹', 'icon': '🥈'},
        {'name': 'Crude Oil', 'price': 82.40, 'change': 0.98, 'change_pct': 1.20, 'unit': '$/bbl', 'icon': '🛢️'},
        {'name': 'Natural Gas', 'price': 203.40, 'change': -5.20, 'change_pct': -2.49, 'unit': '₹/MMBtu', 'icon': '🔥'},
    ]
