import joblib
import numpy as np
from app.features.feature_extractor import URLFeatureExtractor
from app.core.config import settings
from pathlib import Path

def test():
    model_dir = Path(settings.model_path)
    clf = joblib.load(model_dir / "feature_classifier.joblib")
    scaler = joblib.load(model_dir / "feature_scaler.joblib")
    
    urls = [
        "http://google.com",
        "https://www.google.com",
        "http://ecnavi.jp",
        "http://paypal-security-update-now.com"
    ]
    
    for url in urls:
        extractor = URLFeatureExtractor() # FRESH INSTANCE EVERY TIME
        
        # Method A: Direct
        feat_A = extractor.extract_feature_vector(url)
        scaled_A = scaler.transform([feat_A])
        prob_A = clf.predict_proba(scaled_A)[0]
        
        # Method B: Indirect (Like predictor.py)
        extractor2 = URLFeatureExtractor()
        features = extractor2.extract_all_features(url)
        feat_B = extractor2.extract_feature_vector(features['url'])
        scaled_B = scaler.transform([feat_B])
        prob_B = clf.predict_proba(scaled_B)[0]
        
        print(f"[{url}]")
        print(f"  Method A (Direct): {prob_A[1]:.4f} Phishing")
        print(f"  Method B (Indirect): {prob_B[1]:.4f} Phishing")
        print(f"  Match? {feat_A == feat_B}")
        
if __name__ == "__main__":
    test()
