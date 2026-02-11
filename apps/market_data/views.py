"""
Market data views for displaying indices and stock prices
"""
from django.shortcuts import render
from django.http import JsonResponse
from apps.market_data.models import MarketIndex, StockPrice, PopularStock
from apps.market_data.services import (
    get_market_summary, 
    get_popular_stocks_data,
    fetch_stock_price,
    update_index_prices,
    update_popular_stocks
)


def market_indices_view(request):
    """Display market indices"""
    indices = MarketIndex.objects.all()
    
    context = {
        'indices': indices,
    }
    
    return render(request, 'market_data/indices.html', context)


def popular_stocks_view(request):
    """Display popular stocks"""
    stocks = StockPrice.objects.filter(
        symbol__in=PopularStock.objects.filter(is_active=True).values_list('symbol', flat=True)
    ).order_by('symbol')
    
    context = {
        'stocks': stocks,
    }
    
    return render(request, 'market_data/popular_stocks.html', context)


def market_data_api(request):
    """API endpoint for real-time market data"""
    data_type = request.GET.get('type', 'indices')
    
    if data_type == 'indices':
        data = get_market_summary()
    elif data_type == 'stocks':
        data = get_popular_stocks_data()
    else:
        data = {'error': 'Invalid data type'}
    
    return JsonResponse(data, safe=False)


def update_market_data_view(request):
    """Manually trigger market data update (admin only)"""
    if not request.user.is_authenticated or request.user.role != 'ADMIN':
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    indices_updated = update_index_prices()
    stocks_updated = update_popular_stocks()
    
    return JsonResponse({
        'status': 'success',
        'indices_updated': indices_updated,
        'stocks_updated': stocks_updated
    })
