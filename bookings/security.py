"""
Security utilities for authentication and validation.
"""
import re
import logging
from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.response import Response

logger = logging.getLogger('office_booking')


class PasswordValidator:
    """Validates password requirements: min 8 chars, digit, special char."""
    
    MIN_LENGTH = 8
    SPECIAL_CHARS = r'[!@#$%^&*()_+\-=\[\]{};:\'",.<>?/\\|`~]'
    
    @classmethod
    def validate(cls, password):
        """
        Validate password strength.
        
        Args:
            password (str): Password to validate
            
        Returns:
            tuple: (is_valid, error_message)
        """
        if not password or len(password) < cls.MIN_LENGTH:
            return False, f"Пароль має бути мінімум {cls.MIN_LENGTH} символів"
        
        if not re.search(r'\d', password):
            return False, "Пароль має містити мінімум одну цифру (0-9)"
        
        if not re.search(cls.SPECIAL_CHARS, password):
            return False, "Пароль має містити мінімум один спеціальний символ (!@#$%^&* тощо)"
        
        return True, None


class EmailValidator:
    """Validates email format."""
    
    EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    @classmethod
    def validate(cls, email):
        """
        Validate email format.
        
        Args:
            email (str): Email to validate
            
        Returns:
            tuple: (is_valid, error_message)
        """
        if not email:
            return False, "Email не може бути порожним"
        
        if not re.match(cls.EMAIL_REGEX, email):
            return False, "Невірний формат email адреси"
        
        if len(email) > 254:
            return False, "Email занадто довгий (макс 254 символи)"
        
        return True, None


class SecurityLogger:
    """Log security-related events."""
    
    @staticmethod
    def log_registration_attempt(username, success, reason=None):
        """Log registration attempt."""
        if success:
            logger.info(f"Registration success: {username}")
        else:
            logger.warning(f"Registration failed for {username}: {reason}")
    
    @staticmethod
    def log_login_attempt(username, success, ip_address=None):
        """Log login attempt."""
        if success:
            logger.info(f"Login success: {username} from {ip_address}")
        else:
            logger.warning(f"Login failed for {username} from {ip_address}")
    
    @staticmethod
    def log_auth_error(error_type, details, ip_address=None):
        """Log authentication errors."""
        logger.error(f"Auth error [{error_type}] from {ip_address}: {details}")


class SecurityException(Exception):
    """Base security exception."""
    pass


class InvalidPasswordException(SecurityException):
    """Raised when password doesn't meet requirements."""
    pass


class InvalidEmailException(SecurityException):
    """Raised when email format is invalid."""
    pass


class DuplicateUserException(SecurityException):
    """Raised when user already exists."""
    pass


def get_client_ip(request):
    """
    Get client IP address from request.

    Takes the LAST value from X-Forwarded-For — this is the address
    added by the last trusted proxy (e.g. nginx/load balancer),
    and cannot be forged by the client.

    If X-Forwarded-For is absent, falls back to REMOTE_ADDR.

    Args:
        request: Django HTTP request

    Returns:
        str: Client IP address (stripped)
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        # Last entry = set by the last (trusted) proxy, not the client
        ip = x_forwarded_for.split(',')[-1].strip()
    else:
        ip = request.META.get('REMOTE_ADDR', '')
    return ip