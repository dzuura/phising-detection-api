"""Model loading and validation"""
import os
import joblib
from typing import Any
from sklearn.ensemble import RandomForestClassifier
from app.core.logging import get_logger
from app.core.config import settings


logger = get_logger(__name__)


class ModelLoader:
    """Handles loading and validation of the Random Forest model"""
    
    def __init__(self):
        self.model: RandomForestClassifier | None = None
        self.model_path = settings.model_path
    
    def load_model(self) -> RandomForestClassifier:
        """
        Load the Random Forest model from pickle file
        
        Returns:
            RandomForestClassifier: Loaded model
            
        Raises:
            FileNotFoundError: If model file doesn't exist
            Exception: If model loading fails
        """
        try:
            # Check if model file exists
            if not os.path.exists(self.model_path):
                error_msg = f"Model file not found at: {self.model_path}"
                logger.error(error_msg)
                raise FileNotFoundError(error_msg)
            
            logger.info(f"Loading model from: {self.model_path}")
            
            # Load model using joblib
            model = joblib.load(self.model_path)
            
            logger.info("Model loaded successfully")
            return model
            
        except FileNotFoundError:
            raise
        except Exception as e:
            error_msg = f"Failed to load model: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise Exception(error_msg) from e
    
    def validate_model(self, model: Any) -> bool:
        """
        Validate that the loaded model is compatible
        
        Args:
            model: The loaded model to validate
            
        Returns:
            bool: True if model is valid
            
        Raises:
            ValueError: If model validation fails
        """
        try:
            # Check if model is RandomForestClassifier
            if not isinstance(model, RandomForestClassifier):
                raise ValueError(
                    f"Expected RandomForestClassifier, got {type(model).__name__}"
                )
            
            # Check if model has been fitted
            if not hasattr(model, "n_features_in_"):
                raise ValueError("Model has not been fitted")
            
            # Validate feature dimensions (expecting 22 features after preprocessing)
            expected_features = model.n_features_in_
            logger.info(f"Model expects {expected_features} features")
            
            # Check if model has classes
            if not hasattr(model, "classes_"):
                raise ValueError("Model does not have classes_ attribute")
            
            logger.info(f"Model validation successful. Classes: {model.classes_}")
            return True
            
        except ValueError as e:
            logger.error(f"Model validation failed: {str(e)}")
            raise
    
    def initialize(self) -> RandomForestClassifier:
        """
        Initialize model by loading and validating
        
        Returns:
            RandomForestClassifier: Loaded and validated model
        """
        model = self.load_model()
        self.validate_model(model)
        self.model = model
        return model


# Global model loader instance
model_loader = ModelLoader()
