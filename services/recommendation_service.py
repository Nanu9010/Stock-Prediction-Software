"""
Recommendation Service — personalized stock call recommendations
Based on broker accuracy, call performance, and user activity
"""
import logging
from django.db.models import Count, Avg, Q, F
from django.utils import timezone

logger = logging.getLogger(__name__)


def get_user_recommendations(user, limit=6):
    """
    Get personalized recommendations for a user based on:
    1. Top-performing broker calls
    2. Calls similar to user's watchlist/portfolio
    3. Trending calls (most added to portfolios)
    """
    from apps.research_calls.models import ResearchCall
    from apps.brokers.models import Broker
    from apps.watchlists.models import WatchlistItem
    from apps.portfolios.models import PortfolioItem

    recommendations = []

    # 1. Get user's preferred sectors/symbols from watchlist + portfolio
    user_symbols = set()
    user_sectors = set()

    try:
        watchlist_symbols = WatchlistItem.objects.filter(
            watchlist__user=user
        ).values_list('research_call__symbol', flat=True)
        user_symbols.update(watchlist_symbols)

        portfolio_symbols = PortfolioItem.objects.filter(
            portfolio__user=user, status='ACTIVE'
        ).values_list('research_call__symbol', flat=True)
        user_symbols.update(portfolio_symbols)

        # Get sectors from user's symbols
        if user_symbols:
            sectors = ResearchCall.objects.filter(
                symbol__in=user_symbols
            ).values_list('sector', flat=True).distinct()
            user_sectors.update(s for s in sectors if s)
    except Exception:
        pass

    # 2. Find active calls from top-performing brokers
    top_broker_calls = ResearchCall.objects.filter(
        status='ACTIVE',
        broker__is_active=True,
        broker__overall_accuracy__gte=60,
    ).select_related('broker').order_by(
        '-broker__overall_accuracy', '-published_at'
    )[:limit]

    for call in top_broker_calls:
        recommendations.append({
            'call': call,
            'reason': f"From {call.broker.name} ({call.broker.overall_accuracy}% accuracy)",
            'type': 'top_broker',
            'score': float(call.broker.overall_accuracy or 0),
        })

    # 3. Calls in user's preferred sectors (if any)
    if user_sectors:
        sector_calls = ResearchCall.objects.filter(
            status='ACTIVE',
            sector__in=user_sectors,
        ).exclude(
            id__in=[r['call'].id for r in recommendations]
        ).select_related('broker').order_by('-published_at')[:3]

        for call in sector_calls:
            recommendations.append({
                'call': call,
                'reason': f"In your preferred sector: {call.sector}",
                'type': 'sector_match',
                'score': 70,
            })

    # 4. Trending calls (most added to portfolios recently)
    trending_ids = PortfolioItem.objects.filter(
        created_at__gte=timezone.now() - timezone.timedelta(days=7)
    ).values('research_call').annotate(
        count=Count('id')
    ).order_by('-count')[:5]

    trending_call_ids = [t['research_call'] for t in trending_ids]
    if trending_call_ids:
        trending_calls = ResearchCall.objects.filter(
            id__in=trending_call_ids,
            status='ACTIVE'
        ).exclude(
            id__in=[r['call'].id for r in recommendations]
        ).select_related('broker')

        for call in trending_calls:
            recommendations.append({
                'call': call,
                'reason': "Trending — popular among investors",
                'type': 'trending',
                'score': 65,
            })

    # Sort by score and limit
    recommendations.sort(key=lambda x: x['score'], reverse=True)
    return recommendations[:limit]


def get_top_performing_brokers(limit=5):
    """Get brokers ranked by accuracy and performance"""
    from apps.brokers.models import Broker

    brokers = Broker.objects.filter(
        is_active=True,
        total_calls_published__gt=0,
    ).order_by('-overall_accuracy')[:limit]

    return [
        {
            'broker': broker,
            'accuracy': float(broker.overall_accuracy or 0),
            'total_calls': broker.total_calls_published,
            'avg_return': float(broker.avg_return_percentage or 0),
        }
        for broker in brokers
    ]


def get_trending_calls(limit=8):
    """Get most popular active calls based on portfolio/watchlist additions"""
    from apps.research_calls.models import ResearchCall

    trending = ResearchCall.objects.filter(
        status='ACTIVE'
    ).annotate(
        portfolio_count=Count('portfolio_items'),
    ).order_by('-portfolio_count', '-published_at').select_related('broker')[:limit]

    return trending


def get_market_sentiment():
    """Calculate overall market sentiment from active calls"""
    from apps.research_calls.models import ResearchCall

    active_calls = ResearchCall.objects.filter(status='ACTIVE')
    total = active_calls.count()

    if total == 0:
        return {'sentiment': 'NEUTRAL', 'buy_pct': 50, 'sell_pct': 50, 'total': 0}

    buy_count = active_calls.filter(action='BUY').count()
    sell_count = active_calls.filter(action='SELL').count()

    buy_pct = round((buy_count / total) * 100, 1)
    sell_pct = round((sell_count / total) * 100, 1)

    if buy_pct > 65:
        sentiment = 'BULLISH'
    elif sell_pct > 65:
        sentiment = 'BEARISH'
    else:
        sentiment = 'NEUTRAL'

    return {
        'sentiment': sentiment,
        'buy_pct': buy_pct,
        'sell_pct': sell_pct,
        'total': total,
    }
