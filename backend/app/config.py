"""Configuration management for the Rizzard AI microservice."""

import os
import logging
from functools import lru_cache
from pathlib import Path

try:
    from pydantic_settings import BaseSettings
except ImportError:
    # Fallback for older pydantic versions
    from pydantic import BaseSettings

from pydantic import Field

# Try to load .env file explicitly with python-dotenv if available
try:
    from dotenv import load_dotenv
    # Get the backend directory (parent of app directory)
    BACKEND_DIR = Path(__file__).parent.parent
    ENV_FILE = BACKEND_DIR / ".env"
    if ENV_FILE.exists():
        load_dotenv(ENV_FILE, override=True)  # Add override=True to ensure it overwrites
        print(f"✓ Loaded .env file from: {ENV_FILE}")  # Use print for visibility during startup
except ImportError:
    # python-dotenv not installed, will rely on Pydantic's built-in .env loading
    BACKEND_DIR = Path(__file__).parent.parent
    ENV_FILE = BACKEND_DIR / ".env"

logger = logging.getLogger(__name__)

# Log the .env file path for debugging
logger.info(f"Looking for .env file at: {ENV_FILE}")
if ENV_FILE.exists():
    logger.info(f".env file found at: {ENV_FILE}")
else:
    logger.warning(f".env file NOT found at: {ENV_FILE}")

# Verify API key is loaded
env_key_check = os.getenv("CLAUDE_API")
if env_key_check:
    logger.info(f"CLAUDE_API found in environment: {env_key_check[:10]}...")
else:
    logger.warning("CLAUDE_API NOT found in environment after load_dotenv")


class Settings(BaseSettings):
    """Application settings loaded from environment variables or .env file."""

    app_name: str = Field("Rizzard AI Microservice", env="APP_NAME")
    debug: bool = Field(False, env="DEBUG")
    claude_api_key: str | None = Field(None, env="CLAUDE_API")

    class Config:
        env_file = str(ENV_FILE) if ENV_FILE.exists() else ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields from .env that don't match model fields


@lru_cache()
def get_settings() -> Settings:
    """Return a cached Settings instance."""
    settings = Settings()
    
    # Fallback: if Pydantic didn't load it, try os.getenv directly
    if not settings.claude_api_key:
        env_key = os.getenv("CLAUDE_API")
        if env_key:
            # Manually set it if found in environment
            settings.claude_api_key = env_key
            logger.info(f"Claude API key loaded via fallback: {env_key[:10]}...")
    
    # Log whether API key was loaded (without exposing the full key)
    if settings.claude_api_key:
        logger.info(f"Claude API key loaded: {settings.claude_api_key[:10]}...")
    else:
        logger.warning("Claude API key NOT loaded from .env file or environment")
        # Also check environment variable directly
        env_key = os.getenv("CLAUDE_API")
        if env_key:
            logger.info("CLAUDE_API found in environment variables")
        else:
            logger.warning("CLAUDE_API not found in environment variables either")
    return settings
