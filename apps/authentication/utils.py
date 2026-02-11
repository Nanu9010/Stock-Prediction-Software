"""
Authentication utilities for token generation and email
"""
import secrets
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def generate_verification_token():
    """Generate a secure random token for email verification"""
    return secrets.token_urlsafe(32)


def send_verification_email(user, token):
    """
    Send email verification link to user
    
    Args:
        user: User instance
        token: Verification token
    """
    subject = 'Verify your Stock Research Platform account'
    verification_url = f"{settings.SITE_URL}/auth/verify/{token}/"
    
    html_message = render_to_string('authentication/emails/verification_email.html', {
        'user': user,
        'verification_url': verification_url,
    })
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=html_message,
        fail_silently=False,
    )


def send_password_reset_email(user, token):
    """
    Send password reset link to user
    
    Args:
        user: User instance
        token: Reset token
    """
    subject = 'Reset your Stock Research Platform password'
    reset_url = f"{settings.SITE_URL}/auth/reset-password/{token}/"
    
    html_message = render_to_string('authentication/emails/password_reset_email.html', {
        'user': user,
        'reset_url': reset_url,
    })
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=html_message,
        fail_silently=False,
    )


def send_welcome_email(user):
    """
    Send welcome email to newly registered user
    
    Args:
        user: User instance
    """
    subject = 'Welcome to Stock Research Platform!'
    
    html_message = render_to_string('authentication/emails/welcome_email.html', {
        'user': user,
    })
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=html_message,
        fail_silently=False,
    )
