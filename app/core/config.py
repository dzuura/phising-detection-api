"""Application configuration"""
import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Model Configuration
    model_path: str = Field(default="./models/model.pkl", env="MODEL_PATH")
    
    # Server Configuration
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    reload: bool = Field(default=False, env="RELOAD")
    
    # CORS Configuration
    allowed_origins: str = Field(
        default="http://localhost:3000",
        env="ALLOWED_ORIGINS"
    )
    
    # Feature Extraction Configuration
    scraping_timeout: int = Field(default=5, env="SCRAPING_TIMEOUT")
    max_redirects: int = Field(default=10, env="MAX_REDIRECTS")
    
    # Rate Limiting
    max_requests_per_minute: int = Field(default=60, env="MAX_REQUESTS_PER_MINUTE")
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="json", env="LOG_FORMAT")
    
    # API Configuration
    api_version: str = Field(default="v1", env="API_VERSION")
    api_title: str = Field(default="Phishing Detection API", env="API_TITLE")
    api_description: str = Field(
        default="API for detecting phishing URLs using machine learning",
        env="API_DESCRIPTION"
    )
    
    @property
    def allowed_origins_list(self) -> List[str]:
        """Parse allowed origins from comma-separated string"""
        return [origin.strip() for origin in self.allowed_origins.split(",")]
    
    model_config = {
        "protected_namespaces": (),  # Disable protected namespace warnings
        "env_file": ".env",
        "case_sensitive": False
    }


# Global settings instance
settings = Settings()
