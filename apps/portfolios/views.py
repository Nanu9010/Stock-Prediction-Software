"""
Portfolio views for portfolio management
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from apps.portfolios.models import Portfolio, PortfolioItem
from apps.portfolios.services import add_to_portfolio, exit_position, calculate_portfolio_summary
from apps.research_calls.models import ResearchCall


@login_required
def portfolio_view(request):
    """View user's portfolio"""
    portfolio, created = Portfolio.objects.get_or_create(
        user=request.user,
        defaults={'name': 'My Portfolio'}
    )
    
    active_items = portfolio.items.filter(
        status='ACTIVE'
    ).select_related('research_call__broker')
    
    closed_items = portfolio.items.filter(
        status='CLOSED'
    ).select_related('research_call__broker').order_by('-exit_date')[:10]
    
    summary = calculate_portfolio_summary(portfolio)
    
    context = {
        'portfolio': portfolio,
        'active_items': active_items,
        'closed_items': closed_items,
        'summary': summary,
    }
    
    return render(request, 'portfolios/portfolio.html', context)


@login_required
def add_to_portfolio_view(request):
    """Add research call to portfolio"""
    if request.method == 'POST':
        call_id = request.POST.get('call_id')
        entry_price = request.POST.get('entry_price')
        quantity = request.POST.get('quantity')
        
        try:
            call = ResearchCall.objects.get(id=call_id)
            item = add_to_portfolio(
                user=request.user,
                research_call=call,
                entry_price=entry_price,
                quantity=quantity
            )
            messages.success(request, f'{call.symbol} added to portfolio successfully!')
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Added to portfolio'})
            
            return redirect('portfolios:portfolio')
        
        except Exception as e:
            messages.error(request, f'Error adding to portfolio: {str(e)}')
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': str(e)})
            
            return redirect('research_calls:live_calls')
    
    return redirect('research_calls:live_calls')


@login_required
def exit_position_view(request, pk):
    """Exit a portfolio position"""
    item = get_object_or_404(PortfolioItem, pk=pk, portfolio__user=request.user)
    
    if request.method == 'POST':
        exit_price = request.POST.get('exit_price')
        
        try:
            exit_position(item, exit_price, exit_by=request.user)
            messages.success(request, f'Position in {item.research_call.symbol} closed successfully!')
        except Exception as e:
            messages.error(request, f'Error closing position: {str(e)}')
    
    return redirect('portfolios:portfolio')
