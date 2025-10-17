"""Middleware package."""

from .error_handler import (
    ErrorDetail,
    ErrorResponse,
    register_exception_handlers,
)
from .auth_middleware import (
    AuthMiddleware,
    require_root_role,
    get_auth_middleware,
)

__all__ = [
    "ErrorDetail",
    "ErrorResponse",
    "register_exception_handlers",
    "AuthMiddleware",
    "require_root_role",
    "get_auth_middleware",
]
