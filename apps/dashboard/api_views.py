"""
Lightweight JSON API views for dashboard widgets.
Designed for low-latency, no external API calls in request path.
"""
import logging
from django.http import JsonResponse
from django.views import View
from django.utils import timezone
from django.core.cache import cache

logger = logging.getLogger(__name__)


class CustomerDashboardSummaryView(View):
    """
    GET /api/dashboard/customer-summary/
    Returns counts-only KPI data for the customer dashboard.
    No external API calls. Uses .count() instead of loading rows.
    Cached per-user for 60s.
    """

    def get(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Unauthorized'}, status=401)

        user = request.user
        cache_key = f'dashboard_summary:{user.pk}'
        cached = cache.get(cache_key)
        if cached:
            return JsonResponse(cached)

        data = self._build_summary(user)
        cache.set(cache_key, data, 60)
        return JsonResponse(data)

    def _build_summary(self, user):
        from apps.portfolios.models import Portfolio, PortfolioItem
        from apps.research_calls.models import ResearchCall
        from apps.notifications.models import Notification

        # Active portfolio positions (count only)
        active_positions = 0
        try:
            portfolio = Portfolio.objects.get(user=user)
            active_positions = PortfolioItem.objects.filter(
                portfolio=portfolio, status='ACTIVE'
            ).count()
        except Portfolio.DoesNotExist:
            pass

        # Today's active calls (count only, range filter)
        now = timezone.localtime()
        day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timezone.timedelta(days=1)
        today_calls_count = ResearchCall.objects.filter(
            status='ACTIVE',
            published_at__gte=day_start,
            published_at__lt=day_end,
        ).count()

        # Unread notifications (count only)
        unread_count = Notification.objects.filter(
            user=user, is_read=False
        ).count()

        # Sentiment (lightweight, counts only)
        from services.recommendation_service import get_market_sentiment
        sentiment = get_market_sentiment()

        return {
            'active_positions': active_positions,
            'today_calls_count': today_calls_count,
            'unread_notifications': unread_count,
            'sentiment': sentiment,
        }


class MarketTickerLiteView(View):
    """
    GET /api/dashboard/ticker-lite/
    Returns indices from DB only (no yfinance).
    Cached for 180s. If DB is empty, returns empty list.
    Background Celery task is responsible for populating the data.
    """

    def get(self, request):
        cache_key = 'ticker_lite_v1'
        cached = cache.get(cache_key)
        if cached is not None:
            response = JsonResponse(cached, safe=False)
            response['Cache-Control'] = 'public, max-age=60, stale-while-revalidate=120'
            return response

        data = self._from_db()
        cache.set(cache_key, data, 180)
        response = JsonResponse(data, safe=False)
        response['Cache-Control'] = 'public, max-age=60, stale-while-revalidate=120'
        return response

    def _from_db(self):
        from apps.market_data.models import MarketIndex

        priority = ['NIFTY50', 'SENSEX', 'BANKNIFTY', 'FINNIFTY', 'MIDCPNIFTY']
        display_names = {
            'NIFTY50': 'NIFTY 50',
            'SENSEX': 'SENSEX',
            'BANKNIFTY': 'BANK NIFTY',
            'FINNIFTY': 'FIN NIFTY',
            'MIDCPNIFTY': 'MIDCAP NIFTY',
        }

        db_indices = {
            idx.symbol: idx
            for idx in MarketIndex.objects.filter(symbol__in=priority)
        }

        results = []
        for sym in priority:
            if sym in db_indices:
                idx = db_indices[sym]
                results.append({
                    'symbol': sym,
                    'name': display_names.get(sym, sym),
                    'price': float(idx.current_price),
                    'change': float(idx.change),
                    'change_pct': float(idx.change_percent),
                    'is_positive': float(idx.change_percent) >= 0,
                })

        return results
