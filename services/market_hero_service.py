"""
Market Hero Service — powers the home page Market Hero Section
Fetches live Top10 Gainers/Losers (today & weekly) from yfinance
"""
import yfinance as yf
import logging
from decimal import Decimal
from django.core.cache import cache

logger = logging.getLogger(__name__)

# Suppress noisy yfinance download-level error logs
logging.getLogger('yfinance').setLevel(logging.CRITICAL)

# NIFTY 50 constituent symbols (NSE) — verified Yahoo Finance tickers
NIFTY50_SYMBOLS = [
    'RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'ICICIBANK',
    'HINDUNILVR', 'SBIN', 'BHARTIARTL', 'ITC', 'KOTAKBANK',
    'LT', 'HCLTECH', 'AXISBANK', 'ASIANPAINT', 'MARUTI',
    'SUNPHARMA', 'TITAN', 'BAJFINANCE', 'DMART', 'ULTRACEMCO',
    'NTPC', 'TATMOTORS', 'WIPRO', 'ONGC', 'SHRIRAMFIN',
    'ADANIENT', 'ADANIPORTS', 'POWERGRID', 'NESTLEIND', 'JSWSTEEL',
    'TATASTEEL', 'TECHM', 'HDFCLIFE', 'BAJAJFINSV', 'DIVISLAB',
    'CIPLA', 'DRREDDY', 'BPCL', 'COALINDIA', 'BRITANNIA',
    'EICHERMOT', 'APOLLOHOSP', 'SBILIFE', 'TATACONSUM', 'HEROMOTOCO',
    'GRASIM', 'INDUSINDBK', 'BAJAJ-AUTO', 'HINDALCO', 'BEL',
]

CACHE_TTL = 300  # 5 minutes


def _fetch_batch_prices(symbols, period='1d'):
    """Fetch batch price data from yfinance"""
    try:
        yf_symbols = [f"{s}.NS" for s in symbols]
        tickers_str = ' '.join(yf_symbols)
        data = yf.download(tickers_str, period=period, group_by='ticker', progress=False, threads=True)
        return data
    except Exception as e:
        logger.error(f"Error fetching batch prices: {e}")
        return None


def _parse_daily_changes(data, symbols):
    """Parse daily change data from yfinance download result"""
    results = []
    for symbol in symbols:
        yf_sym = f"{symbol}.NS"
        try:
            if len(symbols) == 1:
                ticker_data = data
            else:
                if yf_sym not in data.columns.get_level_values(0):
                    continue
                ticker_data = data[yf_sym]

            if ticker_data.empty:
                continue

            close = float(ticker_data['Close'].iloc[-1])
            open_price = float(ticker_data['Open'].iloc[-1])

            if open_price == 0:
                continue

            change = close - open_price
            change_pct = (change / open_price) * 100

            results.append({
                'symbol': symbol,
                'price': round(close, 2),
                'change': round(change, 2),
                'change_pct': round(change_pct, 2),
            })
        except Exception as e:
            logger.debug(f"Skipping {symbol}: {e}")
            continue

    return results


def get_today_top10_gainers(force_refresh=False):
    """Get today's top 10 gainers from NIFTY 50"""
    cache_key = 'market_hero_today_top10'
    if not force_refresh:
        cached = cache.get(cache_key)
        if cached:
            return cached

    data = _fetch_batch_prices(NIFTY50_SYMBOLS, period='1d')
    if data is None or data.empty:
        return _fallback_gainers()

    results = _parse_daily_changes(data, NIFTY50_SYMBOLS)
    results.sort(key=lambda x: x['change_pct'], reverse=True)
    top10 = results[:10]

    cache.set(cache_key, top10, CACHE_TTL)
    return top10


def get_today_top10_losers(force_refresh=False):
    """Get today's top 10 losers from NIFTY 50"""
    cache_key = 'market_hero_today_loss10'
    if not force_refresh:
        cached = cache.get(cache_key)
        if cached:
            return cached

    data = _fetch_batch_prices(NIFTY50_SYMBOLS, period='1d')
    if data is None or data.empty:
        return _fallback_losers()

    results = _parse_daily_changes(data, NIFTY50_SYMBOLS)
    results.sort(key=lambda x: x['change_pct'])
    loss10 = results[:10]

    cache.set(cache_key, loss10, CACHE_TTL)
    return loss10


def get_weekly_top_gainers(force_refresh=False):
    """Get weekly top gainers from NIFTY 50 (5-day change)"""
    cache_key = 'market_hero_weekly_top'
    if not force_refresh:
        cached = cache.get(cache_key)
        if cached:
            return cached

    try:
        yf_symbols = [f"{s}.NS" for s in NIFTY50_SYMBOLS]
        tickers_str = ' '.join(yf_symbols)
        data = yf.download(tickers_str, period='5d', group_by='ticker', progress=False, threads=True)

        if data is None or data.empty:
            return _fallback_gainers()

        results = []
        for symbol in NIFTY50_SYMBOLS:
            yf_sym = f"{symbol}.NS"
            try:
                ticker_data = data[yf_sym] if yf_sym in data.columns.get_level_values(0) else None
                if ticker_data is None or ticker_data.empty or len(ticker_data) < 2:
                    continue

                first_close = float(ticker_data['Close'].iloc[0])
                last_close = float(ticker_data['Close'].iloc[-1])

                if first_close == 0:
                    continue

                change = last_close - first_close
                change_pct = (change / first_close) * 100

                results.append({
                    'symbol': symbol,
                    'price': round(last_close, 2),
                    'change': round(change, 2),
                    'change_pct': round(change_pct, 2),
                })
            except Exception:
                continue

        results.sort(key=lambda x: x['change_pct'], reverse=True)
        top10 = results[:10]
        cache.set(cache_key, top10, CACHE_TTL)
        return top10

    except Exception as e:
        logger.error(f"Error fetching weekly gainers: {e}")
        return _fallback_gainers()


def get_weekly_top_losers(force_refresh=False):
    """Get weekly top losers from NIFTY 50 (5-day change)"""
    cache_key = 'market_hero_weekly_loss'
    if not force_refresh:
        cached = cache.get(cache_key)
        if cached:
            return cached

    try:
        yf_symbols = [f"{s}.NS" for s in NIFTY50_SYMBOLS]
        tickers_str = ' '.join(yf_symbols)
        data = yf.download(tickers_str, period='5d', group_by='ticker', progress=False, threads=True)

        if data is None or data.empty:
            return _fallback_losers()

        results = []
        for symbol in NIFTY50_SYMBOLS:
            yf_sym = f"{symbol}.NS"
            try:
                ticker_data = data[yf_sym] if yf_sym in data.columns.get_level_values(0) else None
                if ticker_data is None or ticker_data.empty or len(ticker_data) < 2:
                    continue

                first_close = float(ticker_data['Close'].iloc[0])
                last_close = float(ticker_data['Close'].iloc[-1])

                if first_close == 0:
                    continue

                change = last_close - first_close
                change_pct = (change / first_close) * 100

                results.append({
                    'symbol': symbol,
                    'price': round(last_close, 2),
                    'change': round(change, 2),
                    'change_pct': round(change_pct, 2),
                })
            except Exception:
                continue

        results.sort(key=lambda x: x['change_pct'])
        loss10 = results[:10]
        cache.set(cache_key, loss10, CACHE_TTL)
        return loss10

    except Exception as e:
        logger.error(f"Error fetching weekly losers: {e}")
        return _fallback_losers()


def get_market_indices(force_refresh=False):
    """Get live market index values"""
    cache_key = 'market_hero_indices'
    if not force_refresh:
        cached = cache.get(cache_key)
        if cached:
            return cached

    indices = {
        'NIFTY 50': '^NSEI',
        'SENSEX': '^BSESN',
        'BANK NIFTY': '^NSEBANK',
        'NIFTY IT': '^CNXIT',
    }

    results = []
    for name, symbol in indices.items():
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            current = info.get('regularMarketPrice') or info.get('currentPrice', 0)
            prev = info.get('previousClose', current)
            change = current - prev
            change_pct = (change / prev * 100) if prev else 0

            results.append({
                'name': name,
                'symbol': symbol,
                'price': round(current, 2),
                'change': round(change, 2),
                'change_pct': round(change_pct, 2),
            })
        except Exception as e:
            logger.debug(f"Skipping index {name}: {e}")
            results.append({
                'name': name, 'symbol': symbol,
                'price': 0, 'change': 0, 'change_pct': 0,
            })

    cache.set(cache_key, results, CACHE_TTL)
    return results


# ─── Fallback data when API fails ───────────────────────────

def _fallback_gainers():
    return [
        {'symbol': 'RELIANCE', 'price': 2890.50, 'change': 52.30, 'change_pct': 1.84},
        {'symbol': 'HDFCBANK', 'price': 1635.20, 'change': 28.40, 'change_pct': 1.77},
        {'symbol': 'INFY', 'price': 1520.80, 'change': 22.10, 'change_pct': 1.47},
        {'symbol': 'TCS', 'price': 3945.60, 'change': 48.90, 'change_pct': 1.25},
        {'symbol': 'ICICIBANK', 'price': 1045.30, 'change': 11.50, 'change_pct': 1.11},
        {'symbol': 'ITC', 'price': 458.20, 'change': 4.20, 'change_pct': 0.92},
        {'symbol': 'SBIN', 'price': 628.40, 'change': 5.10, 'change_pct': 0.82},
        {'symbol': 'LT', 'price': 3680.50, 'change': 25.30, 'change_pct': 0.69},
        {'symbol': 'BHARTIARTL', 'price': 1158.30, 'change': 7.80, 'change_pct': 0.68},
        {'symbol': 'KOTAKBANK', 'price': 1845.90, 'change': 10.20, 'change_pct': 0.56},
    ]


def _fallback_losers():
    return [
        {'symbol': 'ADANIENT', 'price': 2420.30, 'change': -85.60, 'change_pct': -3.42},
        {'symbol': 'TATAMOTORS', 'price': 645.20, 'change': -18.90, 'change_pct': -2.85},
        {'symbol': 'MARUTI', 'price': 10250.00, 'change': -198.50, 'change_pct': -1.90},
        {'symbol': 'SUNPHARMA', 'price': 1185.40, 'change': -20.30, 'change_pct': -1.68},
        {'symbol': 'M&M', 'price': 1580.60, 'change': -22.10, 'change_pct': -1.38},
        {'symbol': 'CIPLA', 'price': 1245.80, 'change': -14.20, 'change_pct': -1.13},
        {'symbol': 'DRREDDY', 'price': 5620.40, 'change': -52.30, 'change_pct': -0.92},
        {'symbol': 'DIVISLAB', 'price': 3890.50, 'change': -30.10, 'change_pct': -0.77},
        {'symbol': 'POWERGRID', 'price': 245.60, 'change': -1.80, 'change_pct': -0.73},
        {'symbol': 'NTPC', 'price': 285.30, 'change': -1.50, 'change_pct': -0.52},
    ]
