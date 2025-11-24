"""Configuration management for the Rizzard AI microservice."""

import os
import logging
from functools import lru_cache
from pathlib import Path
from typing import Optional

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

# Verify API keys are loaded
env_claude_key = os.getenv("CLAUDE_API")
if env_claude_key:
    logger.info(f"CLAUDE_API found in environment: {env_claude_key[:10]}...")
else:
    logger.warning("CLAUDE_API NOT found in environment after load_dotenv")

env_firecrawl_key = os.getenv("FIRECRAWL_API")
if env_firecrawl_key:
    logger.info("FIRECRAWL_API found in environment.")
else:
    logger.debug("FIRECRAWL_API not set in environment.")


class Settings(BaseSettings):
    """Application settings loaded from environment variables or .env file."""

    app_name: str = Field("Rizzard AI Microservice", env="APP_NAME")
    debug: bool = Field(False, env="DEBUG")
    claude_api_key: Optional[str] = Field(None, env="CLAUDE_API")
    claude_model: str = Field("claude-3-haiku-20240307", env="CLAUDE_MODEL")
    firecrawl_api_key: Optional[str] = Field(None, env="FIRECRAWL_API")
    embedding_model_name: str = Field(
        "sentence-transformers/all-MiniLM-L6-v2",
        env="EMBEDDING_MODEL_NAME",
    )
    helixdb_local: bool = Field(True, env="HELIXDB_LOCAL")
    helixdb_verbose: bool = Field(False, env="HELIXDB_VERBOSE")
    helixdb_endpoint: Optional[str] = Field(None, env="HELIXDB_ENDPOINT")
    helixdb_api_key: Optional[str] = Field(None, env="HELIXDB_API_KEY")

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

    if not settings.firecrawl_api_key:
        env_firecrawl = os.getenv("FIRECRAWL_API")
        if env_firecrawl:
            settings.firecrawl_api_key = env_firecrawl
            logger.info("Firecrawl API key loaded via fallback environment lookup.")

    if not settings.embedding_model_name:
        env_embedding = os.getenv("EMBEDDING_MODEL_NAME")
        if env_embedding:
            settings.embedding_model_name = env_embedding
            logger.info("Embedding model name loaded via fallback environment lookup.")

    return settings
