"""Configuration management for the Rizzard AI microservice."""

from functools import lru_cache

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables or .env file."""

    app_name: str = Field("Rizzard AI Microservice", env="APP_NAME")
    debug: bool = Field(False, env="DEBUG")
    claude_api_key: str | None = Field(None, env="CLAUDE_API")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Return a cached Settings instance."""
    return Settings()
