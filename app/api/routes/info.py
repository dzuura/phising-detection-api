"""Information endpoints for phishing and mitigation"""
import json
import os
from fastapi import APIRouter, Query
from typing import Dict, Any
from app.models.schemas import PhishingInfoResponse, MitigationInfoResponse


router = APIRouter()

# Load static data
DATA_DIR = os.path.join(os.path.dirname(__file__), "../../data")
PHISHING_INFO_PATH = os.path.join(DATA_DIR, "phishing_info.json")
MITIGATION_INFO_PATH = os.path.join(DATA_DIR, "mitigation_info.json")

# Cache loaded data
_phishing_info_cache: Dict[str, Any] = {}
_mitigation_info_cache: Dict[str, Any] = {}


def load_phishing_info() -> Dict[str, Any]:
    """Load phishing information from JSON file"""
    global _phishing_info_cache
    if not _phishing_info_cache:
        with open(PHISHING_INFO_PATH, 'r', encoding='utf-8') as f:
            _phishing_info_cache = json.load(f)
    return _phishing_info_cache


def load_mitigation_info() -> Dict[str, Any]:
    """Load mitigation information from JSON file"""
    global _mitigation_info_cache
    if not _mitigation_info_cache:
        with open(MITIGATION_INFO_PATH, 'r', encoding='utf-8') as f:
            _mitigation_info_cache = json.load(f)
    return _mitigation_info_cache


@router.get(
    "/phishing",
    response_model=PhishingInfoResponse,
    summary="Get phishing information",
    description="Get educational information about different types of phishing attacks"
)
async def get_phishing_info(
    lang: str = Query(default="en", description="Language code (en or id)")
):
    """
    Get phishing information
    
    - **lang**: Language code (en for English, id for Indonesian)
    
    Returns information about different types of phishing attacks,
    their indicators, and examples
    """
    data = load_phishing_info()
    language = lang if lang in data else "en"
    
    return {
        "categories": data[language]["categories"],
        "language": language
    }


@router.get(
    "/mitigation",
    response_model=MitigationInfoResponse,
    summary="Get mitigation strategies",
    description="Get security recommendations and mitigation strategies for phishing"
)
async def get_mitigation_info(
    lang: str = Query(default="en", description="Language code (en or id)")
):
    """
    Get mitigation strategies
    
    - **lang**: Language code (en for English, id for Indonesian)
    
    Returns mitigation strategies categorized by:
    - Individual users
    - Organizations
    
    Each strategy includes technical and non-technical recommendations
    """
    data = load_mitigation_info()
    language = lang if lang in data else "en"
    
    return {
        "individual": data[language]["individual"],
        "organization": data[language]["organization"],
        "language": language
    }
