"""
Password reset views
"""
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings
from apps.authentication.models import User


def password_reset_request(request):
    """Request password reset"""
    if request.method == 'POST':
        email = request.POST.get('email')
        
        try:
            user = User.objects.get(email=email)
            
            # Generate token
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # Build reset link
            reset_link = request.build_absolute_uri(
                f'/auth/password-reset/{uid}/{token}/'
            )
            
            # Send email
            subject = 'Password Reset Request'
            message = f'Click the link below to reset your password:\n\n{reset_link}\n\nThis link will expire in 24 hours.'
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            
            messages.success(request, 'Password reset link sent to your email!')
            return redirect('authentication:login')
            
        except User.DoesNotExist:
            messages.error(request, 'No account found with that email address')
    
    return render(request, 'authentication/password_reset_request.html')


def password_reset_confirm(request, uidb64, token):
    """Confirm password reset with token"""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            password = request.POST.get('password')
            password_confirm = request.POST.get('password_confirm')
            
            if password != password_confirm:
                messages.error(request, 'Passwords do not match')
            else:
                user.set_password(password)
                user.save()
                messages.success(request, 'Password reset successful! You can now login.')
                return redirect('authentication:login')
        
        return render(request, 'authentication/password_reset_confirm.html', {
            'validlink': True,
            'uidb64': uidb64,
            'token': token
        })
    else:
        messages.error(request, 'Invalid or expired reset link')
        return redirect('authentication:password_reset_request')
