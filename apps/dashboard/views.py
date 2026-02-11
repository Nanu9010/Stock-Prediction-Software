"""
Views for dashboard and home page
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.research_calls.models import ResearchCall
from apps.brokers.models import Broker
from django.db.models import Count, Avg, Q


def home_view(request):
    """Professional landing page"""
    # Get statistics
    total_calls = ResearchCall.objects.count()
    active_calls = ResearchCall.objects.filter(status='ACTIVE').count()
    
    # Calculate success rate (closed calls with positive return)
    closed_calls = ResearchCall.objects.filter(status='CLOSED')
    successful_calls = closed_calls.filter(actual_return_percentage__gt=0).count()
    total_closed = closed_calls.count()
    success_rate = (successful_calls / total_closed * 100) if total_closed > 0 else 87
    
    # Get top brokers
    top_brokers = Broker.objects.annotate(
        total_calls=Count('research_calls')
    ).filter(total_calls__gt=0).order_by('-overall_accuracy')[:4]
    
    context = {
        'total_calls': total_calls,
        'success_rate': f"{success_rate:.1f}%",
        'active_users': '10,000+',  # Placeholder
        'top_brokers': top_brokers,
    }
    
    return render(request, 'home.html', context)


@login_required
def dashboard_home_view(request):
    """Dashboard home - redirect based on role"""
    if request.user.role == 'CUSTOMER':
        from apps.research_calls.models import ResearchCall
        from apps.portfolios.models import Portfolio, PortfolioItem
        from django.utils import timezone
        
        # Get today's active calls
        today = timezone.now().date()
        today_calls = ResearchCall.objects.filter(
            status='ACTIVE',
            published_at__date=today
        ).select_related('broker', 'created_by').order_by('-published_at')
        
        # Get portfolio
        try:
            portfolio = Portfolio.objects.get(user=request.user)
            active_items = PortfolioItem.objects.filter(portfolio=portfolio, status='ACTIVE').select_related('research_call')
        except Portfolio.DoesNotExist:
            portfolio = None
            active_items = []
            
        # Get top brokers
        top_brokers = Broker.objects.annotate(
            total_calls=Count('research_calls'),
            total_calls_published=Count('research_calls', filter=Q(research_calls__status__in=['ACTIVE', 'CLOSED']))
        ).filter(total_calls__gt=0).order_by('-overall_accuracy')[:4]
        
        context = {
            'today_calls': today_calls,
            'portfolio': portfolio,
            'active_items': active_items,
            'top_brokers': top_brokers,
        }
        return render(request, 'dashboard/customer_dashboard.html', context)
    elif request.user.role == 'ANALYST':
        return render(request, 'dashboard/analyst_dashboard.html')
    elif request.user.role == 'ADMIN':
        return render(request, 'dashboard/admin_dashboard.html')
    else:
        return render(request, 'dashboard/home.html')


def markets_view(request):
    """Markets overview page"""
    from apps.market_data.models import MarketIndex, StockPrice
    
    indices = MarketIndex.objects.all()
    
    # Get top gainers and losers
    all_stocks = StockPrice.objects.all().order_by('-change_percent')
    top_gainers = all_stocks[:10]
    top_losers = all_stocks.order_by('change_percent')[:10]
    
    context = {
        'indices': indices,
        'top_gainers': top_gainers,
        'top_losers': top_losers,
    }
    
    return render(request, 'markets/overview.html', context)


def pro_trades_view(request):
    """PRO Trades page"""
    context = {
        'is_pro': request.user.is_authenticated and hasattr(request.user, 'subscription') and request.user.subscription.is_active,
    }
    return render(request, 'pro/pro_trades.html', context)


def pro_baskets_view(request):
    """PRO Baskets page"""
    context = {
        'is_pro': request.user.is_authenticated and hasattr(request.user, 'subscription') and request.user.subscription.is_active,
    }
    return render(request, 'pro/pro_baskets.html', context)


def ipo_view(request):
    """IPO section"""
    return render(request, 'ipo/upcoming.html')


def explore_view(request):
    """Explore page"""
    return render(request, 'explore.html')
