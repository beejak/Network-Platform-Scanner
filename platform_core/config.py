"""
Centralized configuration management for the platform.

This module uses Pydantic's BaseSettings to load configuration from
environment variables, providing a single source of truth for all settings.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """
    Defines the application's configuration settings.
    Settings are loaded from environment variables.
    """
    # PostgreSQL Database
    POSTGRES_USER: str = "jules"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "test"

    # Neo4j Database
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "password"

    # RabbitMQ
    RABBITMQ_URL: str = "amqp://guest:guest@localhost:5672/"

    # NetBox Integration
    NETBOX_URL: str = "http://localhost:8000"
    NETBOX_TOKEN: str = "your-netbox-api-token"

    # JWT Authentication
    JWT_SECRET_KEY: str = "your-super-secret-key"
    JWT_ALGORITHM: str = "HS256"

    @property
    def postgres_dsn(self) -> str:
        """Asynchronous PostgreSQL connection string."""
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache()
def get_settings() -> Settings:
    """
    Returns the cached settings instance.
    The lru_cache decorator ensures that the Settings object is created only once.
    """
    return Settings()
