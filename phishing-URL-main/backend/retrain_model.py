import os
import sys
from pathlib import Path

# Add the backend directory to sys.path to ensure 'app' can be imported
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.append(str(backend_dir))

import os
import time
import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
import warnings

# Use the feature extractor
from app.features.feature_extractor import URLFeatureExtractor
from app.core.config import settings

import warnings
from sklearn.preprocessing import StandardScaler

def retrain_from_dataset():
    extractor = URLFeatureExtractor()
    print("Loading 10k dataset from URL...")
    url = "https://raw.githubusercontent.com/shreyagopal/Phishing-Website-Detection-by-Machine-Learning-Techniques/master/DataFiles/5.urldata.csv"
    try:
        df = pd.read_csv(url)
    except Exception as e:
        print(f"Failed to load dataset: {e}")
        return

    domains = df['Domain'].tolist()
    labels = df['Label'].tolist()  # 1 for Phishing, 0 for Legitimate

    print(f"Loaded {len(domains)} URLs. Extracting features for all. This will take some time...")

    X = []
    y = []
    failed = 0

    start_time = time.time()
    for i, (domain, label) in enumerate(zip(domains, labels)):
        if i > 0 and i % 1000 == 0:
            print(f"Extracted {i}/{len(domains)} URLs...")
            
        # Ensure scheme is prepended for proper parsing
        test_url = domain
        if not test_url.startswith("http"):
            test_url = "http://" + domain

        try:
            # We use extract_feature_vector which returns a list ordered exactly by get_feature_names()
            vector = extractor.extract_feature_vector(test_url)
            X.append(vector)
            y.append(label)
        except Exception as e:
            failed += 1
            
    extract_time = time.time() - start_time
    print(f"Feature Extraction Complete in {extract_time:.2f}s! ({failed} failures, {len(X)} success)")

    X = np.array(X)
    y = np.array(y)
    
    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    print("\nTraining RandomForestClassifier ...")
    # Removing 'balanced_subsample' because it clearly exploded the False Positive rates on this particular dataset
    clf = RandomForestClassifier(
        n_estimators=100, 
        max_depth=15, 
        random_state=42, 
        n_jobs=-1
    )

    # Split to test locally first
    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42, stratify=y)
    
    clf.fit(X_train, y_train)
    
    y_pred = clf.predict(X_test)
    print("\nInternal Validation Results:")
    print(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}")
    print("\nConfusion Matrix:")
    print(confusion_matrix(y_test, y_pred))
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))

    # Now, train on ALL data for the final model
    print("\nTraining final model on full dataset...")
    final_clf = RandomForestClassifier(
        n_estimators=100, 
        max_depth=15, 
        random_state=42, 
        n_jobs=-1
    )
    final_clf.fit(X_scaled, y)

    # Save the model
    model_dir = Path(settings.model_path)
    model_dir.mkdir(parents=True, exist_ok=True)
    classifier_path = model_dir / settings.feature_classifier_name
    
    print(f"Saving new model to: {classifier_path}")
    joblib.dump(final_clf, classifier_path)
    
    scaler_path = model_dir / "feature_scaler.joblib"
    print(f"Saving scaler to: {scaler_path}")
    joblib.dump(scaler, scaler_path)
    
    print("Done! Ready for blast testing!")

if __name__ == "__main__":
    retrain_from_dataset()
