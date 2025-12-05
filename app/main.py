"""Main FastAPI application"""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from datetime import datetime
import sys

from app.core.config import settings
from app.core.logging import setup_logging, get_logger
from app.ml.model_loader import model_loader
from app.ml.predictor import PhishingPredictor
from app.services import url_analyzer
from app.api.routes import detection, health, info
from app import __version__


# Setup logging
setup_logging()
logger = get_logger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    logger.error(f"Validation error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": "ValidationError",
            "detail": str(exc),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "path": str(request.url.path)
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "InternalServerError",
            "detail": "An unexpected error occurred",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "path": str(request.url.path)
        }
    )


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    try:
        logger.info("Starting Phishing Detection API...")
        logger.info(f"Version: {__version__}")
        logger.info(f"Model path: {settings.model_path}")
        
        # Load and validate model
        model = model_loader.initialize()
        logger.info("Model loaded and validated successfully")
        
        # Initialize predictor
        predictor = PhishingPredictor(model)
        
        # Initialize URL analyzer with predictor
        url_analyzer.url_analyzer = url_analyzer.URLAnalyzer(predictor)
        logger.info("URL analyzer initialized")
        
        logger.info("Application startup complete")
        
    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}", exc_info=True)
        sys.exit(1)


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Phishing Detection API...")


# Include routers
app.include_router(
    detection.router,
    prefix=f"/api/{settings.api_version}",
    tags=["Detection"]
)

app.include_router(
    health.router,
    prefix=f"/api/{settings.api_version}",
    tags=["Health & Stats"]
)

app.include_router(
    info.router,
    prefix=f"/api/{settings.api_version}/info",
    tags=["Information"]
)


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "name": settings.api_title,
        "version": __version__,
        "docs": "/docs",
        "health": f"/api/{settings.api_version}/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload
    )
