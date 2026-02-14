"""
Enhanced research call views with card layout and filtering
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Avg
from apps.research_calls.models import ResearchCall
from apps.brokers.models import Broker
from apps.authentication.decorators import role_required





@login_required
@role_required(['ANALYST', 'ADMIN'])
def call_create_view(request):
    """Create new research call"""
    from .forms import ResearchCallForm
    
    if request.method == 'POST':
        form = ResearchCallForm(request.POST)
        if form.is_valid():
            call = form.save(commit=False)
            call.created_by = request.user
            if 'status' in request.POST:
                call.status = request.POST['status']
            call.save()
            messages.success(request, 'Research call created successfully!')
            return redirect('research_calls:call_detail', pk=call.pk)
    else:
        form = ResearchCallForm()
        
    return render(request, 'research_calls/call_form.html', {'form': form})


@login_required
@role_required(['ANALYST', 'ADMIN'])
def call_edit_view(request, pk):
    """Edit existing research call"""
    from .forms import ResearchCallForm
    call = get_object_or_404(ResearchCall, pk=pk)
    
    if request.method == 'POST':
        form = ResearchCallForm(request.POST, instance=call)
        if form.is_valid():
            call = form.save(commit=False)
            if 'status' in request.POST:
                call.status = request.POST['status']
            call.save()
            messages.success(request, 'Research call updated successfully!')
            return redirect('research_calls:call_detail', pk=call.pk)
    else:
        form = ResearchCallForm(instance=call)
        
    return render(request, 'research_calls/call_form.html', {'form': form, 'call': call})


@login_required
@role_required(['ADMIN'])
def call_approve_view(request, pk):
    """Approve a research call"""
    call = get_object_or_404(ResearchCall, pk=pk)
    from apps.research_calls.services import approve_research_call
    approve_research_call(call, request.user)
    messages.success(request, f'Call {call.symbol} approved successfully!')
    return redirect('research_calls:call_detail', pk=pk)


@login_required
@role_required(['ADMIN'])
def call_publish_view(request, pk):
    """Publish a research call"""
    call = get_object_or_404(ResearchCall, pk=pk)
    from apps.research_calls.services import publish_research_call
    publish_research_call(call, request.user)
    messages.success(request, f'Call {call.symbol} published successfully!')
    return redirect('research_calls:call_detail', pk=pk)


@login_required
def call_detail_view(request, pk):
    """Call detail view with exit functionality"""
    call = get_object_or_404(
        ResearchCall.objects.select_related('broker', 'created_by'),
        pk=pk
    )
    
    # Check permission for ACTIVE calls
    if call.status == 'ACTIVE':
        # Safely check for active subscription
        has_active_sub = False
        if request.user.is_authenticated:
            subscription = getattr(request.user, 'subscription', None)
            if subscription:
                # Check method or property
                has_active_sub = subscription.is_active() if callable(getattr(subscription, 'is_active', None)) else subscription.is_active
        
        is_pro = has_active_sub
        
        if not is_pro and not request.user.role == 'ADMIN':
            messages.warning(request, 'You must be a PRO member to view this active trade.')
            return redirect('payments:membership')

    # Check if user has this in portfolio
    in_portfolio = False
    portfolio_item = None
    
    if request.user.is_authenticated and request.user.role == 'CUSTOMER':
        from apps.portfolios.models import Portfolio, PortfolioItem
        try:
            portfolio = Portfolio.objects.get(user=request.user)
            portfolio_item = PortfolioItem.objects.filter(
                portfolio=portfolio,
                research_call=call,
                status='ACTIVE'
            ).first()
            in_portfolio = portfolio_item is not None
        except Portfolio.DoesNotExist:
            pass
    
    context = {
        'call': call,
        'in_portfolio': in_portfolio,
        'portfolio_item': portfolio_item,
    }
    
    return render(request, 'research_calls/call_detail.html', context)


def live_calls_view(request):
    """Display all active research calls with category filters"""
    calls = ResearchCall.objects.filter(status='ACTIVE').select_related('broker', 'created_by')
    
    # Category filter
    category = request.GET.get('category', 'all')
    if category != 'all':
        normalized_cat = category.upper().replace(' ', '_')
        if normalized_cat in ['FUTURES', 'OPTIONS', 'COMMODITY']:
            calls = calls.filter(instrument_type=normalized_cat)
        else:
            calls = calls.filter(call_type=normalized_cat)
    
    # Context (categorized_calls removed as unused in new template)
    context = {
        'calls': calls,
        'selected_category': category,
        'total_count': calls.count(),
    }
    return render(request, 'research_calls/live_trades.html', context)


def closed_calls_view(request):
    """Display closed research calls with performance metrics"""
    calls = ResearchCall.objects.filter(status='CLOSED').select_related('broker', 'created_by')
    
    # Category filter
    category = request.GET.get('category', 'all')
    if category != 'all':
        normalized_cat = category.upper().replace(' ', '_')
        if normalized_cat in ['FUTURES', 'OPTIONS', 'COMMODITY']:
            calls = calls.filter(instrument_type=normalized_cat)
        else:
            calls = calls.filter(call_type=normalized_cat)
    
    # Search filter
    search_query = request.GET.get('search')
    if search_query:
        calls = calls.filter(
            Q(symbol__icontains=search_query) |
            Q(broker__name__icontains=search_query)
        )
    
    # Calculate performance metrics
    total_calls = calls.count()
    successful_calls = calls.filter(actual_return_percentage__gt=0).count()
    failed_calls = calls.filter(actual_return_percentage__lte=0).count()
    accuracy = (successful_calls / total_calls * 100) if total_calls > 0 else 0
    
    context = {
        'calls': calls,
        'selected_category': category,
        'search_query': search_query,
        'total_calls': total_calls,
        'successful_calls': successful_calls,
        'failed_calls': failed_calls,
        'accuracy': accuracy,
    }
    return render(request, 'research_calls/closed_trades.html', context)

