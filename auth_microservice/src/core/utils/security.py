"""Security utilities for authentication microservice.

Provides helper functions for token hashing, log sanitization, and other security operations.
"""
import hashlib
import re
from typing import Any, Dict


def hash_token(token: str) -> str:
    """
    Generate SHA-256 hash of a token for secure storage.
    
    Args:
        token: JWT token string
        
    Returns:
        SHA-256 hash of the token in hexadecimal format
    """
    return hashlib.sha256(token.encode('utf-8')).hexdigest()


def sanitize_email_for_log(email: str) -> str:
    """
    Mask email for logging purposes.
    
    Args:
        email: Email address to sanitize
        
    Returns:
        Masked email address
        
    Example:
        'user@example.com' -> 'u***r@example.com'
    """
    if '@' not in email:
        return '***'
    
    local, domain = email.split('@', 1)
    if len(local) <= 2:
        masked_local = local[0] + '*'
    else:
        masked_local = local[0] + '*' * (len(local) - 2) + local[-1]
    
    return f"{masked_local}@{domain}"


def sanitize_username_for_log(username: str) -> str:
    """
    Mask username for logging purposes.
    
    Args:
        username: Username to sanitize
        
    Returns:
        Masked username
        
    Example:
        'admin123' -> 'ad***23'
    """
    if len(username) <= 3:
        return '*' * len(username)
    
    return username[:2] + '*' * (len(username) - 4) + username[-2:]


def sanitize_user_id(user_id: str) -> str:
    """
    Mask user ID for logging purposes.
    
    Args:
        user_id: User ID (UUID) to sanitize
        
    Returns:
        Partially masked user ID
        
    Example:
        '129fce00-b477-4cfe-9fc9-35391db39672' -> '129fce00-****-****-****-35391db39672'
    """
    # Preserve first and last segments of UUID
    parts = user_id.split('-')
    if len(parts) == 5:
        return f"{parts[0]}-****-****-****-{parts[-1]}"
    return '****-****-****-****'


def sanitize_log_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize sensitive data in dictionaries for logging.
    
    Args:
        data: Dictionary potentially containing sensitive data
        
    Returns:
        Dictionary with sensitive fields masked
    """
    sanitized = data.copy()
    
    # Fields to sanitize
    sensitive_fields = {
        'email': sanitize_email_for_log,
        'username': sanitize_username_for_log,
        'user_id': sanitize_user_id,
        'password': lambda x: '********',
        'token': lambda x: x[:10] + '...' if len(x) > 10 else '***',
        'access_token': lambda x: x[:10] + '...' if len(x) > 10 else '***',
        'refresh_token': lambda x: x[:10] + '...' if len(x) > 10 else '***',
        'otp_code': lambda x: '******',
    }
    
    for field, sanitizer in sensitive_fields.items():
        if field in sanitized and sanitized[field]:
            sanitized[field] = sanitizer(str(sanitized[field]))
    
    return sanitized


def validate_jti_format(jti: str) -> bool:
    """
    Validate JWT ID (jti) format.
    
    Args:
        jti: JWT ID to validate
        
    Returns:
        True if jti is a valid UUID format
    """
    uuid_pattern = re.compile(
        r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
        re.IGNORECASE
    )
    return bool(uuid_pattern.match(jti))


__all__ = [
    'hash_token',
    'sanitize_email_for_log',
    'sanitize_username_for_log',
    'sanitize_user_id',
    'sanitize_log_data',
    'validate_jti_format',
]
