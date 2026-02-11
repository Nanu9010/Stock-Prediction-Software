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
from .forms import ResearchCallForm, BrokerForm

from apps.authentication.models import User
from apps.brokers.models import Broker
from apps.research_calls.models import ResearchCall
from apps.portfolios.models import Portfolio, PortfolioItem


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
        
        # Date ranges
        today = timezone.now().date()
        last_30_days = today - timedelta(days=30)
        
        # User statistics
        context['total_users'] = User.objects.count()
        context['active_users'] = User.objects.filter(is_active=True).count()
        context['new_users_30d'] = User.objects.filter(created_at__gte=last_30_days).count()
        
        # Research call statistics
        context['total_calls'] = ResearchCall.objects.count()
        context['active_calls'] = ResearchCall.objects.filter(status='ACTIVE').count()
        context['pending_calls'] = ResearchCall.objects.filter(status='PENDING').count()
        
        # Success rate
        closed_calls = ResearchCall.objects.filter(status='CLOSED')
        successful_calls = closed_calls.filter(actual_return_percentage__gt=0).count()
        total_closed = closed_calls.count()
        context['success_rate'] = (successful_calls / total_closed * 100) if total_closed > 0 else 0
        
        # Broker statistics
        context['total_brokers'] = Broker.objects.count()
        context['verified_brokers'] = Broker.objects.filter(is_verified=True).count()
        
        # Top brokers by accuracy
        context['top_brokers'] = Broker.objects.filter(
            is_verified=True
        ).order_by('-overall_accuracy')[:5]
        
        # Recent calls
        context['recent_calls'] = ResearchCall.objects.select_related(
            'broker', 'created_by', 'approved_by'
        ).order_by('-created_at')[:10]
        
        # Pending approvals
        context['pending_approvals'] = ResearchCall.objects.filter(
            status='PENDING'
        ).count()
        
        return context


# Research Calls Management Views
class CallListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    """List all research calls with filters"""
    model = ResearchCall
    template_name = 'admin_panel/calls/list.html'
    context_object_name = 'calls'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = ResearchCall.objects.select_related('broker', 'created_by', 'approved_by').order_by('-created_at')
        
        # Filters
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


# Broker Management Views
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
        
        # Filters
        verified = self.request.GET.get('verified')
        search = self.request.GET.get('search')
        
        if verified == 'true':
            queryset = queryset.filter(is_verified=True)
        elif verified == 'false':
            queryset = queryset.filter(is_verified=False)
        
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


# User Management Views
class UserListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    """List all users"""
    model = User
    template_name = 'admin_panel/users/list.html'
    context_object_name = 'users'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = User.objects.order_by('-created_at')
        
        # Filters
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
        
        # Get user's portfolio
        try:
            portfolio = user.portfolios.first()
            context['portfolio'] = portfolio
            if portfolio:
                context['portfolio_items'] = portfolio.items.all()[:10]
        except:
            context['portfolio'] = None
        
        return context

