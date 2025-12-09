"""Pydantic models for API requests and responses"""
from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, HttpUrl, Field, validator


class URLPredictionRequest(BaseModel):
    """Request model for URL prediction"""
    url: str = Field(..., description="URL to analyze for phishing")
    
    @validator('url')
    def validate_url_format(cls, v):
        """Validate URL format"""
        if not v or len(v.strip()) == 0:
            raise ValueError("URL cannot be empty")
        
        # Basic URL validation
        v = v.strip()
        if not v.startswith(('http://', 'https://')):
            v = 'https://' + v
        
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://example.com"
            }
        }


class NetworkInfo(BaseModel):
    """Network information about the URL"""
    redirect_chain: List[str] = Field(default_factory=list, description="Chain of redirects")
    final_url: str = Field(..., description="Final URL after redirects")
    ip_address: Optional[str] = Field(None, description="IP address of the server")
    location: Dict[str, Any] = Field(
        default_factory=dict,
        description="Geographic location of the server"
    )


class Features(BaseModel):
    """Extracted features from URL"""
    # URL Structure features
    url_similarity_index: Optional[float] = None
    char_continuation_rate: Optional[float] = None
    url_char_prob: Optional[float] = None
    letter_ratio: Optional[float] = None
    digit_ratio: Optional[float] = None
    special_chars: Optional[int] = None
    special_char_ratio: Optional[float] = None
    is_https: Optional[int] = None
    no_of_dot_in_url: Optional[int] = None
    no_of_dash_in_url: Optional[int] = None
    url_is_live: Optional[int] = None
    # Content features
    has_title: Optional[int] = None
    domain_title_match: Optional[float] = None
    url_title_match: Optional[float] = None
    has_favicon: Optional[int] = None
    has_robots: Optional[int] = None
    is_responsive: Optional[int] = None
    has_description: Optional[int] = None
    has_social_net: Optional[int] = None
    has_submit_button: Optional[int] = None
    has_hidden_fields: Optional[int] = None
    has_payment: Optional[int] = None
    has_copyright: Optional[int] = None
    no_of_js: Optional[int] = None
    no_of_self_ref: Optional[int] = None
    tld: Optional[str] = None


class PredictionResponse(BaseModel):
    """Response model for URL prediction"""
    url: str = Field(..., description="Analyzed URL")
    is_phishing: bool = Field(..., description="Whether URL is phishing")
    confidence: float = Field(..., description="Prediction confidence score (0-1)")
    risk_level: str = Field(..., description="Risk level: low, medium, or high")
    risk_indicators: List[str] = Field(
        default_factory=list,
        description="List of risk indicators found"
    )
    features: Features = Field(..., description="Extracted features")
    network_info: NetworkInfo = Field(..., description="Network information")
    detection_timestamp: str = Field(..., description="Timestamp of detection (ISO 8601)")
    analysis_time_ms: int = Field(..., description="Analysis time in milliseconds")
    
    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://example.com",
                "is_phishing": False,
                "confidence": 0.95,
                "risk_level": "low",
                "risk_indicators": [],
                "features": {
                    "url_similarity_index": 100.0,
                    "char_continuation_rate": 0.15,
                    "tld": "com",
                    "no_of_dot_in_url": 2,
                    "no_of_dash_in_url": 0
                },
                "network_info": {
                    "redirect_chain": [],
                    "final_url": "https://example.com",
                    "ip_address": "93.184.216.34",
                    "location": {
                        "country": "United States",
                        "city": "Los Angeles",
                        "region": "California"
                    }
                },
                "detection_timestamp": "2024-12-05T10:30:00Z",
                "analysis_time_ms": 245
            }
        }


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error type")
    detail: str = Field(..., description="Error details")
    timestamp: str = Field(..., description="Error timestamp")
    path: Optional[str] = Field(None, description="Request path")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "ValidationError",
                "detail": "Invalid URL format",
                "timestamp": "2024-12-05T10:30:00Z",
                "path": "/api/v1/predict"
            }
        }


class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Service status")
    model_loaded: bool = Field(..., description="Whether ML model is loaded")
    version: str = Field(..., description="API version")
    timestamp: str = Field(..., description="Current timestamp")
    
    model_config = {
        "protected_namespaces": (),  # Disable protected namespace warnings
        "json_schema_extra": {
            "example": {
                "status": "healthy",
                "model_loaded": True,
                "version": "1.0.0",
                "timestamp": "2024-12-05T10:30:00Z"
            }
        }
    }


class StatsResponse(BaseModel):
    """Statistics response"""
    total_analyzed: int = Field(..., description="Total URLs analyzed")
    phishing_detected: int = Field(..., description="Number of phishing URLs detected")
    legitimate_detected: int = Field(..., description="Number of legitimate URLs detected")
    avg_confidence: float = Field(..., description="Average confidence score")
    session_start: str = Field(..., description="Session start timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_analyzed": 150,
                "phishing_detected": 45,
                "legitimate_detected": 105,
                "avg_confidence": 0.87,
                "session_start": "2024-12-05T09:00:00Z"
            }
        }


class PhishingInfo(BaseModel):
    """Phishing information"""
    type: str
    description: str
    indicators: List[str]
    examples: List[str]


class PhishingInfoResponse(BaseModel):
    """Response for phishing information endpoint"""
    categories: List[PhishingInfo]
    language: str = "en"


class MitigationStrategy(BaseModel):
    """Mitigation strategy"""
    title: str
    description: str
    steps: List[str]
    category: str  # "technical" or "non-technical"


class MitigationInfoResponse(BaseModel):
    """Response for mitigation information endpoint"""
    individual: List[MitigationStrategy]
    organization: List[MitigationStrategy]
    language: str = "en"
