from app.features.feature_extractor import URLFeatureExtractor

def debug_rule():
    extractor = URLFeatureExtractor()
    url = "https://www.google.com"
    features = extractor.extract_all_features(url)
    
    print("\nFeatures:")
    for k, v in features.items():
        print(f"{k}: {v}")
        
    from app.models.predictor import get_predictor
    predictor = get_predictor()
    pred, conf = predictor._rule_based_prediction(features)
    print(f"\nRule Pred: {pred} | Conf: {conf}")

if __name__ == "__main__":
    debug_rule()
