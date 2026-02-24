"""
Views for the subscriptions app.
Customers can view plans and their own subscriptions.
Admins can manage all subscriptions.
"""
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.subscriptions.models import SubscriptionPlan, UserSubscription
from apps.subscriptions.serializers import (
    SubscriptionPlanSerializer,
    UserSubscriptionSerializer,
)


class IsAdminUser(permissions.BasePermission):
    """Allow access only to admin-role users."""

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'ADMIN'


# ─── Plan Views ─────────────────────────────────────────────────────────────

class SubscriptionPlanListView(generics.ListAPIView):
    """
    GET /api/subscriptions/plans/
    Public. Returns all active subscription plans ordered by display_order.
    """
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return SubscriptionPlan.objects.filter(is_active=True)


class SubscriptionPlanDetailView(generics.RetrieveAPIView):
    """
    GET /api/subscriptions/plans/<pk>/
    Public. Returns details of a single subscription plan.
    """
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [permissions.AllowAny]
    queryset = SubscriptionPlan.objects.filter(is_active=True)


# ─── User Subscription Views ─────────────────────────────────────────────────

class MySubscriptionsView(generics.ListAPIView):
    """
    GET /api/subscriptions/my/
    Authenticated users can view all their own subscriptions.
    """
    serializer_class = UserSubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserSubscription.objects.filter(user=self.request.user).select_related('plan')


class ActiveSubscriptionView(APIView):
    """
    GET /api/subscriptions/my/active/
    Returns the user's currently active subscription, or 404.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        from django.utils import timezone
        subscription = UserSubscription.objects.filter(
            user=request.user,
            status='ACTIVE',
            end_date__gt=timezone.now().date(),
        ).select_related('plan').first()

        if not subscription:
            return Response({'detail': 'No active subscription found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserSubscriptionSerializer(subscription)
        return Response(serializer.data)


# ─── Admin Views ─────────────────────────────────────────────────────────────

class AdminSubscriptionPlanListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/subscriptions/admin/plans/   — list all plans (including inactive)
    POST /api/subscriptions/admin/plans/   — create a new plan
    Admin only.
    """
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [IsAdminUser]
    queryset = SubscriptionPlan.objects.all()


class AdminSubscriptionPlanDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/subscriptions/admin/plans/<pk>/
    PATCH  /api/subscriptions/admin/plans/<pk>/
    DELETE /api/subscriptions/admin/plans/<pk>/
    Admin only.
    """
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [IsAdminUser]
    queryset = SubscriptionPlan.objects.all()


class AdminUserSubscriptionsView(generics.ListAPIView):
    """
    GET /api/subscriptions/admin/users/
    Admin: View all user subscriptions.
    """
    serializer_class = UserSubscriptionSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        return UserSubscription.objects.select_related('user', 'plan').all()
