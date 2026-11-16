from app.models.predictor import get_predictor
import json
import logging

# Set loguru to only print errors to console to avoid clutter
from loguru import logger
import sys

logger.remove()
logger.add(sys.stderr, level="ERROR")

def predict_single():
    predictor = get_predictor()
    urls = [
        "http://google.com",
        "https://www.google.com",
        "http://ecnavi.jp",
        "https://linkedin.com",
        "http://paypal-security-update-now.com",
        "http://192.168.1.55/login"
    ]
    
    results = []
    for url in urls:
        pred, conf, feat = predictor.predict(url)
        # Re-extract the vector for viewing
        vec = predictor.feature_extractor.extract_feature_vector(url)
        
        # We manually call the ML model to get exact probabilities without rule overrides
        import numpy as np
        vec_np = np.array(vec).reshape(1, -1)
        proba = predictor.feature_classifier.predict_proba(vec_np)[0]
        
        results.append({
            "url": url,
            "prediction": pred,
            "confidence": conf,
            "ml_probabilities": {"legitimate": proba[0], "phishing": proba[1]},
            "vector": vec
        })
        
    with open("feature_dump.json", "w") as f:
        json.dump(results, f, indent=2)
        
if __name__ == "__main__":
    predict_single()
