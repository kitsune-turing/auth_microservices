"""Application Settings.

Configuration management using Pydantic Settings.
"""
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings."""
    
    # Service Configuration
    SERVICE_NAME: str = Field(default="Auth Microservice", description="Service name")
    ENVIRONMENT: str = Field(default="development", description="Environment (development/production)")
    SERVICE_PORT: int = Field(default=8001, description="Service port")
    SERVICE_HOST: str = Field(default="0.0.0.0", description="Service host")
    
    # JWT Configuration
    JWT_SECRET_KEY: str = Field(
        default="your-secret-key-change-in-production-min-32-characters",
        description="JWT secret key (min 32 characters)"
    )
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60, description="Access token expiration in minutes")
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, description="Refresh token expiration in days")
    
    # Microservices URLs
    USERS_SERVICE_URL: str = Field(
        default="http://users_microservice:8006",
        description="Users microservice URL"
    )
    USERS_SERVICE_TIMEOUT: int = Field(default=10, description="Users service timeout in seconds")
    OTP_SERVICE_URL: str = Field(
        default="http://otp_microservice:8003",
        description="OTP microservice URL"
    )
    OTP_SERVICE_TIMEOUT: int = Field(default=5, description="OTP service timeout in seconds")
    JANO_SERVICE_URL: str = Field(
        default="http://jano_microservice:8005",
        description="JANO security microservice URL"
    )
    JANO_SERVICE_TIMEOUT: int = Field(default=10, description="JANO service timeout in seconds")
    
    # CORS
    CORS_ORIGINS: list[str] = Field(
        default=["*"],
        description="Allowed CORS origins"
    )
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    
    # Database Configuration
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://admin:secure_password_123@auth_login_services_db:5432/auth_login_services",
        description="Database connection URL"
    )
    DATABASE_PASSWORD: str = Field(default="secure_password_123", description="Database password")
    DATABASE_POOL_SIZE: int = Field(default=10, description="Database connection pool size")
    DATABASE_MAX_OVERFLOW: int = Field(default=20, description="Database max overflow connections")
    DATABASE_POOL_PRE_PING: bool = Field(default=True, description="Test connections before using")
    DATABASE_TIMEOUT: int = Field(default=10, description="Database connection timeout in seconds")
    
    class Config:
        """Pydantic config."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Global settings instance
settings = Settings()


__all__ = ["settings", "Settings"]
