"""FastAPI application - OTP Microservice."""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.infrastructure.adapters.controllers.otp_controller import router as otp_router
from src.infrastructure.middleware.error_handler import register_exception_handlers
from src.infrastructure.adapters.db import DatabaseAdapter
from src.infrastructure.config import settings

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
    logger.info("🔢 OTP MICROSERVICE STARTING")
    logger.info("=" * 60)
    logger.info(f"Service: {settings.SERVICE_NAME}")
    logger.info(f"Port: {settings.SERVICE_PORT}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"OTP Expiry: {settings.OTP_EXPIRY_MINUTES} minutes")
    logger.info(f"Max Attempts: {settings.OTP_MAX_ATTEMPTS}")
    logger.info("=" * 60)
    
    # Initialize database
    try:
        logger.info("Initializing database connection...")
        DatabaseAdapter.initialize(
            database_url=settings.DATABASE_URL,
            echo=settings.ENVIRONMENT == "development",
            pool_size=settings.DATABASE_POOL_SIZE,
            max_overflow=settings.DATABASE_MAX_OVERFLOW,
            pool_pre_ping=settings.DATABASE_POOL_PRE_PING,
            timeout=settings.DATABASE_TIMEOUT,
        )
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("=" * 60)
    logger.info("OTP MICROSERVICE SHUTTING DOWN")
    logger.info("=" * 60)
    
    await DatabaseAdapter.close()


app = FastAPI(
    title="OTP Microservice",
    description=(
        "One-Time Password microservice for 2FA authentication. "
        "Generates and validates OTP codes with database persistence. "
        "Integrated with PostgreSQL for reliable OTP storage."
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
        "database": "postgresql",
    }


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "otp_microservice",
        "version": "1.0.0",
        "database": "connected",
    }


if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.getenv("SERVICE_PORT", "8003"))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)