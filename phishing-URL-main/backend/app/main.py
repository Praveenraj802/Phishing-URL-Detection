"""
FastAPI Application Entry Point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.logging import app_logger as logger
from app.api.routes import router as api_router


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Real-time phishing URL detection with explainable AI",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include API routes
app.include_router(
    api_router,
    prefix=settings.api_prefix,
    tags=["URL Scanning"]
)


@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Debug mode: {settings.debug}")
    
    # Initialize models
    from app.models.predictor import get_predictor
    predictor = get_predictor()
    
    if predictor.is_ready():
        logger.info("✓ Models loaded and ready")
    else:
        logger.warning("⚠ Models not loaded - using rule-based fallback")


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    logger.info(f"Shutting down {settings.app_name}")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "docs": "/docs",
        "api": settings.api_prefix
    }


@app.get("/api")
async def api_root():
    """API root endpoint"""
    return {
        "message": "Phishing URL Detection API",
        "version": settings.app_version,
        "endpoints": {
            "scan_url": f"{settings.api_prefix}/scan-url",
            "health": f"{settings.api_prefix}/health",
            "feedback": f"{settings.api_prefix}/feedback"
        }
    }


# Custom exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
            "detail": str(exc) if settings.debug else None
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        reload_excludes=["venv", "*.pyc", "__pycache__"],
        log_level="info"
    )
