"""
Authentication views for login, register, logout, and profile management
"""
from django.shortcuts import render, redirect
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.authentication.forms import UserRegistrationForm, UserLoginForm, ProfileUpdateForm
from apps.authentication.models import UserSession
from services.auth_service import AuthService


def register_view(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('dashboard:dashboard')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = AuthService.register_user(request, form)
            
            messages.success(request, f'Welcome {user.get_full_name()}! Your account has been created successfully.')
            return redirect('dashboard:dashboard')
        else:
            print("Registration Form Errors:", form.errors)
    else:
        form = UserRegistrationForm()
    
    return render(request, 'authentication/register.html', {'form': form})


def login_view(request):
    """User login view"""
    if request.user.is_authenticated:
        return redirect('dashboard:dashboard')
    
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            user = AuthService.login_user(request, form)
            
            messages.success(request, f'Welcome back, {user.get_full_name()}!')
            
            # Redirect to next or dashboard
            next_url = request.GET.get('next', 'dashboard:dashboard')
            return redirect(next_url)
        else:
            print("Login Form Errors:", form.errors)
    else:
        form = UserLoginForm()
    
    return render(request, 'authentication/login.html', {'form': form})


@login_required
def logout_view(request):
    """User logout view"""
    user_name = request.user.get_full_name()
    AuthService.logout_user(request)
    messages.info(request, f'Goodbye, {user_name}! You have been logged out successfully.')
    return redirect('authentication:login')




@login_required
def profile_view(request):
    """User profile view and edit with subscription status"""
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('authentication:profile')
    else:
        form = ProfileUpdateForm(instance=request.user)
    
    # Get user's active subscription
    from apps.payments.models import Subscription
    current_subscription = Subscription.objects.filter(
        user=request.user,
        status='ACTIVE'
    ).select_related('payment').first()
    
    # Get portfolio summary
    portfolio_summary = None
    try:
        from apps.portfolios.models import Portfolio
        portfolio = Portfolio.objects.filter(user=request.user).first()
        if portfolio:
            portfolio_summary = {
                'total_value': portfolio.total_value,
                'total_invested': portfolio.total_invested,
                'profit_loss': portfolio.total_value - portfolio.total_invested if portfolio.total_value and portfolio.total_invested else 0,
                'profit_loss_percentage': ((portfolio.total_value - portfolio.total_invested) / portfolio.total_invested * 100) if portfolio.total_invested and portfolio.total_invested > 0 else 0,
            }
    except:
        pass
    
    context = {
        'form': form,
        'user': request.user,
        'current_subscription': current_subscription,
        'portfolio_summary': portfolio_summary,
    }
    return render(request, 'authentication/profile.html', context)
