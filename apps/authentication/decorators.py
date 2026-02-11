"""
Authentication decorators for role-based access control
"""
from functools import wraps
from django.shortcuts import redirect
from django.http import HttpResponseForbidden
from django.contrib import messages


def role_required(*roles):
    """
    Decorator to restrict view access based on user roles.
    
    Usage:
        @role_required('ADMIN', 'ANALYST')
        def create_research_call(request):
            pass
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.warning(request, 'Please login to access this page.')
                return redirect('authentication:login')
            
            if request.user.role not in roles:
                messages.error(request, "You don't have permission to access this page.")
                return HttpResponseForbidden(
                    "You don't have permission to access this page. "
                    f"Required roles: {', '.join(roles)}"
                )
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


def admin_required(view_func):
    """Shortcut decorator for admin-only views"""
    return role_required('ADMIN')(view_func)


def analyst_required(view_func):
    """Shortcut decorator for analyst-only views"""
    return role_required('ANALYST')(view_func)


def customer_required(view_func):
    """Shortcut decorator for customer-only views"""
    return role_required('CUSTOMER')(view_func)


def analyst_or_admin_required(view_func):
    """Shortcut decorator for analyst or admin views"""
    return role_required('ANALYST', 'ADMIN')(view_func)
