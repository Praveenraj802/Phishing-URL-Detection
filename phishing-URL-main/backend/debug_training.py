import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from app.features.feature_extractor import URLFeatureExtractor
import numpy as np
import time

def debug_training():
    url = "https://raw.githubusercontent.com/shreyagopal/Phishing-Website-Detection-by-Machine-Learning-Techniques/master/DataFiles/5.urldata.csv"
    print("Loading df...")
    df = pd.read_csv(url)
    extractor = URLFeatureExtractor()
    
    # Take a tiny sample to debug quickly
    df_sample = df.sample(500, random_state=42)
    domains = df_sample['Domain'].tolist()
    labels = df_sample['Label'].tolist()
    
    X = []
    y = []
    
    for d, l in zip(domains, labels):
        test_url = d if d.startswith("http") else "http://" + d
        try:
            vec = extractor.extract_feature_vector(test_url)
            X.append(vec)
            y.append(l)
        except:
            pass
            
    X = np.array(X)
    y = np.array(y)
    
    # The original training data had 'Label' = 1 for phishing, 0 for legitimate. Let's verify our feature extraction variance.
    print(f"Sampled {len(X)} instances. Targets: {np.bincount(y)}")
    
    clf = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
    
    clf.fit(X_train, y_train)
    
    print("\nFeature Importances:")
    importances = clf.feature_importances_
    for name, imp in zip(extractor.get_feature_names(), importances):
        if imp > 0.05:
            print(f"{name}: {imp:.4f}")
            
    # Test on google
    print("\nTesting google.com:")
    vec = extractor.extract_feature_vector("https://www.google.com")
    pred = clf.predict([vec])[0]
    prob = clf.predict_proba([vec])[0]
    print(f"Google prediction: {pred} | Prob: {prob}")

if __name__ == "__main__":
    debug_training()
