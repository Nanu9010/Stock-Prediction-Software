"""
Live market ticker API — DB-first, no yfinance in request path.
Returns NIFTY 50, SENSEX, BANKNIFTY, NIFTY IT, MIDCAP with live prices.
Data is populated by Celery background task; this view only reads from DB/cache.
"""
from django.http import JsonResponse
from django.views import View
from django.core.cache import cache


CACHE_KEY = "live_ticker_data"
CACHE_TTL = 60  # seconds

TICKER_DISPLAY = {
    'NIFTY50':    'NIFTY 50',
    'SENSEX':     'SENSEX',
    'BANKNIFTY':  'BANKNIFTY',
    'FINNIFTY':   'FIN NIFTY',
    'MIDCPNIFTY': 'MIDCAP 100',
}


class LiveTickerView(View):
    """
    GET /api/core/live-ticker/
    Returns JSON list of live market data for the ticker bar.
    Reads from DB — never calls yfinance during a user request.
    """

    def get(self, request):
        data = cache.get(CACHE_KEY)
        if data:
            return JsonResponse({"results": data, "cached": True})

        data = self._from_db()
        if data:
            cache.set(CACHE_KEY, data, CACHE_TTL)
        return JsonResponse({"results": data or self._fallback(), "cached": False})

    def _from_db(self):
        """Read indices from MarketIndex table (populated by Celery task)."""
        from apps.market_data.models import MarketIndex

        priority = list(TICKER_DISPLAY.keys())
        db_indices = {
            idx.symbol: idx
            for idx in MarketIndex.objects.filter(symbol__in=priority)
        }

        if not db_indices:
            return None  # DB not yet populated — use fallback

        results = []
        for sym in priority:
            if sym not in db_indices:
                continue
            idx = db_indices[sym]
            price = float(idx.current_price)
            change = float(idx.change)
            prev = float(idx.previous_close) if idx.previous_close else price
            change_pct = (change / prev * 100) if prev else 0

            results.append({
                "label":      TICKER_DISPLAY.get(sym, sym),
                "price":      f"₹{price:,.2f}",
                "change":     f"{'+' if change >= 0 else ''}{change:,.2f}",
                "change_pct": f"{'+' if change_pct >= 0 else ''}{change_pct:.2f}%",
                "direction":  "up" if change >= 0 else "down",
            })

        return results if results else None

    def _fallback(self):
        """Static fallback if DB has no data yet."""
        return [
            {"label": "NIFTY 50",  "price": "—",  "change": "—", "change_pct": "—", "direction": "neutral"},
            {"label": "SENSEX",    "price": "—",  "change": "—", "change_pct": "—", "direction": "neutral"},
            {"label": "BANKNIFTY", "price": "—",  "change": "—", "change_pct": "—", "direction": "neutral"},
        ]
