"""
Hybrid Model Inference Engine
Combines LSTM and feature-based classifier predictions
"""

import os
import time
import json
import urllib.request
from pathlib import Path
from typing import Dict, Any, Tuple
import numpy as np
import joblib

from loguru import logger
from app.core.config import settings
from app.features.feature_extractor import URLFeatureExtractor
from app.services.threat_intel import intel_service


class HybridModelPredictor:
    """Hybrid model combining LSTM and feature-based classifier"""
    
    def __init__(self):
        """Initialize the hybrid model predictor"""
        self.feature_extractor = URLFeatureExtractor()
        self.feature_classifier = None
        self.feature_scaler = None
        self.lstm_model = None
        self.models_loaded = False
        
        # Model weights for ensemble
        self.feature_classifier_weight = 0.6
        self.lstm_weight = 0.4
        
        # Load models if available
        self._load_models()
    
    def _load_models(self):
        """Load trained models from disk"""
        try:
            model_dir = Path(settings.model_path)
            
            # Load feature-based classifier (prefer XGBoost)
            xgb_path = model_dir / "xgboost_classifier.joblib"
            classifier_path = model_dir / settings.feature_classifier_name
            
            if xgb_path.exists():
                self.feature_classifier = joblib.load(xgb_path)
                logger.info(f"Loaded XGBoost feature classifier from {xgb_path}")
            elif classifier_path.exists():
                self.feature_classifier = joblib.load(classifier_path)
                logger.info(f"Loaded Random Forest classifier from {classifier_path}")
            else:
                logger.warning(f"Feature classifiers not found at {xgb_path} or {classifier_path}")
                
            # Load the newly added feature scaler
            scaler_path = model_dir / "feature_scaler.joblib"
            if scaler_path.exists():
                self.feature_scaler = joblib.load(scaler_path)
                logger.info(f"Loaded feature scaler from {scaler_path}")
            else:
                self.feature_scaler = None
                logger.warning(f"Feature scaler not found at {scaler_path}")
            
            # Load Deep NLP LSTM model (if available)
            lstm_path = model_dir / 'lstm_model.h5'
            tokenizer_path = model_dir / 'lstm_tokenizer.pickle'
            
            if lstm_path.exists() and tokenizer_path.exists():
                try:
                    import tensorflow as tf
                    import pickle
                    self.lstm_model = tf.keras.models.load_model(str(lstm_path))
                    with open(tokenizer_path, 'rb') as handle:
                        self.lstm_tokenizer = pickle.load(handle)
                    logger.info(f"Loaded TensorFlow Keras LSTM from {lstm_path}")
                except Exception as e:
                    logger.warning(f"LSTM Engine failed to load (run 'pip install tensorflow'): {e}")
            else:
                logger.warning(f"Deep NLP LSTM Engine not found at {lstm_path}")
            
            # Check if at least one model is loaded
            if self.feature_classifier is not None:
                self.models_loaded = True
                logger.info("Models loaded successfully")
            else:
                logger.warning("No models loaded - using rule-based fallback")
                
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            self.models_loaded = False
    
    def predict(self, url: str) -> Tuple[str, float, Dict[str, Any]]:
        """
        Predict if URL is phishing or legitimate
        
        Args:
            url: The URL to analyze
            
        Returns:
            Tuple of (prediction, confidence, features)
            - prediction: 'phishing' or 'legitimate'
            - confidence: Confidence score (0-1)
            - features: Extracted features dictionary
        """
        start_time = time.time()
        
        # ZERO-DAY THREAT INTEL: Check Google Safe Browsing before any ML
        is_threat = intel_service.check_url(url)
        if is_threat is True:
            logger.error(f"ZERO-DAY DEFENSE: {url} is a verified phishing threat on Google Safe Browsing!")
            return (
                "phishing", 
                0.99, 
                {
                    'url': url,
                    'flagged_by_safe_browsing': True,
                    'analysis_time_ms': round((time.time() - start_time) * 1000, 2)
                }
            )
        
        # Extract features - if URL is invalid, treat as phishing!
        try:
            features = self.feature_extractor.extract_all_features(url)
        except ValueError as e:
            # Invalid URL format = suspicious = PHISHING!
            logger.warning(f"Invalid URL format detected: {url} - Marking as phishing")
            
            # Return phishing with high confidence
            # Invalid URLs are extremely suspicious
            return (
                "phishing",
                0.95,  # 95% confidence - invalid format is very suspicious
                {
                    'url': url,
                    'invalid_format': True,
                    'error_reason': str(e)
                }
            )
        except Exception as e:
            logger.error(f"Unexpected error during feature extraction: {e}")
            raise ValueError(f"Failed to process URL: {str(e)}")
        
        # Get predictions from available models
        if self.models_loaded and self.feature_classifier is not None:
            # Use trained model
            prediction_ml, confidence_ml = self._predict_with_models(features, url)
            logger.info(f"ML ENGINE RET: {prediction_ml} | Conf: {confidence_ml}")
            
            # ALSO get rule-based predictions
            prediction_rb, confidence_rb = self._rule_based_prediction(features)
            logger.info(f"RB ENGINE RET: {prediction_rb} | Conf: {confidence_rb}")
            
            # HYBRID ENSEMBLE LOGIC:
            if prediction_rb == 'phishing' and confidence_rb >= 0.70:
                logger.warning(f"Rule-based engine OVERRIDE: Phishing detected with high confidence ({confidence_rb:.2f})")
                prediction = 'phishing'
                confidence = max(confidence_ml, confidence_rb)
            else:
                prediction = prediction_ml
                confidence = confidence_ml
        else:
            # Fallback to pure rule-based detection
            logger.warning("Using rule-based fallback for prediction")
            prediction, confidence = self._rule_based_prediction(features)
        
        inference_time = (time.time() - start_time) * 1000  # Convert to ms
        logger.info(f"Prediction: {prediction} (confidence: {confidence:.4f}) in {inference_time:.2f}ms")
        
        return prediction, confidence, features
    
    def _predict_with_models(self, features: Dict[str, Any], url: str) -> Tuple[str, float]:
        """
        Make prediction using trained models
        
        Args:
            features: Extracted features
            url: The original URL string
            
        Returns:
            Tuple of (prediction, confidence)
        """
        # Prepare feature vector
        feature_vector_full = self.feature_extractor.extract_feature_vector(url)
        
        # SHIM: In case model is still 35 features but extractor is 40
        try:
            expected_features = self.feature_classifier.n_features_in_
            if expected_features < len(feature_vector_full):
                feature_vector = feature_vector_full[:expected_features]
                logger.info(f"SHIM: Downsized {len(feature_vector_full)} features to {expected_features}")
            else:
                feature_vector = feature_vector_full
        except AttributeError:
            feature_vector = feature_vector_full[:35]
            
        feature_vector = np.array(feature_vector).reshape(1, -1)
        
        # Apply scaling if the scaler was loaded
        if self.feature_scaler:
            feature_vector = self.feature_scaler.transform(feature_vector)
        
        logger.info(f"Feature vector shape: {feature_vector.shape}")
        logger.info(f"Feature vector sample: {feature_vector[0][:5]} ...")
        
        # Get prediction from feature classifier
        classifier_proba = self.feature_classifier.predict_proba(feature_vector)[0]
        logger.info(f"Classifier raw proba: {classifier_proba}")
        classifier_confidence = classifier_proba[1]  # Probability of phishing class
        
        # If LSTM is available, run ensemble prediction
        if self.lstm_model is not None and hasattr(self, 'lstm_tokenizer'):
            try:
                from tensorflow.keras.preprocessing.sequence import pad_sequences
                seq = self.lstm_tokenizer.texts_to_sequences([url])
                pad_seq = pad_sequences(seq, maxlen=150)
                lstm_confidence = float(self.lstm_model.predict(pad_seq, verbose=0)[0][0])
                logger.info(f"🧠 Deep NLP LSTM Confidence: {lstm_confidence:.4f}")
                
                # Ensemble: 70% XGBoost, 30% LSTM Sequence Model
                classifier_confidence = (classifier_confidence * 0.7) + (lstm_confidence * 0.3)
                logger.info(f"🔗 Hybrid Ensemble Confidence: {classifier_confidence:.4f}")
            except Exception as e:
                logger.warning(f"LSTM Neural Network inference failed: {e}")
                
        # Make final classification
        prediction = 'phishing' if classifier_confidence >= 0.5 else 'legitimate'
        
        return prediction, float(classifier_confidence)
    
    def _rule_based_prediction(self, features: Dict[str, Any]) -> Tuple[str, float]:
        """
        Rule-based fallback prediction when models are not available
        Enhanced to be more aggressive in detecting phishing
        
        Args:
            features: Extracted features
            
        Returns:
            Tuple of (prediction, confidence)
        """
        suspicious_score = 0
        max_score = 15  # Increased for more granular scoring
        
        # CRITICAL: Typosquatting detection - INSTANT PHISHING VERDICT
        is_typosquatting = features.get('is_typosquatting', 0) == 1
        if is_typosquatting:
            # Typosquatting is ALWAYS phishing - return immediately with high confidence
            logger.warning(f"Typosquatting detected - automatic phishing verdict")
            return 'phishing', 0.85  # High confidence - it's definitely fake
            
        # CRITICAL: Dead Domain detection (No A Record)
        # Note: If it's an IP, it gets has_a_record=1 so it skips this check
        if features.get('has_a_record', 1) == 0:
            logger.warning(f"Domain does not resolve (No A record) - likely dead threat or fake.")
            return 'phishing', 0.80
            
        # VERY HIGH RISK: No Mail servers + Any suspicious keywords
        if features.get('has_mx_record', 1) == 0 and features.get('num_suspicious_keywords', 0) > 0:
            suspicious_score += 5 # No mail server for a "login" or "secure" page is incredibly fake

        # High-risk indicators (3 points each)
        if features.get('has_ip_address', 0) == 1:
            suspicious_score += 3  # Very suspicious
        
        # Medium-risk indicators (2 points each)
        if features.get('is_https', 0) == 0:
            suspicious_score += 2  # No HTTPS is risky
        
        if features.get('num_suspicious_keywords', 0) > 0:
            # More keywords = higher risk
            suspicious_score += min(features['num_suspicious_keywords'], 3) * 2
        
        if features.get('is_url_shortener', 0) == 1:
            suspicious_score += 2
        
        if features.get('domain_has_hyphens', 0) == 1 and features.get('num_suspicious_keywords', 0) > 0:
            suspicious_score += 2  # Hyphen + suspicious keyword combination
        
        # Low-risk indicators (1 point each)
        if features.get('long_url', 0) == 1:
            suspicious_score += 1
        
        if features.get('num_subdomains', 0) > 2:
            suspicious_score += min(features['num_subdomains'] - 2, 2)  # More subdomains = more suspicious
        
        if features.get('excessive_dots', 0) == 1:
            suspicious_score += 1
        
        if features.get('excessive_hyphens', 0) == 1:
            suspicious_score += 1
        
        if features.get('has_port', 0) == 1:
            suspicious_score += 1
        
        if features.get('domain_has_digits', 0) == 1:
            suspicious_score += 1
        
        # High entropy suggests obfuscation
        if features.get('url_entropy', 0) > 4.0:
            suspicious_score += 1
        
        # Calculate confidence based on score
        confidence = suspicious_score / max_score
        
        # INCREASE threshold for phishing detection (was way too aggressive at 0.30)
        # Even legit sites have hyphens or a few path elements.
        threshold = 0.50 
        
        # Boost confidence if multiple red flags
        if suspicious_score >= 8:
            confidence = max(confidence, 0.75)  # High confidence for multiple flags
        
        # Ensure reasonable confidence range
        confidence = max(0.15, min(0.95, confidence))
        
        # DEBUG LOGGER
        logger.info(f"Rule-based scored {suspicious_score}/{max_score} -> Confidence: {confidence:.2f}")
        
        prediction = 'phishing' if confidence > threshold else 'legitimate'
        
        return prediction, confidence
    
    def is_ready(self) -> bool:
        """Check if models are loaded and ready"""
        return self.models_loaded or True  # True because rule-based fallback is always available


# Global predictor instance
_predictor_instance = None


def get_predictor() -> HybridModelPredictor:
    """Get or create global predictor instance"""
    global _predictor_instance
    if _predictor_instance is None:
        _predictor_instance = HybridModelPredictor()
    return _predictor_instance
