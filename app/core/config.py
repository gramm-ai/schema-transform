"""
Application configuration with type safety and validation
"""
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List


class Settings(BaseSettings):
    """
    Type-safe configuration with automatic validation
    Loads from environment variables and .env file
    """

    # Environment
    ENV: str = "development"
    DEBUG: bool = False

    # Azure OpenAI Configuration
    AZURE_OPENAI_API_KEY: str
    AZURE_OPENAI_ENDPOINT: str
    AZURE_OPENAI_DEPLOYMENT_NAME: str = "gpt-4"
    AZURE_OPENAI_API_VERSION: str = "2024-02-01"

    # Database Configuration
    AZURE_SQL_SERVER: str = ""
    AZURE_SQL_USERNAME: str = ""
    AZURE_SQL_PASSWORD: str = ""

    # Application Settings
    MAX_QUERY_RESULTS: int = 1000
    QUERY_TIMEOUT_SECONDS: int = 30
    ALLOWED_ORIGINS: str = "*"  # Comma-separated list

    # LLM Settings
    LLM_TEMPERATURE: float = 0.3
    LLM_MAX_TOKENS: int = 1000
    LLM_REQUEST_TIMEOUT: int = 30

    # Retry Configuration
    MAX_RETRY_ATTEMPTS: int = 3
    RETRY_MIN_WAIT_SECONDS: int = 2
    RETRY_MAX_WAIT_SECONDS: int = 10

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"

    def get_allowed_origins(self) -> List[str]:
        """Parse comma-separated CORS origins"""
        if self.ALLOWED_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    def validate_production_settings(self):
        """Additional validation for production environment"""
        if self.ENV == "production":
            if self.DEBUG:
                raise ValueError("DEBUG cannot be True in production")
            if self.ALLOWED_ORIGINS == "*":
                raise ValueError("ALLOWED_ORIGINS must be specific in production")
            if not self.AZURE_SQL_SERVER:
                raise ValueError("Database configuration required in production")


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance (singleton pattern)
    Cache ensures settings are loaded only once
    """
    settings = Settings()

    # Validate production settings
    if settings.ENV == "production":
        settings.validate_production_settings()

    return settings
