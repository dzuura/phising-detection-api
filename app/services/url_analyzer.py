"""URL analysis orchestration service"""
import time
from typing import Dict, Any
from app.services.feature_extractor import feature_extractor
from app.ml.predictor import PhishingPredictor
from app.core.logging import get_logger


logger = get_logger(__name__)


class URLAnalyzer:
    """Orchestrates URL analysis workflow"""
    
    def __init__(self, predictor: PhishingPredictor):
        self.predictor = predictor
        self.feature_extractor = feature_extractor
    
    def analyze_url(self, url: str) -> Dict[str, Any]:
        """
        Analyze a URL for phishing
        
        Args:
            url: The URL to analyze
            
        Returns:
            Complete analysis results
        """
        start_time = time.time()
        
        try:
            logger.info(f"Starting analysis for URL")
            
            # Extract features
            features = self.feature_extractor.extract_all_features(url)
            
            # Get prediction
            prediction_result = self.predictor.predict(features)
            
            # Calculate risk indicators for phishing URLs
            risk_indicators = []
            if prediction_result["is_phishing"]:
                risk_indicators = self._calculate_risk_indicators(features)
            
            # Calculate analysis time
            analysis_time_ms = int((time.time() - start_time) * 1000)
            
            # Build complete response
            result = {
                "url": url,
                "is_phishing": prediction_result["is_phishing"],
                "confidence": prediction_result["confidence"],
                "risk_level": prediction_result["risk_level"],
                "risk_indicators": risk_indicators,
                "features": {
                    "url_similarity_index": features.get("url_similarity_index"),
                    "char_continuation_rate": features.get("char_continuation_rate"),
                    "tld": features.get("tld"),
                    "no_of_dot_in_url": features.get("no_of_dot_in_url"),
                    "no_of_dash_in_url": features.get("no_of_dash_in_url"),
                    "url_is_live": features.get("url_is_live"),
                    "has_title": features.get("has_title"),
                    "has_favicon": features.get("has_favicon"),
                    "has_social_net": features.get("has_social_net"),
                    "has_copyright_info": features.get("has_copyright_info"),
                    "no_of_js": features.get("no_of_js"),
                },
                "network_info": {
                    "redirect_chain": features.get("redirect_chain", []),
                    "final_url": features.get("final_url", url),
                    "ip_address": features.get("ip_address"),
                    "location": features.get("location", {})
                },
                "detection_timestamp": features.get("detection_timestamp"),
                "analysis_time_ms": analysis_time_ms
            }
            
            logger.info(f"Analysis complete in {analysis_time_ms}ms")
            return result
            
        except Exception as e:
            logger.error(f"URL analysis failed: {str(e)}", exc_info=True)
            raise
    
    def _calculate_risk_indicators(self, features: Dict[str, Any]) -> list:
        """
        Calculate risk indicators based on features
        
        Args:
            features: Extracted features
            
        Returns:
            List of risk indicator strings
        """
        indicators = []
        
        # Check for suspicious URL patterns
        if features.get("no_of_at_symbol_in_url", 0) > 0:
            indicators.append("URL contains @ symbol (possible credential phishing)")
        
        if features.get("no_of_dash_in_url", 0) > 3:
            indicators.append("Excessive dashes in URL")
        
        if features.get("no_of_dot_in_url", 0) > 5:
            indicators.append("Excessive dots in URL (possible subdomain spoofing)")
        
        # Check for missing security indicators
        if not features.get("has_favicon"):
            indicators.append("Missing favicon")
        
        if not features.get("has_copyright_info"):
            indicators.append("No copyright information found")
        
        if not features.get("has_title"):
            indicators.append("Missing page title")
        
        # Check for suspicious content
        if features.get("has_hidden_fields"):
            indicators.append("Contains hidden form fields")
        
        if features.get("pay") and not features.get("has_social_net"):
            indicators.append("Payment-related content without social media presence")
        
        # Check redirect chain
        if len(features.get("redirect_chain", [])) > 2:
            indicators.append(f"Multiple redirects detected ({len(features.get('redirect_chain', []))} hops)")
        
        return indicators


# This will be initialized with the model in main.py
url_analyzer = None
