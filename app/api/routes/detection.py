"""Detection endpoint"""
from fastapi import APIRouter, HTTPException, status
from app.models.schemas import URLPredictionRequest, PredictionResponse, ErrorResponse
from app.services.url_analyzer import url_analyzer
from app.services.stats_service import stats_service
from app.core.logging import get_logger
from datetime import datetime


logger = get_logger(__name__)
router = APIRouter()


@router.post(
    "/predict",
    response_model=PredictionResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    },
    summary="Analyze URL for phishing",
    description="Analyzes a URL and returns prediction with detailed features and network information"
)
async def predict_url(request: URLPredictionRequest):
    """
    Analyze a URL for phishing detection
    
    - **url**: The URL to analyze (will be prefixed with https:// if no protocol specified)
    
    Returns detailed analysis including:
    - Phishing prediction and confidence score
    - Risk level and indicators
    - Extracted features
    - Network information (redirects, IP, location)
    - Detection timestamp
    """
    try:
        logger.info(f"Received prediction request")
        
        # Analyze URL
        result = url_analyzer.analyze_url(request.url)
        
        # Record statistics
        stats_service.record_analysis(
            result["is_phishing"],
            result["confidence"]
        )
        
        return result
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during URL analysis"
        )
