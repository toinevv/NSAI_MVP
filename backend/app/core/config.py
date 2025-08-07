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
    
    # Supabase Settings
    SUPABASE_URL: str = ""
    SUPABASE_SERVICE_KEY: str = ""
    SUPABASE_ANON_KEY: str = ""  # Added for frontend compatibility
    
    # AI Services
    OPENAI_API_KEY: str = ""
    GPT4V_MODEL: str = "gpt-4o"  # Updated model that supports vision
    MAX_TOKENS_PER_REQUEST: int = 4096
    
    # Storage
    SUPABASE_STORAGE_BUCKET: str = "recording-sessions"
    MAX_FILE_SIZE_MB: int = 500
    ALLOWED_VIDEO_FORMATS: List[str] = ["webm", "mp4"]
    CHUNK_SIZE_SECONDS: int = 5  # 5-second chunks per August plan
    
    # CORS Settings
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Convert CORS_ORIGINS string to list"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    # Business Logic (MVP Focused)
    DEFAULT_ANALYSIS_TIMEOUT_MINUTES: int = 10
    MAX_CONCURRENT_ANALYSES: int = 5
    COST_PER_GPT4V_REQUEST: float = 0.01
    
    # Recording Settings (August Plan Specifications)
    RECORDING_FPS: int = 2  # 2 FPS as per August plan
    MAX_RECORDING_DURATION_MINUTES: int = 30
    FRAME_EXTRACTION_INTERVAL: int = 10  # 1 frame per 10 seconds
    
    # Logging
    LOGGING_LEVEL: str = "INFO"
    SENTRY_DSN: str = ""
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Global settings instance
settings = Settings()