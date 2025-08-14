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
    OPENAI_API_KEY: str
    GPT4V_MODEL: str
    MAX_TOKENS_PER_REQUEST: int
    GPT4V_TEMPERATURE: float
    GPT4V_IMAGE_DETAIL: str
    
    # Storage
    SUPABASE_STORAGE_BUCKET: str = "recording-sessions"
    MAX_FILE_SIZE_MB: int = 500
    ALLOWED_VIDEO_FORMATS: List[str] = ["webm", "mp4"]
    CHUNK_SIZE_SECONDS: int = 5  # 5-second chunks per August plan
    
    # API Settings
    API_BASE_URL: str = "http://localhost:8000"  # For internal API calls
    
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
    
    # Workflow Type Configuration
    DEFAULT_WORKFLOW_CATEGORIES: List[str] = [
        "data_entry", "reporting", "processing", "communication", "analysis", "other"
    ]
    
    # Priority workflow types (get higher scores in analysis)
    HIGH_PRIORITY_WORKFLOW_TYPES: List[str] = ["data_entry", "processing"]
    
    # Workflow detection keywords for automatic categorization
    WORKFLOW_TYPE_KEYWORDS: dict = {
        "data_entry": ["entry", "typing", "copying", "pasting", "entering", "input"],
        "reporting": ["report", "chart", "graph", "dashboard", "summary", "excel"],
        "processing": ["process", "calculate", "compute", "transform", "convert"],
        "communication": ["email", "message", "chat", "call", "meeting", "response"],
        "analysis": ["analyze", "review", "examine", "investigate", "research"]
    }
    
    # Frame Extraction Configuration
    FRAME_EXTRACTION_MODE: str = "testing"  # "production" or "testing"
    
    # Advanced Frame Extraction Settings (configurable via API)
    DEFAULT_FRAMES_PER_SECOND: float = 1.0  # 1 FPS standard for testing
    MIN_FRAMES_PER_SECOND: float = 0.1      # Minimum allowed FPS
    MAX_FRAMES_PER_SECOND: float = 3.0      # Maximum allowed FPS (cost control)
    DEFAULT_SCENE_CHANGE_THRESHOLD: float = 0.2  # Scene change sensitivity
    DEFAULT_MAX_FRAMES_PER_VIDEO: int = 120  # Maximum frames per video
    
    # Quality Presets for Frame Extraction
    FRAME_EXTRACTION_PRESETS: dict = {
        "quick": {"fps": 0.33, "max_frames": 50, "scene_threshold": 0.3},    # $0.50 for 150s
        "standard": {"fps": 1.0, "max_frames": 120, "scene_threshold": 0.2}, # $1.20 for 120s  
        "detailed": {"fps": 2.0, "max_frames": 200, "scene_threshold": 0.15}, # $2.00 for 100s
        "forensic": {"fps": 3.0, "max_frames": 300, "scene_threshold": 0.1}   # $3.00 for 100s
    }
    
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