"""
Live market ticker API — uses yfinance (free, no API key needed).
Returns NIFTY 50, SENSEX, BANKNIFTY, NIFTY IT, NIFTY BANK with live prices.
Cached for 60 seconds to avoid hammering Yahoo Finance.
"""
import json
from django.http import JsonResponse
from django.views import View
from django.core.cache import cache


TICKER_SYMBOLS = [
    {"label": "NIFTY 50",    "symbol": "^NSEI"},
    {"label": "SENSEX",      "symbol": "^BSESN"},
    {"label": "BANKNIFTY",   "symbol": "^NSEBANK"},
    {"label": "NIFTY IT",    "symbol": "^CNXIT"},
    {"label": "MIDCAP 100",  "symbol": "^NSEMDCP50"},
    {"label": "USD/INR",     "symbol": "USDINR=X"},
    {"label": "GOLD",        "symbol": "GC=F"},
]

CACHE_KEY = "live_ticker_data"
CACHE_TTL = 60  # seconds


class LiveTickerView(View):
    """
    GET /api/core/live-ticker/
    Returns JSON list of live market data for the ticker bar.
    """

    def get(self, request):
        data = cache.get(CACHE_KEY)
        if data:
            return JsonResponse({"results": data, "cached": True})

        data = self._fetch_live()
        cache.set(CACHE_KEY, data, CACHE_TTL)
        return JsonResponse({"results": data, "cached": False})

    def _fetch_live(self):
        try:
            import yfinance as yf
        except ImportError:
            return self._fallback()

        results = []
        symbols = [t["symbol"] for t in TICKER_SYMBOLS]

        try:
            tickers = yf.Tickers(" ".join(symbols))
            for item in TICKER_SYMBOLS:
                sym = item["symbol"]
                try:
                    info = tickers.tickers[sym].fast_info
                    price = info.last_price
                    prev  = info.previous_close
                    if price is None or prev is None:
                        # fallback: try history
                        hist = tickers.tickers[sym].history(period="2d")
                        if not hist.empty:
                            price = float(hist["Close"].iloc[-1])
                            prev  = float(hist["Close"].iloc[-2]) if len(hist) > 1 else price
                        else:
                            continue

                    change     = price - prev
                    change_pct = (change / prev) * 100 if prev else 0

                    # Format price: currency pairs show 4 decimals, indices/commodities 2
                    if "=X" in sym:
                        price_str = f"₹{price:.2f}" if "INR" in sym else f"${price:.4f}"
                    elif "GC=F" in sym or "CL=F" in sym:
                        price_str = f"${price:.2f}"
                    else:
                        price_str = f"₹{price:,.2f}"

                    results.append({
                        "label":      item["label"],
                        "price":      price_str,
                        "change":     f"{'+' if change >= 0 else ''}{change:,.2f}",
                        "change_pct": f"{'+' if change_pct >= 0 else ''}{change_pct:.2f}%",
                        "direction":  "up" if change >= 0 else "down",
                    })
                except Exception:
                    continue
        except Exception:
            return self._fallback()

        return results if results else self._fallback()

    def _fallback(self):
        """Static fallback if yfinance fails (never shows stale hardcoded data forever)."""
        return [
            {"label": "NIFTY 50",  "price": "—",  "change": "—", "change_pct": "—", "direction": "neutral"},
            {"label": "SENSEX",    "price": "—",  "change": "—", "change_pct": "—", "direction": "neutral"},
            {"label": "BANKNIFTY", "price": "—",  "change": "—", "change_pct": "—", "direction": "neutral"},
        ]
