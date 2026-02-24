"""
Views for dashboard and home page — powered by live market data services
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg, Q
from django.utils import timezone

from apps.research_calls.models import ResearchCall
from apps.brokers.models import Broker


def landing_page_view(request):
    """Redirect to dashboard (authenticated) or login (unauthenticated)"""
    if request.user.is_authenticated:
        return redirect('dashboard:dashboard')
    return redirect('authentication:login')


@login_required
def dashboard_home_view(request):
    """Dashboard home — redirect based on role"""
    # If user hits /app/ directly, ensure they are logged in (handled by decorator)
    
    if request.user.role == 'CUSTOMER':
        from apps.portfolios.models import Portfolio, PortfolioItem
        from services.recommendation_service import get_user_recommendations, get_market_sentiment

        today = timezone.now().date()
        today_calls = ResearchCall.objects.filter(
            status='ACTIVE',
            published_at__date=today
        ).select_related('broker', 'created_by').order_by('-published_at')

        try:
            portfolio = Portfolio.objects.get(user=request.user)
            active_items = PortfolioItem.objects.filter(
                portfolio=portfolio, status='ACTIVE'
            ).select_related('research_call')
        except Portfolio.DoesNotExist:
            portfolio = None
            active_items = []

        top_brokers = Broker.objects.annotate(
            total_calls=Count('research_calls'),
        ).filter(total_calls__gt=0).order_by('-overall_accuracy')[:4]

        # Recommendations
        recommendations = get_user_recommendations(request.user, limit=6)
        sentiment = get_market_sentiment()

        context = {
            'today_calls': today_calls,
            'portfolio': portfolio,
            'active_items': active_items,
            'top_brokers': top_brokers,
            'recommendations': recommendations,
            'sentiment': sentiment,
        }
        return render(request, 'dashboard/customer_dashboard.html', context)
    elif request.user.role == 'ADMIN':
        # Redirect to admin panel which uses AdminDashboardView with full stats context
        from django.shortcuts import redirect
        return redirect('admin_panel:dashboard')
    else:
        return render(request, 'dashboard/home.html')



def markets_view(request):
    """Markets overview page with live data"""
    from apps.market_data.models import MarketIndex, StockPrice
    from services.market_hero_service import get_today_top10_gainers, get_today_top10_losers

    indices = MarketIndex.objects.all()
    top_gainers = get_today_top10_gainers()
    top_losers = get_today_top10_losers()

    context = {
        'indices': indices,
        'top_gainers': top_gainers,
        'top_losers': top_losers,
    }
    return render(request, 'markets/overview.html', context)


def pro_trades_view(request):
    """PRO Trades page"""
    context = {
        'is_pro': request.user.is_authenticated and hasattr(request.user, 'subscription') and request.user.subscription,
    }
    return render(request, 'pro/pro_trades.html', context)


def pro_baskets_view(request):
    """PRO Baskets page"""
    context = {
        'is_pro': request.user.is_authenticated and hasattr(request.user, 'subscription') and request.user.subscription,
    }
    return render(request, 'pro/baskets.html', context)


def ipo_view(request):
    """IPO section with live data"""
    from services.ipo_service import get_upcoming_ipos, get_recently_listed, get_ipo_stats

    context = {
        'upcoming_ipos': get_upcoming_ipos(),
        'recently_listed': get_recently_listed(),
        'ipo_stats': get_ipo_stats(),
    }
    return render(request, 'ipo/upcoming.html', context)


def explore_view(request):
    """Explore page"""
    return render(request, 'explore.html')


# ─── New Market Section Views ────────────────────────────────

def sip_view(request):
    """SIP section"""
    from services.sip_mf_etf_service import get_top_sip_funds
    context = {'sip_funds': get_top_sip_funds()}
    return render(request, 'markets/sip.html', context)


def mutual_funds_view(request):
    """Mutual Funds section"""
    from services.sip_mf_etf_service import get_top_mutual_funds
    context = {'mutual_funds': get_top_mutual_funds()}
    return render(request, 'markets/mutual_funds.html', context)


def etf_view(request):
    """ETF section"""
    from services.sip_mf_etf_service import get_top_etfs
    context = {'etfs': get_top_etfs()}
    return render(request, 'markets/etf.html', context)


def bonds_view(request):
    """Bonds section"""
    from services.sip_mf_etf_service import get_bonds_data
    context = {'bonds': get_bonds_data()}
    return render(request, 'markets/bonds.html', context)


def liquidity_view(request):
    """Liquidity / Money Market section"""
    from services.sip_mf_etf_service import get_liquidity_data
    context = {'liquidity': get_liquidity_data()}
    return render(request, 'markets/liquidity.html', context)


def commodity_view(request):
    """Commodity section"""
    from services.commodity_service import get_commodity_prices, get_indian_commodity_prices
    context = {
        'global_commodities': get_commodity_prices(),
        'indian_commodities': get_indian_commodity_prices(),
    }
    return render(request, 'markets/commodity.html', context)


def trades_dashboard_view(request):
    """Unified trades dashboard with tabs"""
    tab = request.GET.get('tab', 'all')
    calls = ResearchCall.objects.filter(status='ACTIVE').select_related('broker')

    if tab == 'commodity':
        calls = calls.filter(instrument_type='COMMODITY')
    elif tab == 'futures':
        calls = calls.filter(instrument_type='FUTURES')
    elif tab == 'options':
        calls = calls.filter(instrument_type='OPTIONS')
    elif tab == 'short':
        calls = calls.filter(call_type='SHORT_TERM')
    elif tab == 'medium':
        calls = calls.filter(call_type='MEDIUM_TERM')
    elif tab == 'long':
        calls = calls.filter(call_type='LONG_TERM')
    elif tab == 'intraday':
        calls = calls.filter(call_type='INTRADAY')

    calls = calls.order_by('-published_at')
    brokers = Broker.objects.filter(is_active=True)

    context = {
        'calls': calls,
        'brokers': brokers,
        'active_tab': tab,
    }
    return render(request, 'trades/dashboard.html', context)


def gainers_losers_view(request):
    """Today's Top 10 Gainers & Losers"""
    from services.market_hero_service import get_today_top10_gainers, get_today_top10_losers
    try:
        top_gainers = get_today_top10_gainers()
        top_losers = get_today_top10_losers()
    except Exception as e:
        import logging
        logging.error(f"Error in gainers_losers_view: {e}")
        top_gainers = []
        top_losers = []

    context = {
        'top_gainers': top_gainers,
        'top_losers': top_losers,
    }
    return render(request, 'markets/gainers_losers.html', context)


def recently_listed_view(request):
    """Recently Listed IPOs / Stocks"""
    from services.ipo_service import get_recently_listed
    try:
        recently_listed = get_recently_listed()
    except Exception as e:
        import logging
        logging.error(f"Error in recently_listed_view: {e}")
        recently_listed = []

    context = {
        'recently_listed': recently_listed,
    }
    return render(request, 'markets/recently_listed.html', context)


def top_brokers_view(request):
    """Top Performing Brokers by accuracy"""
    top_brokers = Broker.objects.annotate(
        total_calls=Count('research_calls'),
    ).filter(total_calls__gt=0).order_by('-overall_accuracy')[:20]
    context = {
        'top_brokers': top_brokers,
    }
    return render(request, 'markets/top_brokers.html', context)
