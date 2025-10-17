"""Domain exceptions - errores de negocio."""


class DomainException(Exception):
    """Excepción base de dominio."""
    pass


class UserNotFoundError(DomainException):
    """Usuario no encontrado."""
    pass


class UserAlreadyExistsError(DomainException):
    """Usuario ya existe."""
    pass


class InvalidEmailError(DomainException):
    """Email inválido."""
    pass


class InvalidPasswordError(DomainException):
    """Contraseña no cumple requisitos."""
    pass


class ApplicationNotFoundError(DomainException):
    """Aplicación no encontrada."""
    pass


class ApplicationAlreadyExistsError(DomainException):
    """Aplicación ya existe."""
    pass


class ModuleNotFoundError(DomainException):
    """Módulo no encontrado."""
    pass


class AccessControlNotFoundError(DomainException):
    """Control de acceso no encontrado."""
    pass


# Import new standardized exceptions
from .user_exceptions import (
    UserErrorCode,
    UserException,
    InvalidCredentialsException,
    UserNotFoundException,
    UserInactiveException,
    DuplicateUsernameException,
    DuplicateEmailException,
    InvalidRoleException,
    InsufficientPermissionsException,
    TeamNotFoundException,
    DatabaseException,
    WeakPasswordException,
)

__all__ = [
    # Legacy exceptions
    "DomainException",
    "UserNotFoundError",
    "ApplicationNotFoundError",
    "ModuleNotFoundError",
    "AccessControlNotFoundError",
    # New standardized exceptions
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
