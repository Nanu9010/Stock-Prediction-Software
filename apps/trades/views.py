"""
Views for different trade types and categories
Unified into a single parameterized view to eliminate duplication.
"""
from django.shortcuts import render
from django.db.models import Q
from apps.research_calls.models import ResearchCall
from apps.brokers.models import Broker


# Trade type configurations: (call_type_filter, display_name, description)
TRADE_TYPES = {
    'short-term': {
        'filter': {'call_type': 'SHORT_TERM'},
        'name': 'Short Term',
        'description': 'Quick trades with 1-7 days holding period',
    },
    'medium-term': {
        'filter': {'call_type': 'MEDIUM_TERM'},
        'name': 'Medium Term',
        'description': 'Swing trades with 1-4 weeks holding period',
    },
    'long-term': {
        'filter': {'call_type': 'LONG_TERM'},
        'name': 'Long Term',
        'description': 'Investment ideas with 1+ months holding period',
    },
    'futures': {
        'filter': None,  # uses Q objects below
        'name': 'Futures',
        'description': 'Futures & derivatives trading opportunities',
    },
    'options': {
        'filter': None,
        'name': 'Options',
        'description': 'Options trading strategies (Call & Put)',
    },
    'commodity': {
        'filter': None,
        'name': 'Commodity',
        'description': 'Commodity trading (Gold, Silver, Crude Oil, etc.)',
    },
}


def trade_list_view(request, trade_type):
    """Unified view for all trade types — replaces 6 duplicate views."""
    config = TRADE_TYPES.get(trade_type)
    if not config:
        from django.http import Http404
        raise Http404(f"Unknown trade type: {trade_type}")

    # Base queryset
    calls = ResearchCall.objects.filter(status='ACTIVE').select_related('broker').order_by('-published_at')

    # Apply trade-type-specific filter
    if config['filter']:
        calls = calls.filter(**config['filter'])
    elif trade_type == 'futures':
        calls = calls.filter(Q(symbol__icontains='FUT') | Q(notes__icontains='futures'))
    elif trade_type == 'options':
        calls = calls.filter(
            Q(symbol__icontains='OPT') | Q(symbol__icontains='CE') |
            Q(symbol__icontains='PE') | Q(notes__icontains='option')
        )
    elif trade_type == 'commodity':
        calls = calls.filter(
            Q(symbol__icontains='GOLD') | Q(symbol__icontains='SILVER') |
            Q(symbol__icontains='CRUDE') | Q(notes__icontains='commodity')
        )

    # Common filters (broker, action, search)
    broker_id = request.GET.get('broker')
    action = request.GET.get('action')
    search = request.GET.get('search')

    if broker_id:
        calls = calls.filter(broker_id=broker_id)
    if action:
        calls = calls.filter(action=action.upper())
    if search:
        calls = calls.filter(Q(symbol__icontains=search) | Q(broker__name__icontains=search))

    context = {
        'calls': calls,
        'brokers': Broker.objects.all(),
        'trade_type': config['name'],
        'trade_description': config['description'],
        'selected_broker': broker_id,
        'selected_action': action,
        'search_query': search,
    }

    return render(request, 'trades/trade_list.html', context)
