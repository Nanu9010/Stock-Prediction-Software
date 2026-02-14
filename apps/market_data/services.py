"""
Market Data services using infrastructure client
"""
from decimal import Decimal
from apps.market_data.models import MarketIndex, StockPrice, PopularStock
from infrastructure.market_data_client import MarketDataClient
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

# Initialize client
client = MarketDataClient()

def fetch_stock_price(symbol):
    """
    Fetch current stock price using infrastructure client
    
    Args:
        symbol: Stock symbol (e.g., 'RELIANCE', 'TCS')
    
    Returns:
        dict with price data or None
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
    """
    Get historical stock data
    """
    return client.get_stock_history(symbol, period)


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
