"""
Focused JSON API views for market data.
Each endpoint has one job, one payload contract, one caching policy.
"""
from django.http import JsonResponse
from django.views import View
from apps.market_data.services import get_ticker_data, get_gainers, get_losers, get_most_active


class TickerAPIView(View):
    """
    GET /market/api/ticker/
    Returns compact ticker strip data from DB-backed service.
    """

    def get(self, request):
        data = get_ticker_data()
        response = JsonResponse(data, safe=False)
        response['Cache-Control'] = 'public, max-age=60, stale-while-revalidate=120'
        return response


class MoversAPIView(View):
    """
    GET /market/api/movers/?kind=gainers&limit=10
    Returns top gainers OR losers based on `kind` param.
    """

    def get(self, request):
        kind = request.GET.get('kind', 'gainers')
        try:
            limit = max(1, min(int(request.GET.get('limit', 10)), 50))
        except (TypeError, ValueError):
            limit = 10

        if kind == 'losers':
            data = get_losers(limit=limit)
        else:
            data = get_gainers(limit=limit)

        response = JsonResponse(data, safe=False)
        response['Cache-Control'] = 'public, max-age=60, stale-while-revalidate=120'
        return response


class MostActiveAPIView(View):
    """
    GET /market/api/active/?limit=10
    Returns most active stocks by volume.
    """

    def get(self, request):
        try:
            limit = max(1, min(int(request.GET.get('limit', 10)), 50))
        except (TypeError, ValueError):
            limit = 10

        data = get_most_active(limit=limit)
        response = JsonResponse(data, safe=False)
        response['Cache-Control'] = 'public, max-age=60, stale-while-revalidate=120'
        return response
