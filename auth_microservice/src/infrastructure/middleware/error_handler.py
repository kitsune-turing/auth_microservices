"""Global Exception Handler for FastAPI.

Centralizes error handling and provides standardized error responses.
"""
import logging
from datetime import datetime
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from src.domain.exceptions import AuthException, AuthErrorCode
from src.application.dtos import ErrorResponse, ErrorDetail

logger = logging.getLogger(__name__)


async def auth_exception_handler(request: Request, exc: AuthException) -> JSONResponse:
    """
    Handle auth domain exceptions.
    
    Args:
        request: FastAPI request
        exc: Auth exception
        
    Returns:
        JSON response with error details
    """
    logger.warning(f"Auth exception: {exc.code} - {exc.message} - Path: {request.url.path}")
    
    error_response = ErrorResponse(
        error=ErrorDetail(
            code=exc.code,
            message=exc.message,
            details=exc.details,
            timestamp=datetime.utcnow(),
            path=str(request.url.path),
        )
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump(mode='json'),
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """
    Handle validation errors.
    
    Args:
        request: FastAPI request
        exc: Validation error
        
    Returns:
        JSON response with validation error details
    """
    logger.warning(f"Validation error: {exc.errors()} - Path: {request.url.path}")
    
    error_response = ErrorResponse(
        error=ErrorDetail(
            code=AuthErrorCode.VALIDATION_ERROR,
            message="Validation error",
            details=str(exc.errors()),
            timestamp=datetime.utcnow(),
            path=str(request.url.path),
        )
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response.model_dump(mode='json'),
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle general exceptions.
    
    Args:
        request: FastAPI request
        exc: Exception
        
    Returns:
        JSON response with error details
    """
    logger.error(f"Unhandled exception: {exc} - Path: {request.url.path}", exc_info=True)
    
    error_response = ErrorResponse(
        error=ErrorDetail(
            code=AuthErrorCode.INTERNAL_ERROR,
            message="Internal server error",
            details=str(exc) if logger.level == logging.DEBUG else "An unexpected error occurred",
            timestamp=datetime.utcnow(),
            path=str(request.url.path),
        )
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response.model_dump(mode='json'),
    )


def register_exception_handlers(app):
    """
    Register all exception handlers to FastAPI app.
    
    Args:
        app: FastAPI application instance
    """
    app.add_exception_handler(AuthException, auth_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
    
    logger.info("Exception handlers registered")


__all__ = [
    "auth_exception_handler",
    "validation_exception_handler",
    "general_exception_handler",
    "register_exception_handlers",
]
