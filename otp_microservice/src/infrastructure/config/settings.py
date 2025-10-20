"""Configuration settings for OTP Microservice."""
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
import json


class Settings(BaseSettings):
    """Application settings."""
    
    # Service Configuration
    SERVICE_NAME: str = Field(default="OTP Microservice", description="Service name")
    ENVIRONMENT: str = Field(default="development", description="Environment")
    SERVICE_PORT: int = Field(default=8003, description="Service port")
    SERVICE_HOST: str = Field(default="0.0.0.0", description="Service host")
    
    # Database Configuration
    DATABASE_USER: str = Field(default="otp_service", description="Database username")
    DATABASE_PASSWORD: str = Field(default="", description="Database password (set via env or .env, DO NOT commit)")
    DATABASE_HOST: str = Field(default="postgres", description="Database host")
    DATABASE_PORT: int = Field(default=5432, description="Database port")
    DATABASE_NAME: str = Field(default="auth_login_services", description="Database name")

    DATABASE_URL: str = Field(
        default="",
        description="Database connection URL; if empty it will be constructed from components above"
    )

    @field_validator("DATABASE_URL", mode="after")
    def _assemble_database_url(cls, v, info):
        """
        Assemble DATABASE_URL from components when DATABASE_URL is not provided directly.
        This ensures the password is sourced from environment variables rather than hard-coded.
        """
        if v:
            return v
        data = info.data or {}
        user = data.get("DATABASE_USER", "otp_service")
        password = data.get("DATABASE_PASSWORD", "")
        host = data.get("DATABASE_HOST", "postgres")
        port = data.get("DATABASE_PORT", 5432)
        name = data.get("DATABASE_NAME", "auth_login_services")

        if not password:
            raise ValueError(
                "DATABASE_PASSWORD must be set in the environment or .env for a secure database connection"
            )
        return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{name}"

    DATABASE_POOL_SIZE: int = Field(default=5, description="Database pool size")
    DATABASE_MAX_OVERFLOW: int = Field(default=10, description="Database max overflow")
    DATABASE_POOL_PRE_PING: bool = Field(default=True, description="Test connections")
    DATABASE_TIMEOUT: int = Field(default=10, description="Database timeout")
    
    # OTP Configuration
    OTP_EXPIRY_MINUTES: int = Field(default=5, description="OTP expiration in minutes")
    OTP_MAX_ATTEMPTS: int = Field(default=3, description="Maximum validation attempts")
    OTP_CODE_LENGTH: int = Field(default=6, description="OTP code length")
    
    # Email Configuration (for future implementation)
    SMTP_HOST: str = Field(default="smtp.gmail.com", description="SMTP host")
    SMTP_PORT: int = Field(default=587, description="SMTP port")
    SMTP_USER: str = Field(default="", description="SMTP username")
    SMTP_PASSWORD: str = Field(default="", description="SMTP password")
    SMTP_FROM: str = Field(default="noreply@siata.gov.co", description="From email")
    SMTP_FROM_NAME: str = Field(default="SIATA Security", description="From name")
    
    # SMS Configuration (for future implementation)
    SMS_PROVIDER: str = Field(default="twilio", description="SMS provider")
    SMS_ACCOUNT_SID: str = Field(default="", description="SMS account SID")
    SMS_AUTH_TOKEN: str = Field(default="", description="SMS auth token")
    SMS_FROM_NUMBER: str = Field(default="", description="SMS from number")
    
    # Development Settings
    DEV_SHOW_OTP_IN_RESPONSE: bool = Field(
        default=True,
        description="Show OTP code in response (development only)"
    )
    DEV_SKIP_EMAIL: bool = Field(
        default=True,
        description="Skip email sending (development only)"
    )
    
    # CORS
    CORS_ORIGINS: str = Field(
        default="*",
        description="Allowed CORS origins (comma-separated or JSON list)"
    )
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    
    class Config:
        """Pydantic config."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"
    
    def get_cors_origins(self) -> list[str]:
        """Get CORS origins as list."""
        if isinstance(self.CORS_ORIGINS, list):
            return self.CORS_ORIGINS
        if self.CORS_ORIGINS == "*":
            return ["*"]
        try:
            return json.loads(self.CORS_ORIGINS)
        except (json.JSONDecodeError, TypeError):
            return [o.strip() for o in self.CORS_ORIGINS.split(",")]


# Global settings instance
settings = Settings()


__all__ = ["settings", "Settings"]


