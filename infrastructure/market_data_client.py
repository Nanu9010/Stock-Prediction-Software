"""
Market Data Client implementation using yfinance (FREE)
"""
import yfinance as yf
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

class MarketDataClient:
    """Client for fetching market data from external APIs"""
    
    # Indian stock symbol mapping
    INDIAN_SYMBOLS = {
        'NIFTY50': '^NSEI',
        'SENSEX': '^BSESN',
        'BANKNIFTY': '^NSEBANK',
        'NIFTYIT': '^CNXIT',
        'NIFTYPHARMA': '^CNXPHARMA',
    }
    
    def _get_indian_symbol(self, symbol):
        """Convert symbol to Yahoo Finance format for Indian stocks"""
        if symbol in self.INDIAN_SYMBOLS:
            return self.INDIAN_SYMBOLS[symbol]
        
        # For individual stocks, add .NS for NSE or .BO for BSE
        if not symbol.endswith(('.NS', '.BO')):
            return f"{symbol}.NS"
        return symbol

    def fetch_stock_price(self, symbol):
        """
        Fetch current stock price using yfinance
        
        Args:
            symbol: Stock symbol (e.g., 'RELIANCE', 'TCS')
        
        Returns:
            dict with price data or None
        """
        try:
            yf_symbol = self._get_indian_symbol(symbol)
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
                'open_price': Decimal(str(info.get('regularMarketOpen', current_price))),
                'high': Decimal(str(info.get('dayHigh', current_price))),
                'low': Decimal(str(info.get('dayLow', current_price))),
                'previous_close': Decimal(str(previous_close)),
            }
        
        except Exception as e:
            logger.error(f"Error fetching price for {symbol}: {e}")
            return None

    def get_stock_history(self, symbol, period='1mo'):
        """
        Get historical stock data
        
        Args:
            symbol: Stock symbol
            period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, max)
        
        Returns:
            DataFrame with historical data
        """
        try:
            yf_symbol = self._get_indian_symbol(symbol)
            ticker = yf.Ticker(yf_symbol)
            hist = ticker.history(period=period)
            return hist
        
        except Exception as e:
            logger.error(f"Error fetching history for {symbol}: {e}")
            return None
