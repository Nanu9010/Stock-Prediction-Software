"""
Market Data Client implementation using yfinance (FREE) + NSE JSON (with fallback)
"""
import yfinance as yf
import requests
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

# NSE JSON API headers (simulates browser to avoid 401/403)
NSE_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Referer': 'https://www.nseindia.com/',
}

# NIFTY 50 constituent symbols for yfinance fallback
NIFTY50_SYMBOLS = [
    'RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'ICICIBANK',
    'HINDUNILVR', 'SBIN', 'BHARTIARTL', 'ITC', 'KOTAKBANK',
    'LT', 'HCLTECH', 'AXISBANK', 'ASIANPAINT', 'MARUTI',
    'SUNPHARMA', 'TITAN', 'BAJFINANCE', 'DMART', 'ULTRACEMCO',
    'NTPC', 'TATAMOTORS', 'WIPRO', 'ONGC', 'SHRIRAMFIN',
    'ADANIENT', 'ADANIPORTS', 'POWERGRID', 'NESTLEIND', 'JSWSTEEL',
    'TATASTEEL', 'TECHM', 'HDFCLIFE', 'BAJAJFINSV', 'DIVISLAB',
    'CIPLA', 'DRREDDY', 'BPCL', 'COALINDIA', 'BRITANNIA',
    'EICHERMOT', 'APOLLOHOSP', 'SBILIFE', 'TATACONSUM', 'HEROMOTOCO',
    'GRASIM', 'INDUSINDBK', 'BAJAJ-AUTO', 'HINDALCO', 'BEL',
]


class MarketDataClient:
    """Client for fetching market data from external APIs"""
    
    # Indian stock symbol mapping
    INDIAN_SYMBOLS = {
        'NIFTY50':     '^NSEI',
        'SENSEX':      '^BSESN',
        'BANKNIFTY':   '^NSEBANK',
        'FINNIFTY':    '^CNXFIN',
        'MIDCPNIFTY':  '^NSEMDCP50',
        'NIFTYIT':     '^CNXIT',
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

    # ─── NSE JSON API methods (with yfinance fallback) ──────────────────────

    def _nse_get(self, url, timeout=8):
        """Make a request to NSE with browser-like headers. Returns JSON or None."""
        try:
            session = requests.Session()
            # First hit the NSE home page to get cookies
            session.get('https://www.nseindia.com', headers=NSE_HEADERS, timeout=timeout)
            resp = session.get(url, headers=NSE_HEADERS, timeout=timeout)
            if resp.status_code == 200:
                return resp.json()
        except Exception as e:
            logger.debug(f"NSE API request failed ({url}): {e}")
        return None

    def fetch_nse_gainers_losers(self, index='NIFTY', limit=20):
        """
        Fetch top gainers and losers from NSE JSON API.
        Falls back to yfinance batch fetch if NSE is unavailable.
        Returns { 'gainers': [...], 'losers': [...] }
        """
        url = f"https://www.nseindia.com/api/live-analysis-variations?index={index}"
        data = self._nse_get(url)
        
        if data:
            try:
                gainers = []
                losers = []
                all_stocks = data.get('NIFTY500', data.get(index, []))
                if isinstance(all_stocks, list):
                    for s in all_stocks:
                        item = {
                            'symbol': s.get('symbol', ''),
                            'company_name': s.get('companyName', s.get('symbol', '')),
                            'ltp': round(float(s.get('ltp', 0)), 2),
                            'change': round(float(s.get('netPrice', 0)), 2),
                            'change_pct': round(float(s.get('netPrice', 0)), 2),
                            'volume': int(s.get('tradedQuantity', 0)),
                            'series': s.get('series', 'EQ'),
                        }
                        if item['change_pct'] > 0:
                            gainers.append(item)
                        elif item['change_pct'] < 0:
                            losers.append(item)
                    gainers.sort(key=lambda x: x['change_pct'], reverse=True)
                    losers.sort(key=lambda x: x['change_pct'])
                    return {'gainers': gainers[:limit], 'losers': losers[:limit]}
            except Exception as e:
                logger.warning(f"NSE gainers/losers parse error: {e}")

        # Fallback: use yfinance batch download on NIFTY 50 symbols
        logger.info("Falling back to yfinance for gainers/losers")
        return self._yfinance_gainers_losers(limit=limit)

    def _yfinance_gainers_losers(self, limit=20):
        """yfinance fallback for gainers/losers from NIFTY 50 universe"""
        try:
            yf_symbols = [f"{s}.NS" for s in NIFTY50_SYMBOLS]
            data = yf.download(
                ' '.join(yf_symbols), period='1d',
                group_by='ticker', progress=False, threads=True, auto_adjust=True
            )
            results = []
            for sym in NIFTY50_SYMBOLS:
                yf_sym = f"{sym}.NS"
                try:
                    if len(NIFTY50_SYMBOLS) == 1:
                        td = data
                    else:
                        if yf_sym not in data.columns.get_level_values(0):
                            continue
                        td = data[yf_sym]
                    if td.empty:
                        continue
                    close = float(td['Close'].iloc[-1])
                    open_p = float(td['Open'].iloc[-1])
                    volume = int(td['Volume'].iloc[-1]) if 'Volume' in td.columns else 0
                    if open_p == 0:
                        continue
                    change = close - open_p
                    change_pct = (change / open_p) * 100
                    results.append({
                        'symbol': sym,
                        'company_name': sym,
                        'ltp': round(close, 2),
                        'change': round(change, 2),
                        'change_pct': round(change_pct, 2),
                        'volume': volume,
                    })
                except Exception:
                    continue
            results.sort(key=lambda x: x['change_pct'], reverse=True)
            gainers = [r for r in results if r['change_pct'] > 0][:limit]
            losers = sorted([r for r in results if r['change_pct'] < 0], key=lambda x: x['change_pct'])[:limit]
            return {'gainers': gainers, 'losers': losers}
        except Exception as e:
            logger.error(f"yfinance gainers/losers fallback failed: {e}")
            return {'gainers': [], 'losers': []}

    def fetch_nse_most_active(self, limit=20):
        """Fetch most active stocks by traded value from NSE API. Falls back to yfinance volume sort."""
        url = "https://www.nseindia.com/api/live-analysis-most-active-securities?index=nifty500"
        data = self._nse_get(url)
        if data:
            try:
                stocks = data.get('data', [])
                results = []
                for s in stocks[:limit]:
                    results.append({
                        'symbol': s.get('symbol', ''),
                        'company_name': s.get('companyName', s.get('symbol', '')),
                        'ltp': round(float(s.get('ltp', 0)), 2),
                        'change_pct': round(float(s.get('pChange', 0)), 2),
                        'volume': int(s.get('totalTradedVolume', 0)),
                        'traded_value': round(float(s.get('totalTradedValue', 0)), 2),
                    })
                if results:
                    return results
            except Exception as e:
                logger.warning(f"NSE most active parse error: {e}")
        # Fallback: use cached gainers/losers data sorted by volume
        fallback = self._yfinance_gainers_losers(limit=limit * 2)
        all_stocks = fallback['gainers'] + fallback['losers']
        all_stocks.sort(key=lambda x: x.get('volume', 0), reverse=True)
        return all_stocks[:limit]

    def fetch_ticker_data(self):
        """Compact data for the scrolling market ticker strip (5 indices + top stocks)"""
        items = []
        priority_indices = [
            ('NIFTY 50', 'NIFTY50'),
            ('SENSEX', 'SENSEX'),
            ('BANK NIFTY', 'BANKNIFTY'),
            ('FIN NIFTY', 'FINNIFTY'),
            ('MIDCAP', 'MIDCPNIFTY'),
        ]
        for display_name, key in priority_indices:
            yf_sym = self.INDIAN_SYMBOLS.get(key)
            if not yf_sym:
                continue
            try:
                ticker = yf.Ticker(yf_sym)
                info = ticker.info
                current = info.get('regularMarketPrice') or info.get('currentPrice', 0)
                prev = info.get('previousClose', current)
                if current and prev:
                    change = current - prev
                    change_pct = (change / prev * 100) if prev else 0
                    items.append({
                        'label': display_name,
                        'price': round(current, 2),
                        'change': round(change, 2),
                        'change_pct': round(change_pct, 2),
                        'is_positive': change_pct >= 0,
                    })
            except Exception as e:
                logger.debug(f"Ticker skip {key}: {e}")
        return items
