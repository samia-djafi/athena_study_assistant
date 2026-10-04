"""
Application configuration for Athena AI/CS Study Assistant.
Provides environment-based configuration with sensible defaults for local development.
"""
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Athena AI/CS Study Assistant"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    DEBUG: bool = True
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "*"
    ]
    
    # LLM Settings
    GROQ_API_KEY: Optional[str] = None
    DEFAULT_MODEL: str = "openai/gpt-oss-120b"
    FALLBACK_MODEL: str = "qwen/qwen3.8-27b"
    TEMPERATURE: float = 0.2
    MAX_TOKENS: int = 4096
    
    # Search Settings
    TAVILY_API_KEY: Optional[str] = None
    USE_DDG_SEARCH: bool = True
    MAX_SEARCH_RESULTS: int = 5
    
    # Database
    DATABASE_URL: str = f"sqlite+aiosqlite:///{BASE_DIR / 'athena.db'}"
    SUPABASE_URL: Optional[str] = None
    SUPABASE_KEY: Optional[str] = None
    
    # Safety & Human In The Loop
    REQUIRE_APPROVAL_FOR_DESTRUCTIVE: bool = True
    MAX_CONVERSATION_TOKENS: int = 8000
    SUMMARY_THRESHOLD_TOKENS: int = 6000
    
    # Multimodal & Uploads
    MAX_UPLOAD_SIZE_MB: int = 15
    ALLOWED_IMAGE_TYPES: List[str] = ["image/jpeg", "image/png", "image/webp"]
    ALLOWED_DOC_TYPES: List[str] = ["application/pdf", "text/plain", "text/markdown"]
    
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
