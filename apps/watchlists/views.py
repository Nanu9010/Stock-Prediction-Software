"""
Watchlist views for managing watchlists
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from apps.watchlists.models import Watchlist, WatchlistItem
from apps.research_calls.models import ResearchCall


@login_required
def watchlist_view(request):
    """View user's watchlist"""
    watchlist, created = Watchlist.objects.get_or_create(
        user=request.user,
        defaults={'name': 'My Watchlist'}
    )
    
    items = watchlist.items.filter(
        is_active=True
    ).select_related('research_call__broker')
    
    context = {
        'watchlist': watchlist,
        'items': items,
    }
    
    return render(request, 'watchlists/watchlist.html', context)


@login_required
def add_to_watchlist_view(request):
    """Add research call to watchlist"""
    if request.method == 'POST':
        call_id = request.POST.get('call_id')
        
        try:
            call = ResearchCall.objects.get(id=call_id)
            watchlist, created = Watchlist.objects.get_or_create(
                user=request.user,
                defaults={'name': 'My Watchlist'}
            )
            
            # Check if already in watchlist
            existing = WatchlistItem.objects.filter(
                watchlist=watchlist,
                research_call=call,
                is_active=True
            ).first()
            
            if existing:
                messages.info(request, f'{call.symbol} is already in your watchlist')
            else:
                WatchlistItem.objects.create(
                    watchlist=watchlist,
                    research_call=call
                )
                messages.success(request, f'{call.symbol} added to watchlist!')
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Added to watchlist'})
            
            return redirect('watchlists:watchlist')
        
        except Exception as e:
            messages.error(request, f'Error adding to watchlist: {str(e)}')
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': str(e)})
            
            return redirect('research_calls:list')
    
    return redirect('research_calls:list')


@login_required
def remove_from_watchlist_view(request, pk):
    """Remove item from watchlist"""
    item = get_object_or_404(WatchlistItem, pk=pk, watchlist__user=request.user)
    
    item.is_active = False
    item.save()
    
    messages.success(request, f'{item.research_call.symbol} removed from watchlist')
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    
    return redirect('watchlists:watchlist')
