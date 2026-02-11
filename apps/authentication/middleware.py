"""
Authentication middleware
"""
from django.utils import timezone
from apps.authentication.models import UserSession


class UpdateLastActivityMiddleware:
    """
    Middleware to update user's last activity timestamp
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
