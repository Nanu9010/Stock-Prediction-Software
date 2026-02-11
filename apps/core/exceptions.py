"""
Custom exceptions for the Stock Research Platform
"""


class InsufficientPermissionError(Exception):
    """Raised when user doesn't have permission for an action"""
    pass


class InvalidCallStateError(Exception):
    """Raised when trying to perform invalid state transition"""
    pass


class PortfolioError(Exception):
    """Base exception for portfolio-related errors"""
    pass


class DuplicatePortfolioItemError(PortfolioError):
    """Raised when trying to add duplicate item to portfolio"""
    pass


class InvalidPriceError(Exception):
    """Raised when price validation fails"""
    pass


class SubscriptionError(Exception):
    """Base exception for subscription-related errors"""
    pass


class InsufficientSubscriptionError(SubscriptionError):
    """Raised when user's subscription doesn't allow access"""
    pass
