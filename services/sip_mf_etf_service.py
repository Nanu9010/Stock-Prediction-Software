"""
SIP, Mutual Funds, ETF, Bonds, and Liquidity Service
Combines curated data with live yfinance prices where available
"""
import yfinance as yf
import logging
from django.core.cache import cache

logger = logging.getLogger(__name__)

# Suppress noisy yfinance download-level error logs
logging.getLogger('yfinance').setLevel(logging.CRITICAL)

CACHE_TTL = 600  # 10 minutes

# ─── ETF Data (live from yfinance) ──────────────────────────

POPULAR_ETFS = [
    {'name': 'Nippon India Nifty BeES', 'symbol': 'NIFTYBEES.NS', 'short': 'NIFTYBEES', 'category': 'Index'},
    {'name': 'Nippon India Bank BeES', 'symbol': 'BANKBEES.NS', 'short': 'BANKBEES', 'category': 'Banking'},
    {'name': 'Nippon India Gold BeES', 'symbol': 'GOLDBEES.NS', 'short': 'GOLDBEES', 'category': 'Gold'},
    {'name': 'SBI ETF Nifty 50', 'symbol': 'SETFNIF50.NS', 'short': 'SETFNIF50', 'category': 'Index'},
    {'name': 'Nippon India Junior BeES', 'symbol': 'JUNIORBEES.NS', 'short': 'JUNIORBEES', 'category': 'Index'},
    {'name': 'Nippon India Silver ETF', 'symbol': 'SILVERBEES.NS', 'short': 'SILVERBEES', 'category': 'Silver'},
    {'name': 'Nippon India Liquid BeES', 'symbol': 'LIQUIDBEES.NS', 'short': 'LIQUIDBEES', 'category': 'Liquid'},
    {'name': 'ICICI Pru Bharat 22 ETF', 'symbol': 'ICICIB22.NS', 'short': 'ICICIB22', 'category': 'Thematic'},
]


def get_top_etfs(force_refresh=False):
    """Get popular ETFs with live prices"""
    cache_key = 'etf_top_list'
    if not force_refresh:
        cached = cache.get(cache_key)
        if cached:
            return cached

    results = []
    for etf in POPULAR_ETFS:
        try:
            ticker = yf.Ticker(etf['symbol'])
            hist = ticker.history(period='2d')
            if hist.empty:
                continue

            current = float(hist['Close'].iloc[-1])
            prev = float(hist['Close'].iloc[0]) if len(hist) > 1 else current
            change = current - prev
            change_pct = (change / prev * 100) if prev else 0

            results.append({
                'name': etf['name'],
                'symbol': etf['short'],
                'category': etf['category'],
                'price': round(current, 2),
                'change': round(change, 2),
                'change_pct': round(change_pct, 2),
            })
        except Exception as e:
            logger.debug(f"Skipping ETF {etf['name']}: {e}")

    if not results:
        results = _fallback_etfs()

    cache.set(cache_key, results, CACHE_TTL)
    return results


# ─── Mutual Funds (curated — no free real-time MF NAV API) ──

POPULAR_MUTUAL_FUNDS = [
    {
        'name': 'SBI Bluechip Fund',
        'category': 'Large Cap',
        'aum': '₹45,200 Cr',
        'nav': 78.45,
        'returns_1y': 18.5,
        'returns_3y': 14.2,
        'returns_5y': 12.8,
        'risk': 'Moderate',
        'rating': 5,
    },
    {
        'name': 'HDFC Mid-Cap Opportunities',
        'category': 'Mid Cap',
        'aum': '₹38,800 Cr',
        'nav': 124.30,
        'returns_1y': 25.3,
        'returns_3y': 18.7,
        'returns_5y': 15.4,
        'risk': 'High',
        'rating': 5,
    },
    {
        'name': 'Axis Small Cap Fund',
        'category': 'Small Cap',
        'aum': '₹18,500 Cr',
        'nav': 85.60,
        'returns_1y': 32.1,
        'returns_3y': 22.5,
        'returns_5y': 18.9,
        'risk': 'Very High',
        'rating': 4,
    },
    {
        'name': 'Parag Parikh Flexi Cap',
        'category': 'Flexi Cap',
        'aum': '₹52,100 Cr',
        'nav': 68.20,
        'returns_1y': 20.8,
        'returns_3y': 16.4,
        'returns_5y': 14.1,
        'risk': 'Moderate',
        'rating': 5,
    },
    {
        'name': 'ICICI Pru Technology Fund',
        'category': 'Sectoral',
        'aum': '₹12,600 Cr',
        'nav': 156.80,
        'returns_1y': 28.7,
        'returns_3y': 15.9,
        'returns_5y': 19.2,
        'risk': 'Very High',
        'rating': 4,
    },
    {
        'name': 'Kotak Equity Opportunities',
        'category': 'Large & Mid',
        'aum': '₹22,400 Cr',
        'nav': 245.10,
        'returns_1y': 22.1,
        'returns_3y': 17.3,
        'returns_5y': 14.8,
        'risk': 'Moderate',
        'rating': 4,
    },
]


def get_top_mutual_funds():
    """Get popular mutual funds with returns data"""
    return POPULAR_MUTUAL_FUNDS


# ─── SIP Data (curated) ─────────────────────────────────────

POPULAR_SIPS = [
    {
        'name': 'SBI Nifty 50 Index Fund',
        'min_sip': 500,
        'category': 'Index Fund',
        'returns_1y': 15.2,
        'returns_3y': 12.8,
        'returns_5y': 11.5,
        'popularity': 'Most Popular',
    },
    {
        'name': 'Mirae Asset Large Cap',
        'min_sip': 1000,
        'category': 'Large Cap',
        'returns_1y': 19.8,
        'returns_3y': 15.6,
        'returns_5y': 13.2,
        'popularity': 'Trending',
    },
    {
        'name': 'Quant Small Cap Fund',
        'min_sip': 1000,
        'category': 'Small Cap',
        'returns_1y': 35.4,
        'returns_3y': 28.2,
        'returns_5y': 22.1,
        'popularity': 'Top Performer',
    },
    {
        'name': 'Nippon India Growth Fund',
        'min_sip': 500,
        'category': 'Mid Cap',
        'returns_1y': 24.6,
        'returns_3y': 19.1,
        'returns_5y': 16.3,
        'popularity': 'Rising',
    },
    {
        'name': 'HDFC Balanced Advantage',
        'min_sip': 500,
        'category': 'Hybrid',
        'returns_1y': 14.8,
        'returns_3y': 12.5,
        'returns_5y': 11.8,
        'popularity': 'Stable Pick',
    },
]


def get_top_sip_funds():
    """Get popular SIP investment options"""
    return POPULAR_SIPS


# ─── Bonds Data (curated) ───────────────────────────────────

BONDS_DATA = [
    {
        'name': 'GOI 10Y Bond',
        'type': 'Government',
        'yield_pct': 7.18,
        'maturity': '2034',
        'rating': 'Sovereign',
        'trend': 'stable',
    },
    {
        'name': 'GOI 5Y Bond',
        'type': 'Government',
        'yield_pct': 7.05,
        'maturity': '2029',
        'rating': 'Sovereign',
        'trend': 'down',
    },
    {
        'name': 'SBI Corporate Bond',
        'type': 'Corporate (AAA)',
        'yield_pct': 7.65,
        'maturity': '2028',
        'rating': 'AAA',
        'trend': 'up',
    },
    {
        'name': 'HDFC Ltd Bond',
        'type': 'Corporate (AAA)',
        'yield_pct': 7.82,
        'maturity': '2030',
        'rating': 'AAA',
        'trend': 'stable',
    },
    {
        'name': 'REC Tax-Free Bond',
        'type': 'Tax-Free',
        'yield_pct': 5.45,
        'maturity': '2033',
        'rating': 'AAA',
        'trend': 'stable',
    },
    {
        'name': 'NHAI 54EC Bond',
        'type': 'Capital Gains',
        'yield_pct': 5.25,
        'maturity': '5 Years',
        'rating': 'Sovereign',
        'trend': 'stable',
    },
]


def get_bonds_data():
    """Get bonds market data"""
    return BONDS_DATA


# ─── Liquidity Data (curated) ───────────────────────────────

LIQUIDITY_DATA = [
    {
        'name': 'Overnight MIBOR',
        'rate': 6.50,
        'change': -0.10,
        'type': 'Interbank',
        'description': 'Mumbai Interbank Offered Rate',
    },
    {
        'name': 'RBI Repo Rate',
        'rate': 6.50,
        'change': 0.00,
        'type': 'Policy',
        'description': 'Current RBI policy rate',
    },
    {
        'name': 'RBI Reverse Repo',
        'rate': 3.35,
        'change': 0.00,
        'type': 'Policy',
        'description': 'Reverse repo rate',
    },
    {
        'name': '91-Day T-Bill',
        'rate': 6.75,
        'change': 0.02,
        'type': 'Treasury',
        'description': 'Short-term government borrowing',
    },
    {
        'name': '364-Day T-Bill',
        'rate': 6.85,
        'change': -0.05,
        'type': 'Treasury',
        'description': 'Medium-term government borrowing',
    },
    {
        'name': 'Bank FD 1Y (SBI)',
        'rate': 6.80,
        'change': 0.00,
        'type': 'Deposit',
        'description': '1 year fixed deposit rate',
    },
]


def get_liquidity_data():
    """Get money market / liquidity rates"""
    return LIQUIDITY_DATA


# ─── Fallback ETF data ──────────────────────────────────────

def _fallback_etfs():
    return [
        {'name': 'Nippon India Nifty BeES', 'symbol': 'NIFTYBEES', 'category': 'Index', 'price': 234.50, 'change': 1.85, 'change_pct': 0.80},
        {'name': 'Nippon India Bank BeES', 'symbol': 'BANKBEES', 'category': 'Banking', 'price': 468.20, 'change': 5.10, 'change_pct': 1.10},
        {'name': 'Nippon India Gold BeES', 'symbol': 'GOLDBEES', 'category': 'Gold', 'price': 54.30, 'change': 0.16, 'change_pct': 0.30},
        {'name': 'SBI ETF Nifty 50', 'symbol': 'SETFNIF50', 'category': 'Index', 'price': 245.80, 'change': 2.10, 'change_pct': 0.86},
        {'name': 'Nippon India Silver ETF', 'symbol': 'SILVERBEES', 'category': 'Silver', 'price': 72.10, 'change': -0.14, 'change_pct': -0.19},
    ]
