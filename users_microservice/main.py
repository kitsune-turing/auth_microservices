"""FastAPI application entry point - Users Microservice."""
import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.infrastructure.db.database import setup_database, close_database
from src.infrastructure.adapters.controllers import user_controller, internal_controller
from src.infrastructure.middleware import register_exception_handlers, AuthMiddleware
import src.infrastructure.middleware.auth_middleware as auth_middleware_module
import src.infrastructure.adapters.jano_client as jano_client_module
from src.infrastructure.adapters.jano_client import JANOClient

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    logger.info("Starting Users Microservice...")
    
    # Initialize database
    await setup_database()
    logger.info("Database initialized successfully")
    
    # Initialize auth middleware
    auth_service_url = os.getenv("AUTH_SERVICE_URL", "http://auth_microservice:8001")
    auth_middleware_module.auth_middleware = AuthMiddleware(auth_service_url)
    logger.info(f"Auth middleware initialized with URL: {auth_service_url}")
    
    # Initialize JANO client
    jano_service_url = os.getenv("JANO_SERVICE_URL", "http://jano_microservice:8005")
    jano_client_module.jano_client = JANOClient(
        base_url=jano_service_url,
        timeout=5.0,
        application_id="users_service"
    )
    logger.info(f"JANO client initialized with URL: {jano_service_url}")
    
    # Check JANO availability
    jano_healthy = await jano_client_module.jano_client.health_check()
    if jano_healthy:
        logger.info("✅ JANO service is available")
    else:
        logger.warning("⚠️  JANO service is not available - password validation may fail")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Users Microservice...")
    
    # Close JANO client
    if jano_client_module.jano_client:
        await jano_client_module.jano_client.close()
        logger.info("JANO client closed")
    
    # Close database
    await close_database()
    logger.info("Database connections closed")


# Create FastAPI app
app = FastAPI(
    title="Users Microservice",
    description="Microservicio de gestión de usuarios - Hexagonal Architecture",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register global exception handlers
register_exception_handlers(app)

# Include routers
app.include_router(user_controller.router)  # ROOT-protected endpoints
app.include_router(internal_controller.router)  # Internal inter-service endpoints


@app.get("/health")
async def health():
    """Detailed health check."""
    return {
        "service": "Users Microservice",
        "status": "healthy",
        "description": "User CRUD operations - ROOT only",
        "endpoints": {
            "create_user": "POST /api/users (ROOT only)",
            "get_user": "GET /api/users/{user_id} (ROOT only)",
            "update_user": "PUT /api/users/{user_id} (ROOT only)",
            "disable_user": "PATCH /api/users/{user_id}/disable (ROOT only)",
            "enable_user": "PATCH /api/users/{user_id}/enable (ROOT only)",
        },
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8006,
        reload=True,
        log_level="info",
    )
