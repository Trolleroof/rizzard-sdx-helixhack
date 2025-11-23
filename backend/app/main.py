"""Application entrypoint for the Rizzard AI FastAPI microservice."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from typing import Optional

from .config import Settings, get_settings
from .routers import email, embed, process_profile, project, score


def create_app(settings: Optional[Settings] = None) -> FastAPI:
    """Application factory used by both local development and production."""
    app_settings = settings or get_settings()

    app = FastAPI(
        title="Rizzard AI Microservice",
        description="FastAPI microservice powering AI/ML features for Rizzard",
        version="0.1.0",
    )

    # Add CORS middleware to allow frontend to call backend
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://localhost:3001"],  # Next.js default ports
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Attach configuration for runtime access if needed.
    app.state.settings = app_settings

    # Register API routers.
    app.include_router(embed.router)
    app.include_router(score.router)
    app.include_router(email.router)
    app.include_router(project.router)
    app.include_router(process_profile.router)

    return app


app = create_app()
