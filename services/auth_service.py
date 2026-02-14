"""
Authentication Service
Encapsulates user registration, login, and session management logic.
"""
from django.contrib.auth import login, logout, authenticate
from django.utils import timezone
from apps.authentication.models import User, UserSession
from apps.authentication.forms import UserRegistrationForm, UserLoginForm

class AuthService:
    
    @staticmethod
    def register_user(request, form):
        """
        Register a new user and create an active session.
        
        Args:
            request: HttpRequest object
            form: Validated UserRegistrationForm
            
        Returns:
            User: The created user instance
        """
        user = form.save()
        
        # Log the user in
        login(request, user)
        
        # Create session record
        AuthService._create_user_session(request, user)
        
        return user
    
    @staticmethod
    def login_user(request, form):
        """
        Authenticate and login a user, creating a session.
        
        Args:
            request: HttpRequest object
            form: Validated UserLoginForm
            
        Returns:
            User: The authenticated user instance
        """
        user = form.get_user()
        login(request, user)
        
        # Create session record
        AuthService._create_user_session(request, user)
        
        # Set session expiry
        if not form.cleaned_data.get('remember_me'):
            request.session.set_expiry(0)  # Session expires when browser closes
            
        return user

    @staticmethod
    def logout_user(request):
        """
        Logout the user.
        """
        logout(request)

    @staticmethod
    def _create_user_session(request, user):
        """
        Helper to create a UserSession record.
        """
        UserSession.objects.create(
            user=user,
            session_token=request.session.session_key or '',
            ip_address=request.META.get('REMOTE_ADDR', ''),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
            expires_at=timezone.now() + timezone.timedelta(days=7)
        )
