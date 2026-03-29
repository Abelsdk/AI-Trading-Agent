# src/core/config.py
# This module reads environment variables from .env and exposes them
# as a typed settings object. Every other module imports from here —
# nothing reads .env directly except this file.

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Application
    app_name: str = "AI Trading Agent"
    environment: str = "development"
    secret_key: str = "dev-secret-key"

    # Database
    database_url: str

    # Redis
    redis_url: str = "redis://localhost:6379"

    class Config:
        # Tells Pydantic to read from the .env file
        env_file = ".env"
        case_sensitive = False


# lru_cache means this only runs once — settings are created once
# and reused everywhere. Efficient and clean.
@lru_cache()
def get_settings() -> Settings:
    return Settings()


# Convenience — other files do: from src.core.config import settings
settings = get_settings()