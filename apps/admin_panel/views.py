"""
Admin Panel Views
Comprehensive admin dashboard with CRUD operations for all entities
"""
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView, DetailView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from datetime import timedelta
from .forms import ResearchCallForm, BrokerForm, UserForm, PortfolioForm, WatchlistForm, SubscriptionPlanForm

from apps.authentication.models import User
from apps.brokers.models import Broker
from apps.research_calls.models import ResearchCall
from apps.portfolios.models import Portfolio, PortfolioItem
from apps.watchlists.models import Watchlist, WatchlistItem
from apps.subscriptions.models import SubscriptionPlan
from apps.payments.models import Payment


class AdminRequiredMixin(UserPassesTestMixin):
    """Mixin to ensure only admin users can access views"""
    
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == 'ADMIN'
    
    def handle_no_permission(self):
        messages.error(self.request, 'You do not have permission to access the admin panel.')
        return redirect('dashboard:home')


class AdminDashboardView(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    """Main admin dashboard with analytics overview"""
    template_name = 'admin_panel/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        today = timezone.now().date()
        last_30_days = today - timedelta(days=30)
        
        # User statistics
        context['total_users'] = User.objects.count()
        context['active_users'] = User.objects.filter(is_active=True).count()
        context['new_users_30d'] = User.objects.filter(created_at__gte=last_30_days).count()
        
        # Research call statistics
        context['total_calls'] = ResearchCall.objects.count()
        context['active_calls'] = ResearchCall.objects.filter(status='ACTIVE').count()
        context['pending_calls'] = ResearchCall.objects.filter(status='PENDING_APPROVAL').count()
        
        # Success rate
        closed_calls = ResearchCall.objects.filter(status='CLOSED')
        successful_calls = closed_calls.filter(actual_return_percentage__gt=0).count()
        total_closed = closed_calls.count()
        context['success_rate'] = (successful_calls / total_closed * 100) if total_closed > 0 else 0
        
        # Broker statistics
        context['total_brokers'] = Broker.objects.count()
        context['active_brokers'] = Broker.objects.filter(is_active=True).count()
        
        # Portfolio statistics
        context['total_portfolios'] = Portfolio.objects.count()
        context['total_watchlists'] = Watchlist.objects.count()
        
        # Top brokers by accuracy
        context['top_brokers'] = Broker.objects.filter(
            is_active=True
        ).order_by('-overall_accuracy')[:5]
        
        # Recent calls
        context['recent_calls'] = ResearchCall.objects.select_related(
            'broker', 'created_by'
        ).order_by('-created_at')[:10]
        
        # Pending approvals
        context['pending_approvals'] = ResearchCall.objects.filter(
            status='PENDING_APPROVAL'
        ).count()
        
        return context


# ─── Research Calls Management ────────────────────────────────

class CallListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    """List all research calls with filters"""
    model = ResearchCall
    template_name = 'admin_panel/calls/list.html'
    context_object_name = 'calls'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = ResearchCall.objects.select_related('broker', 'created_by').order_by('-created_at')
        
        status = self.request.GET.get('status')
        broker_id = self.request.GET.get('broker')
        search = self.request.GET.get('search')
        
        if status:
            queryset = queryset.filter(status=status)
        if broker_id:
            queryset = queryset.filter(broker_id=broker_id)
        if search:
            queryset = queryset.filter(
                Q(symbol__icontains=search) | 
                Q(broker__name__icontains=search)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['brokers'] = Broker.objects.all()
        context['selected_status'] = self.request.GET.get('status', '')
        context['selected_broker'] = self.request.GET.get('broker', '')
        context['search_query'] = self.request.GET.get('search', '')
        return context


class CallCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    """Create a new research call"""
    model = ResearchCall
    form_class = ResearchCallForm
    template_name = 'admin_panel/calls/form.html'
    success_url = reverse_lazy('admin_panel:calls_list')
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Research call created successfully.')
        return super().form_valid(form)


class CallUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    """Update an existing research call"""
    model = ResearchCall
    form_class = ResearchCallForm
    template_name = 'admin_panel/calls/form.html'
    success_url = reverse_lazy('admin_panel:calls_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Research call updated successfully.')
        return super().form_valid(form)


class CallDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    """Delete a research call"""
    model = ResearchCall
    template_name = 'admin_panel/calls/confirm_delete.html'
    success_url = reverse_lazy('admin_panel:calls_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Research call deleted successfully.')
        return super().delete(request, *args, **kwargs)


class CallDetailView(LoginRequiredMixin, AdminRequiredMixin, DetailView):
    """View research call details"""
    model = ResearchCall
    template_name = 'admin_panel/calls/detail.html'
    context_object_name = 'call'


# ─── Broker Management ───────────────────────────────────────

class BrokerListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    """List all brokers"""
    model = Broker
    template_name = 'admin_panel/brokers/list.html'
    context_object_name = 'brokers'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Broker.objects.annotate(
            total_calls=Count('research_calls')
        ).order_by('-created_at')
        
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(sebi_registration_no__icontains=search)
            )
        
        return queryset


class BrokerDetailView(LoginRequiredMixin, AdminRequiredMixin, DetailView):
    """View broker details"""
    model = Broker
    template_name = 'admin_panel/brokers/detail.html'
    context_object_name = 'broker'


class BrokerCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    """Create a new broker"""
    model = Broker
    form_class = BrokerForm
    template_name = 'admin_panel/brokers/form.html'
    success_url = reverse_lazy('admin_panel:brokers_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Broker created successfully.')
        return super().form_valid(form)


class BrokerUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    """Update an existing broker"""
    model = Broker
    form_class = BrokerForm
    template_name = 'admin_panel/brokers/form.html'
    success_url = reverse_lazy('admin_panel:brokers_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Broker updated successfully.')
        return super().form_valid(form)


# ─── User Management ─────────────────────────────────────────

class UserListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    """List all users"""
    model = User
    template_name = 'admin_panel/users/list.html'
    context_object_name = 'users'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = User.objects.order_by('-created_at')
        role = self.request.GET.get('role')
        search = self.request.GET.get('search')
        
        if role:
            queryset = queryset.filter(role=role)
        if search:
            queryset = queryset.filter(
                Q(email__icontains=search) | 
                Q(first_name__icontains=search) | 
                Q(last_name__icontains=search)
            )
        
        return queryset


class UserDetailView(LoginRequiredMixin, AdminRequiredMixin, DetailView):
    """View user details"""
    model = User
    template_name = 'admin_panel/users/detail.html'
    context_object_name = 'user_detail'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        
        try:
            portfolio = user.portfolios.first()
            context['portfolio'] = portfolio
            if portfolio:
                context['portfolio_items'] = portfolio.items.all()[:10]
        except Exception:
            context['portfolio'] = None
        
        return context


class UserUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    """Update an existing user"""
    model = User
    form_class = UserForm
    template_name = 'admin_panel/users/form.html'
    success_url = reverse_lazy('admin_panel:users_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'User updated successfully.')
        return super().form_valid(form)


class UserDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    """Delete a user"""
    model = User
    template_name = 'admin_panel/users/confirm_delete.html'
    success_url = reverse_lazy('admin_panel:users_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'User deleted successfully.')
        return super().delete(request, *args, **kwargs)


# ─── Portfolio Management ─────────────────────────────────────

class PortfolioListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    """List all portfolios"""
    model = Portfolio
    template_name = 'admin_panel/portfolios/list.html'
    context_object_name = 'portfolios'
    paginate_by = 20
    
    def get_queryset(self):
        return Portfolio.objects.select_related('user').annotate(
            item_count=Count('items'),
        ).order_by('-created_at')


class PortfolioDetailView(LoginRequiredMixin, AdminRequiredMixin, DetailView):
    """View portfolio details"""
    model = Portfolio
    template_name = 'admin_panel/portfolios/detail.html'
    context_object_name = 'portfolio'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['items'] = self.object.items.select_related('research_call').all()
        return context


class PortfolioDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    """Delete a portfolio"""
    model = Portfolio
    template_name = 'admin_panel/portfolios/confirm_delete.html'
    success_url = reverse_lazy('admin_panel:portfolios_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Portfolio deleted successfully.')
        return super().delete(request, *args, **kwargs)


# ─── Watchlist Management ─────────────────────────────────────

class WatchlistListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    """List all watchlists"""
    model = Watchlist
    template_name = 'admin_panel/watchlists/list.html'
    context_object_name = 'watchlists'
    paginate_by = 20
    
    def get_queryset(self):
        return Watchlist.objects.select_related('user').annotate(
            item_count=Count('items'),
        ).order_by('-created_at')


class WatchlistDetailView(LoginRequiredMixin, AdminRequiredMixin, DetailView):
    """View watchlist details"""
    model = Watchlist
    template_name = 'admin_panel/watchlists/detail.html'
    context_object_name = 'watchlist'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['items'] = self.object.items.select_related('research_call').all()
        return context


class WatchlistDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    """Delete a watchlist"""
    model = Watchlist
    template_name = 'admin_panel/watchlists/confirm_delete.html'
    success_url = reverse_lazy('admin_panel:watchlists_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Watchlist deleted successfully.')
        return super().delete(request, *args, **kwargs)


# ─── Subscription Plan Management ────────────────────────────

class SubscriptionPlanListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    """List all subscription plans"""
    model = SubscriptionPlan
    template_name = 'admin_panel/subscriptions/list.html'
    context_object_name = 'plans'
    paginate_by = 20


class SubscriptionPlanCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    """Create a new subscription plan"""
    model = SubscriptionPlan
    form_class = SubscriptionPlanForm
    template_name = 'admin_panel/subscriptions/form.html'
    success_url = reverse_lazy('admin_panel:subscriptions_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Subscription plan created successfully.')
        return super().form_valid(form)


class SubscriptionPlanUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    """Update a subscription plan"""
    model = SubscriptionPlan
    form_class = SubscriptionPlanForm
    template_name = 'admin_panel/subscriptions/form.html'
    success_url = reverse_lazy('admin_panel:subscriptions_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Subscription plan updated successfully.')
        return super().form_valid(form)


class SubscriptionPlanDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    """Delete a subscription plan"""
    model = SubscriptionPlan
    template_name = 'admin_panel/subscriptions/confirm_delete.html'
    success_url = reverse_lazy('admin_panel:subscriptions_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Subscription plan deleted successfully.')
        return super().delete(request, *args, **kwargs)


# ─── Payment Management (Read-Only) ──────────────────────────

class PaymentListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    """List all payments"""
    model = Payment
    template_name = 'admin_panel/payments/list.html'
    context_object_name = 'payments'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Payment.objects.select_related('user').order_by('-created_at')
        status = self.request.GET.get('status')
        search = self.request.GET.get('search')
        
        if status:
            queryset = queryset.filter(status=status)
        if search:
            queryset = queryset.filter(
                Q(user__email__icontains=search) |
                Q(transaction_id__icontains=search)
            )
        
        return queryset


class PaymentDetailView(LoginRequiredMixin, AdminRequiredMixin, DetailView):
    """View payment details (read-only)"""
    model = Payment
    template_name = 'admin_panel/payments/detail.html'
    context_object_name = 'payment'
