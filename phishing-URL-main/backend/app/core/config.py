"""
Application Configuration
"""

from pydantic_settings import BaseSettings
from typing import Optional, List


class Settings(BaseSettings):
    """Application settings"""
    
    # API Settings
    app_name: str = "Phishing URL Detection API"
    app_version: str = "1.0.0"
    api_prefix: str = "/api/v1"
    debug: bool = True
    
    # CORS Settings
    cors_origins: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    # Model Settings
    model_path: str = "models"
    feature_classifier_name: str = "feature_classifier.joblib"
    sequence_classifier_name: str = "sequence_classifier.h5"
    lstm_model_name: str = "lstm_classifier.h5"
    google_safe_browsing_api_key: str = ""
    
    # Path mappingsference Settings
    max_url_length: int = 2048
    inference_timeout: int = 5  # seconds
    
    # Logging
    log_level: str = "INFO"
    log_file: Optional[str] = "logs/app.log"
    
    # Database (for adaptive learning)
    database_url: str = "sqlite:///./phishing_detector.db"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
