"""URL analysis orchestration service"""
import time
from typing import Dict, Any
from urllib.parse import urlparse
from datetime import datetime
from app.ml.predictor import PhishingPredictor
from app.core.logging import get_logger


logger = get_logger(__name__)


class URLAnalyzer:
    """Orchestrates URL analysis workflow"""
    
    def __init__(self, predictor: PhishingPredictor):
        self.predictor = predictor
        # Import here to avoid circular dependency
        from app.services.feature_extractor import FeatureExtractor
        self.feature_extractor = FeatureExtractor()
    
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
            logger.info(f"Starting analysis for URL: {url}")
            
            # Extract all 22 features
            features = self.feature_extractor.extract_all_features(url)
            
            # Add TLD for model
            parsed = urlparse(url)
            domain = parsed.netloc
            tld = domain.split('.')[-1] if '.' in domain else ''
            features['tld'] = tld
            
            # Get prediction
            prediction_result = self.predictor.predict(features)
            
            # Calculate risk indicators for phishing URLs
            risk_indicators = []
            if prediction_result["is_phishing"]:
                risk_indicators_dict = self._calculate_risk_indicators(features)
                risk_indicators = list(risk_indicators_dict.values())
            
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
                    # URL Structure features
                    "url_similarity_index": features.get("URLSimilarityIndex"),
                    "char_continuation_rate": features.get("CharContinuationRate"),
                    "url_char_prob": features.get("URLCharProb"),
                    "letter_ratio": features.get("LetterRatioInURL"),
                    "digit_ratio": features.get("DegitRatioInURL"),
                    "special_chars": features.get("NoOfOtherSpecialCharsInURL"),
                    "special_char_ratio": features.get("SpacialCharRatioInURL"),
                    "is_https": features.get("IsHTTPS"),
                    "no_of_dot_in_url": features.get("NoOfDotInURL"),
                    "no_of_dash_in_url": features.get("NoOfDashInURL"),
                    "url_is_live": features.get("URLIsLive"),
                    # Content features
                    "has_title": features.get("HasTitle"),
                    "domain_title_match": features.get("DomainTitleMatchScore"),
                    "url_title_match": features.get("URLTitleMatchScore"),
                    "has_favicon": features.get("HasFavicon"),
                    "has_robots": features.get("Robots"),
                    "is_responsive": features.get("IsResponsive"),
                    "has_description": features.get("HasDescription"),
                    "has_social_net": features.get("HasSocialNet"),
                    "has_submit_button": features.get("HasSubmitButton"),
                    "has_hidden_fields": features.get("HasHiddenFields"),
                    "has_payment": features.get("Pay"),
                    "has_copyright": features.get("HasCopyrightInfo"),
                    "no_of_js": features.get("NoOfJS"),
                    "no_of_self_ref": features.get("NoOfSelfRef"),
                    "tld": tld,
                },
                "network_info": {
                    "redirect_chain": self.feature_extractor.redirect_chain,
                    "final_url": self.feature_extractor.final_url or url,
                    "ip_address": self.feature_extractor.ip_address,
                    "location": self.feature_extractor.location
                },
                "detection_timestamp": datetime.utcnow().isoformat() + "Z",
                "analysis_time_ms": analysis_time_ms
            }
            
            logger.info(f"Analysis complete in {analysis_time_ms}ms - Phishing: {prediction_result['is_phishing']}")
            return result
            
        except Exception as e:
            logger.error(f"URL analysis failed: {str(e)}", exc_info=True)
            raise
    
    def _calculate_risk_indicators(self, features: Dict[str, Any]) -> Dict[str, str]:
        """
        Calculate risk indicators based on features
        
        Args:
            features: Extracted features
            
        Returns:
            Dictionary of risk indicators
        """
        indicators = {}
        
        # Check URL structure - CRITICAL indicators
        if features.get("URLSimilarityIndex", 100) < 40:
            indicators["low_similarity"] = "⚠️ URL has unusual character distribution (possible obfuscation)"
        
        if features.get("CharContinuationRate", 0) > 0.25:
            indicators["high_continuation"] = "⚠️ URL has many repeated characters"
        
        if features.get("DegitRatioInURL", 0) > 0.3:
            indicators["high_digits"] = "⚠️ URL contains excessive digits (common in phishing)"
        
        if features.get("SpacialCharRatioInURL", 0) > 0.25:
            indicators["high_special_chars"] = "⚠️ URL contains many special characters"
        
        if features.get("NoOfDotInURL", 0) > 5:
            indicators["excessive_dots"] = "⚠️ Excessive dots in URL (possible subdomain spoofing)"
        
        if features.get("NoOfDashInURL", 0) > 3:
            indicators["excessive_dashes"] = "⚠️ Excessive dashes in URL"
        
        # Check security features - IMPORTANT
        if not features.get("IsHTTPS"):
            indicators["no_https"] = "🔒 Website does not use HTTPS (insecure)"
        
        if not features.get("URLIsLive"):
            indicators["url_dead"] = "💀 URL is not accessible (may be taken down)"
        
        # Check missing trust indicators
        if not features.get("HasFavicon"):
            indicators["no_favicon"] = "Missing favicon (unprofessional)"
        
        if not features.get("HasCopyrightInfo"):
            indicators["no_copyright"] = "No copyright information found"
        
        if not features.get("HasTitle"):
            indicators["no_title"] = "Missing page title"
        
        if not features.get("HasDescription"):
            indicators["no_description"] = "Missing meta description"
        
        # Check suspicious content - HIGH RISK
        if features.get("HasHiddenFields"):
            indicators["hidden_fields"] = "🚨 Contains hidden form fields (data theft risk)"
        
        if features.get("Pay") and not features.get("HasSocialNet"):
            indicators["payment_no_social"] = "💳 Payment content without social media presence (suspicious)"
        
        if features.get("HasSubmitButton") and not features.get("IsHTTPS"):
            indicators["form_no_https"] = "🚨 Form submission without HTTPS (credential theft risk)"
        
        # Check trust signals
        if not features.get("Robots"):
            indicators["no_robots"] = "Missing robots meta tag"
        
        if not features.get("IsResponsive"):
            indicators["not_responsive"] = "Website may not be mobile-friendly"
        
        if not features.get("HasSocialNet"):
            indicators["no_social"] = "No social media links found"
        
        if features.get("NoOfJS", 0) == 0 and features.get("HasSubmitButton"):
            indicators["no_js_with_form"] = "Form without JavaScript (unusual for modern sites)"
        
        # Check redirect chain
        redirect_count = len(self.feature_extractor.redirect_chain) - 1
        if redirect_count > 2:
            indicators["multiple_redirects"] = f"⚠️ Multiple redirects detected ({redirect_count} hops)"
        
        return indicators


# This will be initialized with the model in main.py
url_analyzer = None
