"""Phishing prediction using Random Forest model"""
import numpy as np
from typing import Dict, Any, List
from sklearn.ensemble import RandomForestClassifier
from app.core.logging import get_logger
from app.services.tld_encoder import tld_encoder


logger = get_logger(__name__)


class PhishingPredictor:
    """Handles phishing prediction using the trained model"""
    
    def __init__(self, model: RandomForestClassifier):
        self.model = model
    
    def predict(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict if URL is phishing
        
        Args:
            features: Dictionary of extracted features
            
        Returns:
            Dictionary containing prediction results
        """
        try:
            # Convert features to vector
            feature_vector = self._features_to_vector(features)
            
            # Create feature names list (matching training data)
            feature_names = self._get_feature_names()
            
            # Reshape for model input with feature names
            import pandas as pd
            X = pd.DataFrame([feature_vector], columns=feature_names)
            
            # Get prediction
            prediction = self.model.predict(X)[0]
            
            # Get probability scores
            probabilities = self.model.predict_proba(X)[0]
            
            # Determine confidence and risk level
            confidence = float(max(probabilities))
            is_phishing = bool(prediction == 0)  # Assuming 0 = phishing, 1 = legitimate
            
            # --- Heuristic Override ---
            # If high similarity to a top domain BUT not that domain (Impersonation)
            # USI is usually > 40 for close matches. Let's use 30 to be safe.
            usi = float(features.get("URLSimilarityIndex", 0))
            is_safe_match = bool(features.get("IsSafeMatch", 0))
            
            if usi > 30.0 and not is_safe_match:
                logger.warning(f"Heuristic Override: High Similarity ({usi}) + Unsafe Match -> PHISHING")
                is_phishing = True
                confidence = 0.99
                risk_level = "high"
                # Adjust probabilities to reflect this certainty
                probabilities = [0.99, 0.01]
            else:
                risk_level = self._determine_risk_level(confidence, is_phishing)
            # --------------------------
            
            result = {
                "is_phishing": is_phishing,
                "confidence": confidence,
                "risk_level": risk_level,
                "probabilities": {
                    "phishing": float(probabilities[0]),
                    "legitimate": float(probabilities[1])
                }
            }
            
            logger.info(f"Prediction complete: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Prediction failed: {str(e)}", exc_info=True)
            raise
    
    def _features_to_vector(self, features: Dict[str, Any]) -> List[float]:
        """
        Convert feature dictionary to vector for model input
        
        Args:
            features: Dictionary of extracted features
            
        Returns:
            List of feature values in correct order (716 features total)
        """
        # Base features (22 features - must match training order exactly)
        # These are the features that remain after dropping columns in training
        # Base features (22 features - must match training order exactly)
        vector = [
            float(features.get("URLSimilarityIndex", 0)),
            float(features.get("CharContinuationRate", 0)),
            float(features.get("URLCharProb", 0)),
            float(features.get("LetterRatioInURL", 0)),
            float(features.get("DegitRatioInURL", 0)),
            float(features.get("NoOfOtherSpecialCharsInURL", 0)),
            float(features.get("SpacialCharRatioInURL", 0)),
            float(features.get("IsHTTPS", 0)),
            float(features.get("HasTitle", 0)),
            float(features.get("DomainTitleMatchScore", 0)),
            float(features.get("URLTitleMatchScore", 0)),
            float(features.get("HasFavicon", 0)),
            float(features.get("Robots", 0)),
            float(features.get("IsResponsive", 0)),
            float(features.get("HasDescription", 0)),
            float(features.get("HasSocialNet", 0)),
            float(features.get("HasSubmitButton", 0)),
            float(features.get("HasHiddenFields", 0)),
            float(features.get("Pay", 0)),
            float(features.get("HasCopyrightInfo", 0)),
            float(features.get("NoOfJS", 0)),
            float(features.get("NoOfSelfRef", 0)),
        ]
        
        # Add TLD one-hot encoding (694 features)
        # This matches pd.get_dummies(df_X, columns=["TLD"], drop_first=True)
        tld = features.get("tld", "")
        tld_encoded = tld_encoder.encode(tld)
        vector.extend(tld_encoded)
        
        # Total: 22 base features + 694 TLD features = 716 features
        return vector
    
    def _determine_risk_level(self, confidence: float, is_phishing: bool) -> str:
        """
        Determine risk level based on confidence and prediction
        
        Args:
            confidence: Prediction confidence score
            is_phishing: Whether URL is predicted as phishing
            
        Returns:
            Risk level string: "low", "medium", or "high"
        """
        if not is_phishing:
            return "low"
        
        # For phishing URLs, determine risk based on confidence
        if confidence >= 0.9:
            return "high"
        elif confidence >= 0.7:
            return "medium"
        else:
            return "low"
    
    def _get_feature_names(self) -> List[str]:
        """
        Get feature names matching training data
        
        Returns:
            List of feature names (716 features total)
        """
        from app.services.tld_encoder import tld_encoder
        
        # Base feature names (22 features) matching training data
        base_features = [
            "URLSimilarityIndex",
            "CharContinuationRate",
            "URLCharProb",
            "LetterRatioInURL",
            "DegitRatioInURL",
            "NoOfOtherSpecialCharsInURL",
            "SpacialCharRatioInURL",
            "IsHTTPS",
            "HasTitle",
            "DomainTitleMatchScore",
            "URLTitleMatchScore",
            "HasFavicon",
            "Robots",
            "IsResponsive",
            "HasDescription",
            "HasSocialNet",
            "HasSubmitButton",
            "HasHiddenFields",
            "Pay",
            "HasCopyrightInfo",
            "NoOfJS",
            "NoOfSelfRef",
        ]
        
        # TLD feature names (694 features)
        tld_features = tld_encoder.get_feature_names()
        
        # Combine all feature names
        return base_features + tld_features
    
    def predict_proba(self, features: Dict[str, Any]) -> np.ndarray:
        """
        Get probability scores for prediction
        
        Args:
            features: Dictionary of extracted features
            
        Returns:
            Array of probability scores
        """
        feature_vector = self._features_to_vector(features)
        feature_names = self._get_feature_names()
        
        import pandas as pd
        X = pd.DataFrame([feature_vector], columns=feature_names)
        return self.model.predict_proba(X)
