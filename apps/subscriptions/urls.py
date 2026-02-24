"""
URL configuration for the subscriptions app.
"""
from django.urls import path
from apps.subscriptions import views

app_name = 'subscriptions'

urlpatterns = [
    # Public plan endpoints
    path('plans/', views.SubscriptionPlanListView.as_view(), name='plan-list'),
    path('plans/<int:pk>/', views.SubscriptionPlanDetailView.as_view(), name='plan-detail'),

    # Customer: own subscriptions
    path('my/', views.MySubscriptionsView.as_view(), name='my-subscriptions'),
    path('my/active/', views.ActiveSubscriptionView.as_view(), name='my-active-subscription'),

    # Admin: manage plans and user subscriptions
    path('admin/plans/', views.AdminSubscriptionPlanListCreateView.as_view(), name='admin-plan-list'),
    path('admin/plans/<int:pk>/', views.AdminSubscriptionPlanDetailView.as_view(), name='admin-plan-detail'),
    path('admin/users/', views.AdminUserSubscriptionsView.as_view(), name='admin-user-subscriptions'),
]
