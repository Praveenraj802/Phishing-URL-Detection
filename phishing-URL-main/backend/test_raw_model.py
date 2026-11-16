import joblib
import numpy as np
import pprint
from app.features.feature_extractor import URLFeatureExtractor
from app.core.config import settings
from pathlib import Path

def test_raw_models():
    model_dir = Path(settings.model_path)
    clf = joblib.load(model_dir / "feature_classifier.joblib")
    scaler = joblib.load(model_dir / "feature_scaler.joblib")
    extractor = URLFeatureExtractor()
    
    urls = [
        "http://google.com",
        "https://www.google.com",
        "http://ecnavi.jp"
    ]
    
    for url in urls:
        print(f"\n=== URL: {url} ===")
        features = extractor.extract_all_features(url)
        features_url = features['url'] if 'url' in features else ""
        print(f"Original URL: '{url}' | features['url']: '{features_url}'")
        
        feature_vector = extractor.extract_feature_vector(features_url)
        feature_vector = np.array(feature_vector).reshape(1, -1)
        
        scaled_array = scaler.transform(feature_vector)
        # print(f"Post-scale: {scaled_array[0][:5]}")
        
        # Predict
        proba = clf.predict_proba(scaled_array)[0]
        print(f"[{url}] Proba (Legit, Phish): [{proba[0]:.4f}, {proba[1]:.4f}]")

if __name__ == "__main__":
    test_raw_models()
