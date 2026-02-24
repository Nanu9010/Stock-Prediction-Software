"""
Views for the brokers app.
Public: List and detail of active brokers.
Admin: Full CRUD and performance metrics.
"""
from rest_framework import generics, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from apps.brokers.models import Broker, BrokerPerformanceMetrics
from apps.brokers.serializers import (
    BrokerSerializer,
    BrokerCreateUpdateSerializer,
    BrokerPerformanceMetricsSerializer,
)


class IsAdminUser(permissions.BasePermission):
    """Allow access only to admin-role users."""

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'ADMIN'


# ─── Public / Read Views ────────────────────────────────────────────────────

class BrokerListView(generics.ListAPIView):
    """
    GET /api/brokers/
    Public list of all active, verified brokers.
    """
    serializer_class = BrokerSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'sebi_registration_no']
    ordering_fields = ['overall_accuracy', 'name', 'total_calls_published']
    ordering = ['-overall_accuracy']

    def get_queryset(self):
        return Broker.objects.filter(is_active=True, is_verified=True)


class BrokerDetailView(generics.RetrieveAPIView):
    """
    GET /api/brokers/<pk>/
    Public detail of a single broker.
    """
    serializer_class = BrokerSerializer
    permission_classes = [permissions.AllowAny]
    queryset = Broker.objects.filter(is_active=True)


class BrokerPerformanceMetricsView(generics.ListAPIView):
    """
    GET /api/brokers/<pk>/metrics/
    Performance metrics history for a broker (authenticated users only).
    """
    serializer_class = BrokerPerformanceMetricsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return BrokerPerformanceMetrics.objects.filter(
            broker_id=self.kwargs['pk']
        ).order_by('-metric_date')[:30]  # Last 30 records


# ─── Admin CRUD Views ───────────────────────────────────────────────────────

class AdminBrokerListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/admin/brokers/     — list all brokers (including inactive)
    POST /api/admin/brokers/     — create a new broker
    Admin only.
    """
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['is_active', 'is_verified']
    search_fields = ['name']

    def get_queryset(self):
        return Broker.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return BrokerCreateUpdateSerializer
        return BrokerSerializer


class AdminBrokerDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/admin/brokers/<pk>/  — retrieve
    PATCH  /api/admin/brokers/<pk>/  — update
    DELETE /api/admin/brokers/<pk>/  — soft delete (set is_active=False)
    Admin only.
    """
    permission_classes = [IsAdminUser]
    queryset = Broker.objects.all()

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return BrokerCreateUpdateSerializer
        return BrokerSerializer

    def perform_destroy(self, instance):
        """Soft delete — mark inactive instead of hard delete."""
        instance.is_active = False
        instance.save(update_fields=['is_active', 'updated_at'])
