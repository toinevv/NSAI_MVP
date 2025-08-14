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
    Uses SQLite for development - Supabase operations handled via client SDK
    """
    # For MVP development, use SQLite for SQLAlchemy operations
    # Supabase data operations will be handled via the Supabase Python client
    # This provides the best compatibility and development experience
    
    if settings.SUPABASE_URL and settings.SUPABASE_SERVICE_KEY:
        logger.info("Supabase configured - using SQLite for SQLAlchemy with Supabase client for data operations")
    else:
        logger.warning("Supabase not fully configured - using SQLite for development")
    
    # Always use SQLite for now - this allows local development and testing
    # while we can still save data to Supabase via the client SDK when needed
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
    """Initialize database tables with proper error handling"""
    try:
        from app.models.database import Base
        
        logger.info("Starting database initialization...")
        
        # Create all tables
        Base.metadata.create_all(bind=engine, checkfirst=True)
        
        # Test that we can actually use the database
        with SessionLocal() as db:
            if DATABASE_URL.startswith("sqlite"):
                db.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
            else:
                db.execute(text("SELECT tablename FROM pg_tables WHERE schemaname='public'"))
            db.commit()
        
        logger.info("Database tables created and verified successfully")
        return True
        
    except ImportError as e:
        logger.error(f"Failed to import database models: {e}")
        return False
    except Exception as e:
        logger.error(f"Database initialization failed: {e}", exc_info=True)
        
        # Try to create the database file directory for SQLite
        if DATABASE_URL.startswith("sqlite"):
            try:
                os.makedirs(os.path.dirname(DATABASE_URL.replace("sqlite:///", "")), exist_ok=True)
                logger.info("Created database directory, retrying initialization...")
                Base.metadata.create_all(bind=engine, checkfirst=True)
                return True
            except Exception as retry_error:
                logger.error(f"Retry failed: {retry_error}")
        
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