"""
Views for dashboard and home page — powered by live market data services
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg, Q
from django.utils import timezone

from apps.research_calls.models import ResearchCall
from apps.brokers.models import Broker


def home_view(request):
    """Market Hero — professional landing page with live data"""
    from services.market_hero_service import (
        get_today_top10_gainers, get_today_top10_losers,
        get_weekly_top_gainers, get_weekly_top_losers,
        get_market_indices,
    )
    from services.commodity_service import get_indian_commodity_prices
    from services.ipo_service import get_upcoming_ipos, get_recently_listed, get_ipo_stats
    from services.sip_mf_etf_service import (
        get_top_etfs, get_top_mutual_funds, get_top_sip_funds,
        get_bonds_data, get_liquidity_data,
    )
    from services.recommendation_service import get_market_sentiment

    # Statistics
    total_calls = ResearchCall.objects.count()
    active_calls = ResearchCall.objects.filter(status='ACTIVE').count()
    closed_calls = ResearchCall.objects.filter(status='CLOSED')
    successful_calls = closed_calls.filter(actual_return_percentage__gt=0).count()
    total_closed = closed_calls.count()
    success_rate = (successful_calls / total_closed * 100) if total_closed > 0 else 87

    # Top brokers
    top_brokers = Broker.objects.annotate(
        total_calls=Count('research_calls')
    ).filter(total_calls__gt=0).order_by('-overall_accuracy')[:4]

    context = {
        # Stats
        'total_calls': total_calls,
        'active_calls': active_calls,
        'success_rate': f"{success_rate:.1f}",
        'top_brokers': top_brokers,
        'now': timezone.now(),

        # Market Hero Sections
        'market_indices': get_market_indices(),
        'today_gainers': get_today_top10_gainers(),
        'today_losers': get_today_top10_losers(),
        'weekly_gainers': get_weekly_top_gainers(),
        'weekly_losers': get_weekly_top_losers(),

        # Widgets
        'commodities': get_indian_commodity_prices(),
        'upcoming_ipos': get_upcoming_ipos(),
        'recently_listed': get_recently_listed(),
        'ipo_stats': get_ipo_stats(),
        'etfs': get_top_etfs(),
        'mutual_funds': get_top_mutual_funds(),
        'sip_funds': get_top_sip_funds(),
        'bonds': get_bonds_data(),
        'liquidity': get_liquidity_data(),
        'sentiment': get_market_sentiment(),
    }

    return render(request, 'home.html', context)


@login_required
def dashboard_home_view(request):
    """Dashboard home — redirect based on role"""
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
        return render(request, 'dashboard/admin_dashboard.html')
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
