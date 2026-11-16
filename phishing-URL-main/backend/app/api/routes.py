"""
API Routes for URL Scanning
"""

import time
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from app.api.schemas import (
    URLScanRequest,
    URLScanResponse,
    HealthResponse,
    FeedbackRequest,
    FeedbackResponse,
    ErrorResponse
)
from app.models.predictor import get_predictor
from app.explainability.explainer import ExplainabilityEngine
from app.core.config import settings
from app.core.logging import app_logger as logger

class SimpleTTLCache:
    """In-memory LRU Cache with TTL to prevent re-scanning identical URLs instantly"""
    def __init__(self, ttl_seconds=3600, max_items=10000):
        self.cache = {}
        self.ttl = ttl_seconds
        self.max_items = max_items
        
    def get(self, key):
        if key in self.cache:
            value, timestamp = self.cache[key]
            if time.time() - timestamp <= self.ttl:
                return value
            else:
                del self.cache[key]
        return None
        
    def set(self, key, value):
        if len(self.cache) >= self.max_items:
            # Simple eviction: clear oldest 20%
            sorted_items = sorted(self.cache.items(), key=lambda x: x[1][1])
            for k, _ in sorted_items[:int(self.max_items * 0.2)]:
                del self.cache[k]
        self.cache[key] = (value, time.time())

# Global cache instance (1 hour TTL, max 10,000 URLs)
url_scan_cache = SimpleTTLCache(ttl_seconds=3600, max_items=10000)

router = APIRouter()


@router.post("/scan-url", response_model=URLScanResponse)
async def scan_url(request: URLScanRequest):
    """
    Scan a URL for phishing with optional deep content analysis
    
    Args:
        request: URLScanRequest containing the URL to scan
        
    Returns:
        URLScanResponse with prediction, confidence, and explanations
    """
    try:
        start_time = time.time()
        
        # Check lightning-fast cache first!
        cached_response = url_scan_cache.get(request.url)
        if cached_response:
            logger.info(f"⚡ CACHE HIT: Retrieved scan for {request.url} instantly!")
            # Update dynamic fields
            cached_response['scan_time_ms'] = (time.time() - start_time) * 1000
            if ' (cached)' not in cached_response.get('scan_type', ''):
                cached_response['scan_type'] = str(cached_response.get('scan_type', '')) + " (cached)"
            return URLScanResponse(**cached_response)
            
        logger.info(f"Scanning URL: {request.url}")
        
        # Get predictor
        predictor = get_predictor()
        
        # Phase 1: Static URL Analysis
        prediction, confidence, features = predictor.predict(request.url)
        
        initial_scan_time = (time.time() - start_time) * 1000
        
        # Determine final prediction and confidence
        final_prediction = prediction
        final_confidence = confidence
        scan_type = "static"  # Default to static analysis
        deep_scan_result = None
        
        # Phase 2: ALWAYS PERFORM DEEP SCAN for any suspicious URL (>= 5% risk)
        # This is the user's vision: actually open the website and check the code!
        if confidence >= 0.05:  # Very low threshold - almost always trigger for ANY suspicion
            try:
                logger.info(f"🔍 Triggering DEEP CONTENT ANALYSIS (Static risk: {confidence:.2%})")
                logger.info("📡 Opening URL to inspect website code...")
                
                from app.content_analyzer import DeepScanner
                deep_scanner = DeepScanner()
                
                # Perform deep scan - actually visits the website!
                deep_scan_result = deep_scanner.perform_deep_scan(request.url, confidence)
                
                if deep_scan_result.get('scan_successful'):
                    scan_type = "deep_scan"
                    # Use combined risk score (static + content analysis)
                    final_confidence = deep_scan_result['combined_risk_score']
                    
                    # Update prediction based on combined score
                    if final_confidence >= 0.5:
                        final_prediction = "phishing"
                    else:
                        final_prediction = "safe"
                    
                    logger.info(f"✓ Deep scan complete. Final confidence: {final_confidence:.2%}")
                    logger.info(f"  - Critical findings: {len(deep_scan_result.get('critical_findings', []))}")
                    logger.info(f"  - High findings: {len(deep_scan_result.get('high_findings', []))}")
                
            except Exception as e:
                logger.warning(f"Deep scan failed, falling back to static analysis: {e}")
                # Continue with static analysis results
        else:
            logger.info(f"Static risk too low ({confidence:.2%}), skipping deep scan")
        
        # Calculate total scan time
        scan_time_ms = (time.time() - start_time) * 1000
        
        # Generate explanations (including deep scan evidence if available)
        explainer = ExplainabilityEngine()
        response = explainer.format_explanation_response(
            url=request.url,
            prediction=final_prediction,
            confidence=final_confidence,
            features=features,
            scan_time_ms=scan_time_ms
        )
        
        # Add deep scan evidence if available
        if deep_scan_result and deep_scan_result.get('scan_successful'):
            # Prepend critical findings from actual website analysis
            deep_reasons = deep_scan_result.get('detailed_reasons', [])
            response['reasons'] = deep_reasons + response['reasons']
            
            # Add metadata showing deep analysis was performed
            response['scan_type'] = scan_type
            response['content_analysis'] = {
                'performed': True,
                'website_visited': True,
                'code_analyzed': True,
                'critical_findings': len(deep_scan_result.get('critical_findings', [])),
                'high_findings': len(deep_scan_result.get('high_findings', [])),
                'medium_findings': len(deep_scan_result.get('medium_findings', [])),
                'evidence_available': True
            }
        else:
            response['scan_type'] = scan_type
            response['content_analysis'] = {
                'performed': False,
                'website_visited': False,
                'reason': f'Static risk score ({confidence:.1%}) below threshold (5%) or scan failed'
            }
        
        logger.info(f"Scan completed: {final_prediction} ({final_confidence:.4f}) in {scan_time_ms:.2f}ms [{scan_type}]")
        
        # Save to cache before returning
        url_scan_cache.set(request.url, response)
        
        return URLScanResponse(**response)
        
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Internal error during scan: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while scanning the URL"
        )


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint
    
    Returns:
        HealthResponse with API status and model availability
    """
    try:
        predictor = get_predictor()
        models_loaded = predictor.is_ready()
        
        return HealthResponse(
            status="healthy",
            version=settings.app_version,
            models_loaded=models_loaded
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="degraded",
            version=settings.app_version,
            models_loaded=False
        )


@router.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(request: FeedbackRequest):
    """
    Submit feedback for adaptive learning
    
    Args:
        request: FeedbackRequest with URL and correct label
        
    Returns:
        FeedbackResponse confirming feedback was recorded
    """
    try:
        logger.info(f"Feedback received for URL: {request.url}")
        logger.info(f"Predicted: {request.predicted_label}, Actual: {request.actual_label}")
        
        # TODO: Store feedback in database for retraining
        # For now, just log it
        
        return FeedbackResponse(
            message="Feedback recorded successfully. Thank you for helping improve our system!",
            feedback_id=None
        )
        
    except Exception as e:
        logger.error(f"Error recording feedback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to record feedback"
        )


@router.get("/stats")
async def get_stats():
    """
    Get system statistics (future enhancement)
    
    Returns:
        Dictionary with system statistics
    """
    return {
        "message": "Statistics endpoint - Coming soon",
        "total_scans": 0,
        "phishing_detected": 0,
        "legitimate_detected": 0
    }
