"""
Custom middleware for audit logging and security
"""
from django.utils import timezone
from apps.audit.models import AuditLog


class AuditLogMiddleware:
    """
    Middleware to log all critical state-changing actions
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Log state-changing actions (POST, PUT, PATCH, DELETE)
        if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            if request.user.is_authenticated:
                # Skip logging for certain paths (e.g., static files, admin media)
                if not self._should_skip_logging(request.path):
                    try:
                        AuditLog.objects.create(
                            user=request.user,
                            action=f"{request.method} {request.path}",
                            entity_type='http_request',
                            entity_id=0,
                            new_values={
                                'method': request.method,
                                'path': request.path,
                                'status_code': response.status_code,
                            },
                            ip_address=self._get_client_ip(request),
                            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
                        )
                    except Exception as e:
                        # Don't break the request if audit logging fails
                        print(f"Audit logging failed: {e}")
        
        return response
    
    def _should_skip_logging(self, path):
        """Determine if path should be skipped from audit logging"""
        skip_prefixes = [
            '/static/',
            '/media/',
            '/__debug__/',
            '/admin/jsi18n/',
        ]
        return any(path.startswith(prefix) for prefix in skip_prefixes)
    
    def _get_client_ip(self, request):
        """Get client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip[:45]  # Limit to 45 chars (IPv6 max length)


class LastActivityMiddleware:
    """
    Update user's last activity timestamp
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        if request.user.is_authenticated:
            # Update last_login_at every 5 minutes to avoid too many DB writes
            if hasattr(request.user, 'last_login_at'):
                last_activity = request.user.last_login_at
                if not last_activity or (timezone.now() - last_activity).seconds > 300:
                    request.user.last_login_at = timezone.now()
                    request.user.save(update_fields=['last_login_at'])
        
        return response
