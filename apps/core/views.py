"""
Views for the core app.
Provides utility API endpoints (health check, API version info).
No database models — only infrastructure endpoints.
"""
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from apps.core.serializers import HealthCheckSerializer


class HealthCheckView(APIView):
    """
    GET /api/core/health/
    Public endpoint — returns server health status.
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        data = {
            'status': 'ok',
            'version': '1.0.0',
            'timestamp': timezone.now(),
        }
        serializer = HealthCheckSerializer(data)
        return Response(serializer.data)


class APIInfoView(APIView):
    """
    GET /api/core/info/
    Public endpoint — returns basic API information.
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response({
            'name': 'Stock Prediction System API',
            'version': '1.0.0',
            'description': 'SEBI-compliant stock research platform API',
            'docs_url': '/api/docs/',
            'apps': [
                'authentication', 'brokers', 'research_calls',
                'portfolios', 'watchlists', 'subscriptions',
                'notifications', 'payments', 'market_data',
                'audit', 'dashboard', 'trades',
            ],
        })
