"""
NewSystem.AI FastAPI Application
Main entry point for our business workflow analysis platform
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from app.api.v1 import auth, recordings, analysis, results, insights
from app.core.config import settings
from app.core.database import init_database, test_connection
from app.services.supabase_client import get_supabase_client

# Configure logging
logging.basicConfig(level=getattr(logging, settings.LOGGING_LEVEL))
logger = logging.getLogger(__name__)

# Create FastAPI app with NewSystem.AI branding
app = FastAPI(
    title="NewSystem.AI API",
    description="AI-powered screen recording and workflow analysis platform for business operations",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(recordings.router, prefix="/api/v1/recordings", tags=["recordings"])
app.include_router(analysis.router, prefix="/api/v1/analysis", tags=["analysis"])
app.include_router(results.router, prefix="/api/v1/results", tags=["results"])
app.include_router(insights.router, prefix="/api/v1/insights", tags=["insights"])

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info("Starting NewSystem.AI API...")
    
    # Initialize database with retry logic
    max_retries = 3
    for attempt in range(max_retries):
        logger.info(f"Database initialization attempt {attempt + 1}/{max_retries}")
        if init_database():
            logger.info("Database initialized successfully")
            break
        elif attempt < max_retries - 1:
            logger.warning(f"Database initialization failed, retrying in 2 seconds...")
            import asyncio
            await asyncio.sleep(2)
        else:
            logger.error("Database initialization failed after all retries")
    
    # Test database connection
    if test_connection():
        logger.info("Database connection test passed")
    else:
        logger.error("Database connection test failed - some features may not work")
    
    # Test Supabase connection (non-critical for startup)
    try:
        supabase_client = get_supabase_client()
        if supabase_client.test_connection():
            logger.info("Supabase connection test passed")
        else:
            logger.warning("Supabase connection test failed - storage features may not work")
    except Exception as e:
        logger.warning(f"Supabase client initialization failed: {e}")
    
    logger.info("NewSystem.AI API startup complete")

@app.get("/")
async def root():
    """Root endpoint with NewSystem.AI information"""
    return {
        "message": "NewSystem.AI API",
        "description": "AI-powered workflow analysis for business operations",
        "mission": "Saving 1,000,000 operator hours monthly",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "ready"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring and frontend connection testing"""
    # Test database connection
    db_status = "healthy" if test_connection() else "unhealthy"
    
    # Test Supabase connection
    supabase_status = "unknown"
    try:
        supabase_client = get_supabase_client()
        supabase_status = "healthy" if supabase_client.test_connection() else "unhealthy"
    except Exception:
        supabase_status = "unhealthy"
    
    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "service": "NewSystem.AI API", 
        "version": "1.0.0",
        "environment": settings.APP_ENV,
        "components": {
            "database": db_status,
            "supabase": supabase_status,
            "recording_service": "healthy",
            "storage_service": supabase_status
        },
        "configuration": {
            "chunk_size_seconds": settings.CHUNK_SIZE_SECONDS,
            "recording_fps": settings.RECORDING_FPS,
            "max_file_size_mb": settings.MAX_FILE_SIZE_MB
        }
    }

@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "Endpoint not found"}
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)