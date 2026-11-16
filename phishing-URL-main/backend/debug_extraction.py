import os
import sys
from pathlib import Path

# Add the backend directory to sys.path to ensure 'app' can be imported
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.append(str(backend_dir))

import pandas as pd
from app.features.feature_extractor import URLFeatureExtractor
import numpy as np

def analyze():
    url = "https://raw.githubusercontent.com/shreyagopal/Phishing-Website-Detection-by-Machine-Learning-Techniques/master/DataFiles/5.urldata.csv"
    print("Loading df...")
    df = pd.read_csv(url)
    extractor = URLFeatureExtractor()
    
    # Just grab first 10
    legit_domains = df[df['Label'] == 0]['Domain'].head(10).tolist()
    phish_domains = df[df['Label'] == 1]['Domain'].tail(10).tolist()
    
    print("--- LEGIT DOMAINS ---")
    for d in legit_domains:
        test_url = d if d.startswith("http") else "http://" + d
        vec = extractor.extract_feature_vector(test_url)
        print(d)
        
    print("\n--- PHISHING DOMAINS ---")
    for d in phish_domains:
        test_url = d if d.startswith("http") else "http://" + d
        vec = extractor.extract_feature_vector(test_url)
        print(d)
        
if __name__ == "__main__":
    analyze()
