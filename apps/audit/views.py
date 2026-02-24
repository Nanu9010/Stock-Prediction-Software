"""
Views for the audit app.
Provides read-only access to AuditLog records via REST API.
Admin users can see all logs; customers see only their own.
"""
from rest_framework import generics, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from apps.audit.models import AuditLog
from apps.audit.serializers import AuditLogSerializer


class IsAdminUser(permissions.BasePermission):
    """Allow access only to admin-role users."""

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'ADMIN'


class AuditLogListView(generics.ListAPIView):
    """
    GET /api/audit/logs/
    Admin-only. Returns full paginated audit log list.
    Supports filtering by action, model_name, and ordering by created_at.
    """
    serializer_class = AuditLogSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['action', 'model_name', 'object_id']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        return AuditLog.objects.select_related('user').all()


class AuditLogDetailView(generics.RetrieveAPIView):
    """
    GET /api/audit/logs/<pk>/
    Admin-only. Returns a single audit log entry.
    """
    serializer_class = AuditLogSerializer
    permission_classes = [IsAdminUser]
    queryset = AuditLog.objects.select_related('user').all()


class MyAuditLogListView(generics.ListAPIView):
    """
    GET /api/audit/my-logs/
    Authenticated users can see their own audit trail.
    """
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering = ['-created_at']

    def get_queryset(self):
        return AuditLog.objects.filter(user=self.request.user).select_related('user')
