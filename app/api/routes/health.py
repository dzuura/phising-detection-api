"""Health check and statistics endpoints"""
from fastapi import APIRouter
from datetime import datetime
from app.models.schemas import HealthCheckResponse, StatsResponse
from app.ml.model_loader import model_loader
from app.services.stats_service import stats_service
from app import __version__


router = APIRouter()


@router.get(
    "/health",
    response_model=HealthCheckResponse,
    summary="Health check",
    description="Check if the service is healthy and model is loaded"
)
async def health_check():
    """
    Health check endpoint
    
    Returns service status and model availability
    """
    return {
        "status": "healthy",
        "model_loaded": model_loader.model is not None,
        "version": __version__,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }


@router.get(
    "/stats",
    response_model=StatsResponse,
    summary="Get statistics",
    description="Get analysis statistics for the current session"
)
async def get_statistics():
    """
    Get analysis statistics
    
    Returns statistics about URLs analyzed in the current session
    """
    return stats_service.get_stats()
