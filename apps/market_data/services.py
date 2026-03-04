"""
Market Data services using infrastructure client
"""
from decimal import Decimal
from apps.market_data.models import MarketIndex, StockPrice, PopularStock, GainersLosers
from infrastructure.market_data_client import MarketDataClient
from django.utils import timezone
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)

# Initialize client
client = MarketDataClient()

CACHE_TTL_INDICES  = 180   # 3 min
CACHE_TTL_GAINERS  = 300   # 5 min
CACHE_TTL_ACTIVE   = 300   # 5 min
CACHE_TTL_TICKER   = 180   # 3 min


def fetch_stock_price(symbol):
    """
    Fetch current stock price using infrastructure client
    """
    return client.fetch_stock_price(symbol)


def update_index_prices():
    """Update all market indices using infrastructure client"""
    updated_count = 0
    
    for index_code in client.INDIAN_SYMBOLS.keys():
        try:
            price_data = client.fetch_stock_price(index_code)
            
            if not price_data:
                continue
            
            MarketIndex.objects.update_or_create(
                symbol=index_code,
                defaults={
                    'name': price_data.get('company_name', index_code),
                    'current_price': price_data['current_price'],
                    'change': price_data['change'],
                    'change_percent': price_data['change_percent'],
                    'open_price': price_data.get('open_price', price_data['current_price']),
                    'high': price_data.get('high', price_data['current_price']),
                    'low': price_data.get('low', price_data['current_price']),
                    'previous_close': price_data.get('previous_close', price_data['current_price']),
                }
            )
            updated_count += 1
            
        except Exception as e:
            logger.error(f"Error updating index {index_code}: {e}")
    
    return updated_count


def update_popular_stocks():
    """Update prices for popular stocks"""
    popular_stocks = PopularStock.objects.filter(is_active=True)
    updated_count = 0
    
    for stock in popular_stocks:
        price_data = client.fetch_stock_price(stock.symbol)
        
        if price_data:
            StockPrice.objects.update_or_create(
                symbol=stock.symbol,
                defaults={
                    'current_price': price_data['current_price'],
                    'change': price_data['change'],
                    'change_percent': price_data['change_percent'],
                    'volume': price_data['volume'],
                    'market_cap': price_data['market_cap'],
                    'company_name': price_data['company_name'],
                }
            )
            updated_count += 1
    
    return updated_count


def get_stock_history(symbol, period='1mo'):
    """Get historical stock data"""
    return client.get_stock_history(symbol, period)


def get_market_summary():
    """Get summary of all market indices (legacy endpoint)"""
    indices = MarketIndex.objects.all()
    
    return {
        'indices': [
            {
                'symbol': idx.symbol,
                'name': idx.name,
                'price': float(idx.current_price),
                'change': float(idx.change),
                'change_percent': float(idx.change_percent),
            }
            for idx in indices
        ],
        'updated_at': timezone.now().isoformat(),
    }


def get_live_indices():
    """
    Return the 5 priority indices: NIFTY50, SENSEX, BANKNIFTY, FINNIFTY, MIDCPNIFTY.
    Reads from DB (populated by Celery task or manual update).
    Falls back to live yfinance fetch if DB is empty.
    """
    cache_key = 'live_indices_v2'
    cached = cache.get(cache_key)
    if cached:
        return cached

    priority = ['NIFTY50', 'SENSEX', 'BANKNIFTY', 'FINNIFTY', 'MIDCPNIFTY']
    display_names = {
        'NIFTY50':    'NIFTY 50',
        'SENSEX':     'SENSEX',
        'BANKNIFTY':  'BANK NIFTY',
        'FINNIFTY':   'FIN NIFTY',
        'MIDCPNIFTY': 'MIDCAP NIFTY',
    }

    db_indices = {idx.symbol: idx for idx in MarketIndex.objects.filter(symbol__in=priority)}
    results = []

    for sym in priority:
        if sym in db_indices:
            idx = db_indices[sym]
            results.append({
                'symbol':      sym,
                'name':        display_names.get(sym, sym),
                'price':       float(idx.current_price),
                'change':      float(idx.change),
                'change_pct':  float(idx.change_percent),
                'is_positive': float(idx.change_percent) >= 0,
            })
        else:
            # Live fetch as last resort
            try:
                data = client.fetch_stock_price(sym)
                if data:
                    results.append({
                        'symbol':      sym,
                        'name':        display_names.get(sym, sym),
                        'price':       float(data['current_price']),
                        'change':      float(data['change']),
                        'change_pct':  float(data['change_percent']),
                        'is_positive': float(data['change_percent']) >= 0,
                    })
            except Exception as e:
                logger.warning(f"Live index fetch failed for {sym}: {e}")

    cache.set(cache_key, results, CACHE_TTL_INDICES)
    return results


def fetch_and_cache_gainers_losers(limit=20):
    """
    Fetch top gainers/losers from NSE (with yfinance fallback) and cache + DB store.
    Returns { 'gainers': [...], 'losers': [...] }
    """
    cache_key = f'gainers_losers_{limit}'
    cached = cache.get(cache_key)
    if cached:
        return cached

    result = client.fetch_nse_gainers_losers(limit=limit)
    gainers = result.get('gainers', [])
    losers  = result.get('losers', [])

    # Persist to GainersLosers model for historical reference
    try:
        GainersLosers.objects.filter(category__in=['GAINER', 'LOSER']).delete()
        gl_objs = []
        for rank, item in enumerate(gainers, 1):
            gl_objs.append(GainersLosers(
                symbol=item['symbol'], company_name=item.get('company_name', ''),
                ltp=item.get('ltp', 0), change=item.get('change', 0),
                change_pct=item.get('change_pct', 0), volume=item.get('volume', 0),
                category='GAINER', rank=rank,
            ))
        for rank, item in enumerate(losers, 1):
            gl_objs.append(GainersLosers(
                symbol=item['symbol'], company_name=item.get('company_name', ''),
                ltp=item.get('ltp', 0), change=item.get('change', 0),
                change_pct=item.get('change_pct', 0), volume=item.get('volume', 0),
                category='LOSER', rank=rank,
            ))
        GainersLosers.objects.bulk_create(gl_objs, ignore_conflicts=True)
    except Exception as e:
        logger.warning(f"GainersLosers DB write error: {e}")

    data = {'gainers': gainers, 'losers': losers}
    cache.set(cache_key, data, CACHE_TTL_GAINERS)
    return data


def get_gainers(limit=20):
    """Get top gainers (cached)"""
    return fetch_and_cache_gainers_losers(limit=limit).get('gainers', [])


def get_losers(limit=20):
    """Get top losers (cached)"""
    return fetch_and_cache_gainers_losers(limit=limit).get('losers', [])


def get_most_active(limit=20):
    """Get most active stocks by volume"""
    cache_key = f'most_active_{limit}'
    cached = cache.get(cache_key)
    if cached:
        return cached
    result = client.fetch_nse_most_active(limit=limit)
    cache.set(cache_key, result, CACHE_TTL_ACTIVE)
    return result


def get_ticker_data():
    """Compact ticker strip data — 5 indices from DB/live"""
    cache_key = 'market_ticker_data'
    cached = cache.get(cache_key)
    if cached:
        return cached

    indices = get_live_indices()
    items = [
        {
            'label':       idx['name'],
            'price':       idx['price'],
            'change':      idx['change'],
            'change_pct':  idx['change_pct'],
            'is_positive': idx['is_positive'],
        }
        for idx in indices
    ]
    cache.set(cache_key, items, CACHE_TTL_TICKER)
    return items


def get_popular_stocks_data():
    """Get current prices for popular stocks"""
    stocks = StockPrice.objects.filter(
        symbol__in=PopularStock.objects.filter(is_active=True).values_list('symbol', flat=True)
    ).order_by('-updated_at')[:20]
    
    return [
        {
            'symbol': stock.symbol,
            'company_name': stock.company_name,
            'price': float(stock.current_price),
            'change': float(stock.change),
            'change_percent': float(stock.change_percent),
        }
        for stock in stocks
    ]

