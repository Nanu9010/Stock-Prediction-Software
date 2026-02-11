"""
Custom validators for data validation
"""
import re
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator


def validate_symbol(value):
    """
    Validate stock symbol (alphanumeric only, uppercase)
    """
    if not value.isalnum():
        raise ValidationError('Symbol must be alphanumeric (letters and numbers only)')
    
    if len(value) < 2 or len(value) > 20:
        raise ValidationError('Symbol must be between 2 and 20 characters')
    
    return value.upper()


def validate_mobile(value):
    """
    Validate Indian mobile number (10 digits)
    """
    if not value.isdigit():
        raise ValidationError('Mobile number must contain only digits')
    
    if len(value) != 10:
        raise ValidationError('Mobile number must be exactly 10 digits')
    
    if not value.startswith(('6', '7', '8', '9')):
        raise ValidationError('Mobile number must start with 6, 7, 8, or 9')
    
    return value


class PasswordComplexityValidator:
    """
    Custom password validator requiring:
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    """
    
    def validate(self, password, user=None):
        if not re.search(r'[A-Z]', password):
            raise ValidationError(
                'Password must contain at least one uppercase letter',
                code='password_no_upper',
            )
        
        if not re.search(r'[a-z]', password):
            raise ValidationError(
                'Password must contain at least one lowercase letter',
                code='password_no_lower',
            )
        
        if not re.search(r'\d', password):
            raise ValidationError(
                'Password must contain at least one digit',
                code='password_no_digit',
            )
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError(
                'Password must contain at least one special character (!@#$%^&*)',
                code='password_no_special',
            )
    
    def get_help_text(self):
        return (
            'Your password must contain at least one uppercase letter, '
            'one lowercase letter, one digit, and one special character.'
        )


# Regex validators for common patterns
sebi_registration_validator = RegexValidator(
    regex=r'^[A-Z]{3}\d{6}$',
    message='SEBI registration number must be in format: ABC123456 (3 letters + 6 digits)',
    code='invalid_sebi_registration'
)

pan_validator = RegexValidator(
    regex=r'^[A-Z]{5}\d{4}[A-Z]$',
    message='PAN must be in format: ABCDE1234F (5 letters + 4 digits + 1 letter)',
    code='invalid_pan'
)
