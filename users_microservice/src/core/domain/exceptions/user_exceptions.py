"""User Domain Exceptions.

Custom exceptions for the Users microservice with standardized error codes.
"""
from enum import Enum
from typing import Optional, Any


class UserErrorCode(str, Enum):
    """User error codes (USER_001-999)."""
    
    # Authentication errors (001-099)
    INVALID_CREDENTIALS = "USER_001"
    USER_NOT_FOUND = "USER_002"
    USER_INACTIVE = "USER_003"
    USER_DISABLED = "USER_004"
    
    # Validation errors (100-199)
    INVALID_USERNAME = "USER_100"
    INVALID_PASSWORD = "USER_101"
    INVALID_EMAIL = "USER_102"
    INVALID_ROLE = "USER_103"
    INVALID_TEAM = "USER_104"
    DUPLICATE_USERNAME = "USER_105"
    DUPLICATE_EMAIL = "USER_106"
    WEAK_PASSWORD = "USER_107"
    
    # Authorization errors (200-299)
    INSUFFICIENT_PERMISSIONS = "USER_200"
    ROLE_NOT_ALLOWED = "USER_201"
    TEAM_ACCESS_DENIED = "USER_202"
    
    # Resource errors (300-399)
    TEAM_NOT_FOUND = "USER_300"
    ROLE_NOT_FOUND = "USER_301"
    APPLICATION_NOT_FOUND = "USER_302"
    MODULE_NOT_FOUND = "USER_303"
    PERMISSION_NOT_FOUND = "USER_304"
    
    # Operation errors (400-499)
    CREATE_USER_FAILED = "USER_400"
    UPDATE_USER_FAILED = "USER_401"
    DELETE_USER_FAILED = "USER_402"
    DISABLE_USER_FAILED = "USER_403"
    ENABLE_USER_FAILED = "USER_404"
    
    # Database errors (500-599)
    DATABASE_ERROR = "USER_500"
    TRANSACTION_FAILED = "USER_501"
    CONSTRAINT_VIOLATION = "USER_502"
    
    # General errors (900-999)
    INTERNAL_ERROR = "USER_900"
    VALIDATION_ERROR = "USER_901"
    UNKNOWN_ERROR = "USER_999"


class UserException(Exception):
    """Base exception for user domain."""
    
    def __init__(
        self,
        code: UserErrorCode,
        message: str,
        details: Optional[dict[str, Any]] = None,
        status_code: int = 400,
    ):
        """
        Initialize user exception.
        
        Args:
            code: Error code from UserErrorCode enum
            message: Human-readable error message
            details: Optional additional error details
            status_code: HTTP status code
        """
        self.code = code
        self.message = message
        self.details = details or {}
        self.status_code = status_code
        super().__init__(message)


class InvalidCredentialsException(UserException):
    """Raised when user credentials are invalid."""
    
    def __init__(self, message: str = "Invalid username or password"):
        super().__init__(
            code=UserErrorCode.INVALID_CREDENTIALS,
            message=message,
            status_code=401,
        )


class UserNotFoundException(UserException):
    """Raised when user is not found."""
    
    def __init__(self, user_id: Optional[str] = None, username: Optional[str] = None):
        details = {}
        if user_id:
            details["user_id"] = user_id
        if username:
            details["username"] = username
            
        super().__init__(
            code=UserErrorCode.USER_NOT_FOUND,
            message="User not found",
            details=details,
            status_code=404,
        )


class UserInactiveException(UserException):
    """Raised when user is inactive."""
    
    def __init__(self, username: str):
        super().__init__(
            code=UserErrorCode.USER_INACTIVE,
            message="User account is inactive",
            details={"username": username},
            status_code=403,
        )


class DuplicateUsernameException(UserException):
    """Raised when username already exists."""
    
    def __init__(self, username: str):
        super().__init__(
            code=UserErrorCode.DUPLICATE_USERNAME,
            message=f"Username '{username}' already exists",
            details={"username": username},
            status_code=409,
        )


class DuplicateEmailException(UserException):
    """Raised when email already exists."""
    
    def __init__(self, email: str):
        super().__init__(
            code=UserErrorCode.DUPLICATE_EMAIL,
            message=f"Email '{email}' already exists",
            details={"email": email},
            status_code=409,
        )


class InvalidRoleException(UserException):
    """Raised when role is invalid."""
    
    def __init__(self, role: str):
        super().__init__(
            code=UserErrorCode.INVALID_ROLE,
            message=f"Invalid role: {role}",
            details={"role": role, "allowed_roles": ["root", "external", "user_siata"]},
            status_code=400,
        )


class InsufficientPermissionsException(UserException):
    """Raised when user doesn't have required permissions."""
    
    def __init__(self, required_permission: str, user_role: str):
        super().__init__(
            code=UserErrorCode.INSUFFICIENT_PERMISSIONS,
            message="Insufficient permissions to perform this action",
            details={
                "required_permission": required_permission,
                "user_role": user_role,
            },
            status_code=403,
        )


class TeamNotFoundException(UserException):
    """Raised when team is not found."""
    
    def __init__(self, team_name: str):
        super().__init__(
            code=UserErrorCode.TEAM_NOT_FOUND,
            message=f"Team '{team_name}' not found",
            details={"team_name": team_name},
            status_code=404,
        )


class DatabaseException(UserException):
    """Raised when database operation fails."""
    
    def __init__(self, operation: str, error: str):
        super().__init__(
            code=UserErrorCode.DATABASE_ERROR,
            message="Database operation failed",
            details={"operation": operation, "error": error},
            status_code=500,
        )


class WeakPasswordException(UserException):
    """Raised when password doesn't meet security requirements."""
    
    def __init__(self):
        super().__init__(
            code=UserErrorCode.WEAK_PASSWORD,
            message="Password does not meet security requirements",
            details={
                "requirements": {
                    "min_length": 8,
                    "must_contain": "letters and numbers",
                }
            },
            status_code=400,
        )


__all__ = [
    "UserErrorCode",
    "UserException",
    "InvalidCredentialsException",
    "UserNotFoundException",
    "UserInactiveException",
    "DuplicateUsernameException",
    "DuplicateEmailException",
    "InvalidRoleException",
    "InsufficientPermissionsException",
    "TeamNotFoundException",
    "DatabaseException",
    "WeakPasswordException",
]
