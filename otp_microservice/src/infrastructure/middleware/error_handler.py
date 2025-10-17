"""Global Error Handler for OTP Microservice."""
import logging
from datetime import datetime, UTC
from typing import Union

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field

from src.core.domain.exceptions import OTPException

logger = logging.getLogger(__name__)


class ErrorDetail(BaseModel):
    """Error detail information."""
    field: str
    message: str
    type: str


class ErrorResponse(BaseModel):
    """Standardized error response."""
    
    class ErrorInfo(BaseModel):
        """Error information."""
        code: str = Field(..., description="Error code (OTP_XXX)")
        message: str = Field(..., description="Human-readable error message")
        details: Union[dict, list[ErrorDetail], None] = Field(
            default=None,
            description="Additional error details"
        )
        timestamp: str = Field(..., description="Error timestamp (ISO 8601)")
        path: str = Field(..., description="Request path that caused the error")
    
    error: ErrorInfo


async def otp_exception_handler(request: Request, exc: OTPException) -> JSONResponse:
    """Handle OTP exceptions."""
    logger.warning(
        f"OTP exception: {exc.code} - {exc.message}",
        extra={"code": exc.code, "path": request.url.path, "details": exc.details}
    )
    
    error_response = ErrorResponse(
        error=ErrorResponse.ErrorInfo(
            code=exc.code,
            message=exc.message,
            details=exc.details if exc.details else None,
            timestamp=datetime.now(UTC).isoformat(),
            path=request.url.path,
        )
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump(),
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
) -> JSONResponse:
    """Handle Pydantic validation errors."""
    logger.warning(
        f"Validation error on {request.url.path}",
        extra={"errors": exc.errors()}
    )
    
    error_details = [
        ErrorDetail(
            field=".".join(str(loc) for loc in error["loc"]),
            message=error["msg"],
            type=error["type"],
        )
        for error in exc.errors()
    ]
    
    error_response = ErrorResponse(
        error=ErrorResponse.ErrorInfo(
            code="OTP_901",
            message="Validation error",
            details=[detail.model_dump() for detail in error_details],
            timestamp=datetime.now(UTC).isoformat(),
            path=request.url.path,
        )
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response.model_dump(),
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions."""
    logger.error(
        f"Unexpected error on {request.url.path}: {str(exc)}",
        exc_info=True,
        extra={"path": request.url.path}
    )
    
    error_response = ErrorResponse(
        error=ErrorResponse.ErrorInfo(
            code="OTP_900",
            message="Internal server error",
            details={"type": type(exc).__name__},
            timestamp=datetime.now(UTC).isoformat(),
            path=request.url.path,
        )
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response.model_dump(),
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Register all exception handlers."""
    app.add_exception_handler(OTPException, otp_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
    
    logger.info("Exception handlers registered for OTP Microservice")


__all__ = ["ErrorDetail", "ErrorResponse", "register_exception_handlers"]
