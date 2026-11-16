from app.models.predictor import get_predictor

def predict_single():
    predictor = get_predictor()
    urls = [
        "http://google.com",
        "https://www.google.com",
        "http://ecnavi.jp"
    ]
    
    for url in urls:
        print(f"\nEvaluating: {url}")
        pred, conf, feat = predictor.predict(url)
        if isinstance(pred, tuple):
            print(f"Prediction tuple?: {pred}")
        else:
            print(f"Prediction: {pred} | Confidence: {conf}")
        print("Extracted features sample:")
        for k in list(feat.keys())[:10]:
            print(f"  {k}: {feat[k]}")
    
if __name__ == "__main__":
    predict_single()
