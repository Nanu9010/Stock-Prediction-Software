"""
Market data services using free yfinance API
"""
import yfinance as yf
from decimal import Decimal
from apps.market_data.models import MarketIndex, StockPrice, PopularStock
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


# Indian stock symbol mapping
INDIAN_SYMBOLS = {
    'NIFTY50': '^NSEI',
    'SENSEX': '^BSESN',
    'BANKNIFTY': '^NSEBANK',
    'NIFTYIT': '^CNXIT',
    'NIFTYPHARMA': '^CNXPHARMA',
}


def get_indian_symbol(symbol):
    """Convert symbol to Yahoo Finance format for Indian stocks"""
    if symbol in INDIAN_SYMBOLS:
        return INDIAN_SYMBOLS[symbol]
    
    # For individual stocks, add .NS for NSE or .BO for BSE
    if not symbol.endswith(('.NS', '.BO')):
        return f"{symbol}.NS"
    return symbol


def fetch_stock_price(symbol):
    """
    Fetch current stock price using yfinance (FREE)
    
    Args:
        symbol: Stock symbol (e.g., 'RELIANCE', 'TCS')
    
    Returns:
        dict with price data or None
    """
    try:
        yf_symbol = get_indian_symbol(symbol)
        ticker = yf.Ticker(yf_symbol)
        info = ticker.info
        
        if not info:
            return None
        
        current_price = info.get('currentPrice') or info.get('regularMarketPrice')
        previous_close = info.get('previousClose')
        
        if not current_price or not previous_close:
            return None
        
        change = current_price - previous_close
        change_percent = (change / previous_close) * 100
        
        return {
            'symbol': symbol,
            'current_price': Decimal(str(current_price)),
            'change': Decimal(str(change)),
            'change_percent': Decimal(str(change_percent)),
            'volume': info.get('volume', 0),
            'market_cap': info.get('marketCap'),
            'company_name': info.get('longName', symbol),
        }
    
    except Exception as e:
        logger.error(f"Error fetching price for {symbol}: {e}")
        return None


def update_index_prices():
    """Update all market indices using yfinance (FREE)"""
    updated_count = 0
    
    for index_code, yf_symbol in INDIAN_SYMBOLS.items():
        try:
            ticker = yf.Ticker(yf_symbol)
            info = ticker.info
            
            if not info:
                continue
            
            current_price = info.get('regularMarketPrice')
            previous_close = info.get('previousClose')
            
            if not current_price or not previous_close:
                continue
            
            change = current_price - previous_close
            change_percent = (change / previous_close) * 100
            
            MarketIndex.objects.update_or_create(
                symbol=index_code,
                defaults={
                    'name': info.get('longName', index_code),
                    'current_price': Decimal(str(current_price)),
                    'change': Decimal(str(change)),
                    'change_percent': Decimal(str(change_percent)),
                    'open_price': Decimal(str(info.get('regularMarketOpen', current_price))),
                    'high': Decimal(str(info.get('dayHigh', current_price))),
                    'low': Decimal(str(info.get('dayLow', current_price))),
                    'previous_close': Decimal(str(previous_close)),
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
        price_data = fetch_stock_price(stock.symbol)
        
        if price_data:
            StockPrice.objects.update_or_create(
                symbol=stock.symbol,
                defaults=price_data
            )
            updated_count += 1
    
    return updated_count


def get_stock_history(symbol, period='1mo'):
    """
    Get historical stock data (FREE)
    
    Args:
        symbol: Stock symbol
        period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, max)
    
    Returns:
        DataFrame with historical data
    """
    try:
        yf_symbol = get_indian_symbol(symbol)
        ticker = yf.Ticker(yf_symbol)
        hist = ticker.history(period=period)
        return hist
    
    except Exception as e:
        logger.error(f"Error fetching history for {symbol}: {e}")
        return None


def get_market_summary():
    """Get summary of all market indices"""
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
        'updated_at': timezone.now()
    }


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
