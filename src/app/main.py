"""
Entrypoint for the FastAPI application.

Description:
- Initializes the FastAPI app instance and mounts API routers.
- Registers global middleware, exception handlers, and startup/shutdown logic.

Connections:
- Imports endpoint modules from `api.v1.endpoints` (analyze, results, auth, feedback).
- Readings settings from `config.py`.

Notes:
- Run locally with `uvicorn src.app.main:app --reload`.
- For production, use a production server like Gunicorn behind a reverse proxy.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.v1.endpoints import analyze, results, auth, feedback
from app.db.session import engine
from app.models import db_models

# Initialize Database
# ------------------
# Creates tables automatically on startup for development convenience.
# In a real production environment, use Alembic migrations instead.
db_models.Base.metadata.create_all(bind=engine)

# App Initialization
# ------------------
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS Middleware Configuration
# -----------------------------
# Handles Cross-Origin Resource Sharing settings to allow frontend communication.
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    # Default permissive CORS for easier local development
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Router Registration
# -------------------
# Connects the API routes to the main application.
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(analyze.router, prefix=f"{settings.API_V1_STR}/analyze", tags=["analyze"])
app.include_router(results.router, prefix=f"{settings.API_V1_STR}/results", tags=["results"])
app.include_router(feedback.router, prefix=f"{settings.API_V1_STR}/feedback", tags=["feedback"])

@app.get("/")
def read_root():
    """Root endpoint to verify the API is running."""
    return {"message": "Welcome to SecretSense API"}

