"""Application settings loaded from environment / .env file.

Every service imports `get_settings()` — one source of truth for config.
"""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Typed application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # ignore unrelated env vars
    )

    # App
    env: str = "dev"
    log_level: str = "INFO"

    # LLM
    openai_api_key: str = ""
    llm_model: str = "gpt-4o-mini"

    # Databases
    postgres_url: str = "postgresql://postgres:postgres@localhost:5432/docintel"
    redis_url: str = "redis://localhost:6379/0"
    weaviate_url: str = "http://localhost:8080"

    # Storage
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance."""
    return Settings()