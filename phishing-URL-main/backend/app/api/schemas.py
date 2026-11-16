"""
Pydantic schemas for API requests and responses
"""

from pydantic import BaseModel, Field, HttpUrl, validator
from typing import List, Optional


class URLScanRequest(BaseModel):
    """Request schema for URL scanning"""
    url: str = Field(..., description="URL to scan for phishing", min_length=1, max_length=2048)
    
    @validator('url')
    def validate_url_format(cls, v):
        """Validate URL has proper format"""
        v = v.strip()
        if not v:
            raise ValueError("URL cannot be empty")
        
        # Add http:// if no scheme provided
        if not v.startswith(('http://', 'https://')):
            v = 'http://' + v
        
        return v


class URLScanResponse(BaseModel):
    """Response schema for URL scanning"""
    url: str = Field(..., description="The scanned URL")
    prediction: str = Field(..., description="Prediction result: 'phishing' or 'legitimate'")
    confidence: float = Field(..., description="Confidence score (0-1)", ge=0, le=1)
    risk_level: str = Field(..., description="Risk level: 'low', 'medium', or 'high'")
    reasons: List[str] = Field(..., description="Human-readable reasons for the prediction")
    scan_time_ms: float = Field(..., description="Time taken to scan in milliseconds")
    features_extracted: int = Field(..., description="Number of features extracted")


class HealthResponse(BaseModel):
    """Response schema for health check"""
    status: str = Field(..., description="API status")
    version: str = Field(..., description="API version")
    models_loaded: bool = Field(..., description="Whether ML models are loaded")


class FeedbackRequest(BaseModel):
    """Request schema for user feedback"""
    url: str = Field(..., description="The URL that was scanned")
    predicted_label: str = Field(..., description="What the system predicted")
    actual_label: str = Field(..., description="The actual/correct label")
    user_comment: Optional[str] = Field(None, description="Optional user comment")


class FeedbackResponse(BaseModel):
    """Response schema for feedback submission"""
    message: str = Field(..., description="Confirmation message")
    feedback_id: Optional[int] = Field(None, description="Feedback record ID")


class ErrorResponse(BaseModel):
    """Response schema for errors"""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Additional error details")
