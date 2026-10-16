"""Application settings loaded from environment / .env file."""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    env: str = "dev"
    log_level: str = "INFO"

    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"

    openai_api_key: str = ""
    llm_model: str = "gpt-4o-mini"

    postgres_url: str = "postgresql://postgres:postgres@postgres:5432/docintel"
    redis_url: str = "redis://localhost:6379/0"
    weaviate_url: str = "http://weaviate:8080"

    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"


@lru_cache
def get_settings() -> Settings:
    return Settings()
