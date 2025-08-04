"""
NewSystem.AI FastAPI Application
Main entry point for our logistics workflow analysis platform
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1 import auth, recordings, analysis, results, insights
from app.core.config import settings

# Create FastAPI app with NewSystem.AI branding
app = FastAPI(
    title="NewSystem.AI API",
    description="AI-powered screen recording and workflow analysis platform for logistics operations",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
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
        "description": "AI-powered workflow analysis for logistics operations",
        "mission": "Saving 1,000,000 operator hours monthly",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring and frontend connection testing"""
    return {
        "status": "healthy",
        "service": "NewSystem.AI API",
        "version": "1.0.0",
        "environment": settings.APP_ENV
    }

@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "Endpoint not found"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)