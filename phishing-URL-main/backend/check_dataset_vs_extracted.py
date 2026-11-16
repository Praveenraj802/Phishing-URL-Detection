import os
import sys
from pathlib import Path

# Add the backend directory to sys.path to ensure 'app' can be imported
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.append(str(backend_dir))

import pandas as pd
from app.features.feature_extractor import URLFeatureExtractor

def check_raw_vs_extracted():
    url = "https://raw.githubusercontent.com/shreyagopal/Phishing-Website-Detection-by-Machine-Learning-Techniques/master/DataFiles/5.urldata.csv"
    df = pd.read_csv(url)
    
    extractor = URLFeatureExtractor()
    sample = "http://google.com"
    vec = extractor.extract_feature_vector(sample)
    
    print("My Extracted Vectors (first 5):", vec[:5])
    print("\nDataset Vector (first row):")
    print(df.iloc[0].values)
    
if __name__ == "__main__":
    check_raw_vs_extracted()
