"""FastAPI application - OTP Microservice."""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.infrastructure.adapters.controllers.otp_controller import router as otp_router
from src.infrastructure.middleware.error_handler import register_exception_handlers

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager."""
    logger.info("=" * 60)
    logger.info("🔢 OTP MICROSERVICE STARTING (MOCK MODE)")
    logger.info("=" * 60)
    logger.info("Service: OTP Microservice")
    logger.info("Port: 8003")
    logger.info("Mode: Development (Mock Implementation)")
    logger.info("=" * 60)
    
    yield
    
    logger.info("=" * 60)
    logger.info("🛑 OTP MICROSERVICE SHUTTING DOWN")
    logger.info("=" * 60)


app = FastAPI(
    title="OTP Microservice",
    description=(
        "One-Time Password microservice for 2FA authentication. "
        "**Mock Implementation** - Generates and validates OTP codes. "
        "Prepared for future production implementation with email/SMS delivery."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register global exception handlers
register_exception_handlers(app)

# Include routers
app.include_router(otp_router, prefix="/api")


@app.get("/", tags=["health"])
async def root():
    """Root endpoint."""
    return {
        "service": "OTP Microservice",
        "version": "1.0.0",
        "status": "running",
        "mode": "mock",
    }


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "OTP Microservice",
        "version": "1.0.0",
    }


if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.getenv("SERVICE_PORT", "8003"))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)