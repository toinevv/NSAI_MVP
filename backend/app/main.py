"""
NewSystem.AI FastAPI Application
Main entry point for our business workflow analysis platform
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from app.api.v1 import auth, recordings, analysis, results, insights
from app.core.config import settings
from app.services.supabase_client import get_supabase_client

# Configure logging
logging.basicConfig(level=getattr(logging, settings.LOGGING_LEVEL))
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup and shutdown events"""
    # Startup
    logger.info("🚀 Starting NewSystem.AI API...")
    logger.info("🔐 Using native Supabase authentication and RLS")
    
    # Test Supabase connection
    try:
        supabase_client = get_supabase_client()
        if supabase_client.test_connection():
            logger.info("✅ Supabase connection test passed")
            logger.info("🏢 Multi-tenant isolation enabled via Row Level Security")
        else:
            logger.warning("⚠️ Supabase connection test failed - check your SUPABASE_URL and SUPABASE_SERVICE_KEY")
    except Exception as e:
        logger.error(f"❌ Supabase client initialization failed: {e}")
        logger.error("Please ensure SUPABASE_URL and SUPABASE_SERVICE_KEY are set correctly")
    
    logger.info("🎯 NewSystem.AI API startup complete - Ready to save 1,000,000 operator hours!")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down NewSystem.AI API...")

# Create FastAPI app with NewSystem.AI branding and modern lifespan handler
app = FastAPI(
    title="NewSystem.AI API",
    description="AI-powered screen recording and workflow analysis platform for business operations",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
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
    # Test Supabase connection (which is our only database now)
    supabase_status = "unknown"
    try:
        supabase_client = get_supabase_client()
        supabase_status = "healthy" if supabase_client.test_connection() else "unhealthy"
    except Exception as e:
        logger.error(f"Health check Supabase error: {e}")
        supabase_status = "unhealthy"
    
    return {
        "status": "healthy" if supabase_status == "healthy" else "degraded",
        "service": "NewSystem.AI API", 
        "version": "1.0.0",
        "environment": settings.APP_ENV,
        "components": {
            "database": supabase_status,  # Supabase IS our database
            "supabase": supabase_status,
            "recording_service": "healthy",
            "storage_service": supabase_status,
            "authentication": supabase_status
        },
        "configuration": {
            "chunk_size_seconds": settings.CHUNK_SIZE_SECONDS,
            "recording_fps": settings.RECORDING_FPS,
            "max_file_size_mb": settings.MAX_FILE_SIZE_MB,
            "architecture": "native_supabase_with_rls"
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