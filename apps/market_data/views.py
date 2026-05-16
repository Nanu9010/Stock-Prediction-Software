"""
Market data views — indices, gainers/losers, ETFs, commodities, MF NAVs
"""
from django.shortcuts import render
from django.http import JsonResponse
from apps.market_data.models import MarketIndex, StockPrice, PopularStock
from apps.market_data.services import (
    get_market_summary,
    get_live_indices,
    get_popular_stocks_data,
    fetch_stock_price,
    update_index_prices,
    update_popular_stocks,
    get_ticker_data,
    get_gainers,
    get_losers,
    get_most_active,
)


def market_indices_view(request):
    """Display market indices"""
    indices = get_live_indices()
    return render(request, 'market_data/indices.html', {'indices': indices})


def popular_stocks_view(request):
    """Display popular stocks"""
    stocks = StockPrice.objects.filter(
        symbol__in=PopularStock.objects.filter(is_active=True).values_list('symbol', flat=True)
    ).order_by('symbol')
    return render(request, 'market_data/popular_stocks.html', {'stocks': stocks})


def market_data_api(request):
    """
    Unified JSON API for all market data types.
    type param options: indices | ticker | gainers | losers | active | stocks | etfs | commodities | mf_navs
    """
    data_type = request.GET.get('type', 'indices')
    try:
        limit = max(1, min(int(request.GET.get('limit', 20)), 50))
    except (TypeError, ValueError):
        limit = 20

    if data_type == 'ticker':
        data = get_ticker_data()

    elif data_type == 'indices':
        data = get_live_indices()

    elif data_type == 'gainers':
        data = get_gainers(limit=limit)

    elif data_type == 'losers':
        data = get_losers(limit=limit)

    elif data_type == 'active':
        data = get_most_active(limit=limit)

    elif data_type == 'stocks':
        data = get_popular_stocks_data()

    elif data_type == 'etfs':
        from services.sip_mf_etf_service import get_top_etfs
        data = get_top_etfs()

    elif data_type == 'commodities':
        from services.commodity_service import get_commodity_prices, get_indian_commodity_prices
        data = {
            'global': get_commodity_prices(),
            'indian': get_indian_commodity_prices(),
        }

    elif data_type == 'mf_navs':
        from services.sip_mf_etf_service import get_top_mutual_funds
        data = get_top_mutual_funds()

    else:
        data = {'error': f'Unknown type: {data_type}'}

    response = JsonResponse(data, safe=False)
    if data_type in {'ticker', 'indices', 'gainers', 'losers', 'active', 'stocks'}:
        response['Cache-Control'] = 'public, max-age=60, stale-while-revalidate=120'
    return response


def update_market_data_view(request):
    """Manually trigger market data update (admin only)"""
    if not request.user.is_authenticated or request.user.role != 'ADMIN':
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    indices_updated = update_index_prices()
    stocks_updated  = update_popular_stocks()

    return JsonResponse({
        'status': 'success',
        'indices_updated': indices_updated,
        'stocks_updated': stocks_updated,
    })
