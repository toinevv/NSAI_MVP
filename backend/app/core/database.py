"""
Database connection and session management for NewSystem.AI
Using Supabase PostgreSQL with SQLAlchemy - Simplified for MVP
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from app.core.config import settings
import logging
import os

logger = logging.getLogger(__name__)

def get_database_url() -> str:
    """
    Get database URL for Supabase connection
    For MVP, we'll use a simplified approach via Supabase client
    """
    # For MVP, we'll use the supabase-py client for database operations
    # This is simpler than constructing PostgreSQL URLs
    # In production, we can optimize with direct PostgreSQL connections
    
    # Fallback to local database for development if Supabase isn't configured
    if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_KEY:
        logger.warning("Supabase not fully configured, using SQLite for development")
        return "sqlite:///./newsystem_mvp.db"
    
    # For now, return SQLite - we'll use Supabase client for operations
    # This allows us to test locally while using Supabase for storage
    return "sqlite:///./newsystem_mvp.db"

# Create database engine
DATABASE_URL = get_database_url()

# Configure engine based on database type
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},  # For SQLite
        echo=settings.DEBUG
    )
else:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=300,
        echo=settings.DEBUG
    )

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Session:
    """
    Dependency to get database session
    Use this in FastAPI endpoints
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_sync_db() -> Session:
    """Get synchronous database session for background tasks"""
    return SessionLocal()

def init_database():
    """Initialize database tables"""
    try:
        from app.models.database import Base
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        return True
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return False

def test_connection() -> bool:
    """Test database connection"""
    try:
        with SessionLocal() as db:
            if DATABASE_URL.startswith("sqlite"):
                db.execute(text("SELECT 1"))
            else:
                db.execute(text("SELECT 1"))
            db.commit()
        logger.info("Database connection test successful")
        return True
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False