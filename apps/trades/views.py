"""
Views for different trade types and categories
"""
from django.shortcuts import render
from django.db.models import Q, Count, Avg
from apps.research_calls.models import ResearchCall
from apps.brokers.models import Broker


def short_term_trades_view(request):
    """Short term trades (1-7 days)"""
    calls = ResearchCall.objects.filter(
        status='ACTIVE',
        call_type='SHORT_TERM'
    ).select_related('broker').order_by('-published_at')
    
    # Apply filters
    broker_id = request.GET.get('broker')
    action = request.GET.get('action')
    search = request.GET.get('search')
    
    if broker_id:
        calls = calls.filter(broker_id=broker_id)
    if action:
        calls = calls.filter(action=action.upper())
    if search:
        calls = calls.filter(
            Q(symbol__icontains=search) | Q(broker__name__icontains=search)
        )
    
    brokers = Broker.objects.all()
    
    context = {
        'calls': calls,
        'brokers': brokers,
        'trade_type': 'Short Term',
        'trade_description': 'Quick trades with 1-7 days holding period',
        'selected_broker': broker_id,
        'selected_action': action,
        'search_query': search,
    }
    
    return render(request, 'trades/short_term.html', context)


def medium_term_trades_view(request):
    """Medium term trades (1-4 weeks)"""
    calls = ResearchCall.objects.filter(
        status='ACTIVE',
        call_type='MEDIUM_TERM'
    ).select_related('broker').order_by('-published_at')
    
    # Apply filters
    broker_id = request.GET.get('broker')
    action = request.GET.get('action')
    search = request.GET.get('search')
    
    if broker_id:
        calls = calls.filter(broker_id=broker_id)
    if action:
        calls = calls.filter(action=action.upper())
    if search:
        calls = calls.filter(
            Q(symbol__icontains=search) | Q(broker__name__icontains=search)
        )
    
    brokers = Broker.objects.all()
    
    context = {
        'calls': calls,
        'brokers': brokers,
        'trade_type': 'Medium Term',
        'trade_description': 'Swing trades with 1-4 weeks holding period',
        'selected_broker': broker_id,
        'selected_action': action,
        'search_query': search,
    }
    
    return render(request, 'trades/medium_term.html', context)


def long_term_trades_view(request):
    """Long term trades (1+ months)"""
    calls = ResearchCall.objects.filter(
        status='ACTIVE',
        call_type='LONG_TERM'
    ).select_related('broker').order_by('-published_at')
    
    # Apply filters
    broker_id = request.GET.get('broker')
    action = request.GET.get('action')
    search = request.GET.get('search')
    
    if broker_id:
        calls = calls.filter(broker_id=broker_id)
    if action:
        calls = calls.filter(action=action.upper())
    if search:
        calls = calls.filter(
            Q(symbol__icontains=search) | Q(broker__name__icontains=search)
        )
    
    brokers = Broker.objects.all()
    
    context = {
        'calls': calls,
        'brokers': brokers,
        'trade_type': 'Long Term',
        'trade_description': 'Investment ideas with 1+ months holding period',
        'selected_broker': broker_id,
        'selected_action': action,
        'search_query': search,
    }
    
    return render(request, 'trades/long_term.html', context)


def futures_trades_view(request):
    """Futures & derivatives trades"""
    calls = ResearchCall.objects.filter(
        status='ACTIVE'
    ).filter(
        Q(symbol__icontains='FUT') | Q(notes__icontains='futures')
    ).select_related('broker').order_by('-published_at')
    
    # Apply filters
    broker_id = request.GET.get('broker')
    action = request.GET.get('action')
    search = request.GET.get('search')
    
    if broker_id:
        calls = calls.filter(broker_id=broker_id)
    if action:
        calls = calls.filter(action=action.upper())
    if search:
        calls = calls.filter(
            Q(symbol__icontains=search) | Q(broker__name__icontains=search)
        )
    
    brokers = Broker.objects.all()
    
    context = {
        'calls': calls,
        'brokers': brokers,
        'trade_type': 'Futures',
        'trade_description': 'Futures & derivatives trading opportunities',
        'selected_broker': broker_id,
        'selected_action': action,
        'search_query': search,
    }
    
    return render(request, 'trades/futures.html', context)


def options_trades_view(request):
    """Options trades"""
    calls = ResearchCall.objects.filter(
        status='ACTIVE'
    ).filter(
        Q(symbol__icontains='OPT') | Q(symbol__icontains='CE') | Q(symbol__icontains='PE') | Q(notes__icontains='option')
    ).select_related('broker').order_by('-published_at')
    
    # Apply filters
    broker_id = request.GET.get('broker')
    action = request.GET.get('action')
    search = request.GET.get('search')
    
    if broker_id:
        calls = calls.filter(broker_id=broker_id)
    if action:
        calls = calls.filter(action=action.upper())
    if search:
        calls = calls.filter(
            Q(symbol__icontains=search) | Q(broker__name__icontains=search)
        )
    
    brokers = Broker.objects.all()
    
    context = {
        'calls': calls,
        'brokers': brokers,
        'trade_type': 'Options',
        'trade_description': 'Options trading strategies (Call & Put)',
        'selected_broker': broker_id,
        'selected_action': action,
        'search_query': search,
    }
    
    return render(request, 'trades/options.html', context)


def commodity_trades_view(request):
    """Commodity trades"""
    calls = ResearchCall.objects.filter(
        status='ACTIVE'
    ).filter(
        Q(symbol__icontains='GOLD') | Q(symbol__icontains='SILVER') | 
        Q(symbol__icontains='CRUDE') | Q(notes__icontains='commodity')
    ).select_related('broker', 'analyst__user').order_by('-published_at')
    
    # Apply filters
    broker_id = request.GET.get('broker')
    action = request.GET.get('action')
    search = request.GET.get('search')
    
    if broker_id:
        calls = calls.filter(broker_id=broker_id)
    if action:
        calls = calls.filter(action=action.upper())
    if search:
        calls = calls.filter(
            Q(symbol__icontains=search) | Q(broker__name__icontains=search)
        )
    
    brokers = Broker.objects.all()
    
    context = {
        'calls': calls,
        'brokers': brokers,
        'trade_type': 'Commodity',
        'trade_description': 'Commodity trading (Gold, Silver, Crude Oil, etc.)',
        'selected_broker': broker_id,
        'selected_action': action,
        'search_query': search,
    }
    
    return render(request, 'trades/commodity.html', context)
