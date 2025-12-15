"""
Configuration Settings (Pydantic BaseSettings).

Description:
- Loads configuration from environment variables (.env file).
- manages critical settings like DATABASE_URL, JWT_SECRET_KEY, and OPENAI_API_KEY.

Connections:
- Used by main.py, db/session.py, services/llm_client.py, and auth modules for settings.

Notes:
- Ensure `.env` file exists and contains the necessary secrets.
- Never commit actual secrets to version control.
"""

import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load Environment Variables
# --------------------------
# Reads the .env file and loads values into environment variables.
load_dotenv()

class Settings(BaseSettings):
    """
    Application Settings Class.
    Fields correlate to environment variable names (case-insensitive).
    """
    PROJECT_NAME: str = "SecretSense API"
    API_V1_STR: str = "/api/v1"
    
    # Database Configuration
    # ----------------------
    # Stores data in ./data/ directory to prevent auto-reloader loops generally caused by 
    # writing to the root directory during development.
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./data/secretsense.db")
    
    # Security Settings
    # -----------------
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "CHANGE_THIS_SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS (Cross-Origin Resource Sharing)
    # ------------------------------------
    BACKEND_CORS_ORIGINS: list[str] = ["*"]

    # AI/ML Configuration
    # -------------------
    # Key for accessing OpenAI's LLM for advanced verification.
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

    class Config:
        case_sensitive = True

# Global settings instance
settings = Settings()
