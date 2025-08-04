"""
NewSystem.AI Configuration
Handles all environment variables and settings for the application
"""

from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Application Settings
    APP_NAME: str = "NewSystem.AI API"
    APP_ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "change-in-production"
    
    # Database Settings
    DATABASE_URL: str = "postgresql://user:password@localhost/newsystem_db"
    SUPABASE_URL: str = ""
    SUPABASE_SERVICE_KEY: str = ""
    
    # AI Services
    OPENAI_API_KEY: str = ""
    OPENAI_ORG_ID: str = ""
    GPT4V_MODEL: str = "gpt-4-vision-preview"
    MAX_TOKENS_PER_REQUEST: int = 4096
    
    # Storage
    SUPABASE_STORAGE_BUCKET: str = "recordings"
    MAX_FILE_SIZE_MB: int = 500
    ALLOWED_VIDEO_FORMATS: List[str] = ["webm", "mp4"]
    
    # Background Jobs
    REDIS_URL: str = "redis://localhost:6379"
    CELERY_BROKER_URL: str = "redis://localhost:6379"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379"
    
    # Security
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173", "https://app.newsystem.ai"]
    
    # Business Logic
    DEFAULT_ANALYSIS_TIMEOUT_MINUTES: int = 10
    MAX_CONCURRENT_ANALYSES: int = 5
    COST_PER_GPT4V_REQUEST: float = 0.01
    
    # Logging
    LOGGING_LEVEL: str = "INFO"
    SENTRY_DSN: str = ""
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Global settings instance
settings = Settings()