import os

def generate():
    with open('backend/app/features/feature_extractor.py', 'r', encoding='utf-8') as f:
        extractor = f.read()

    clean_lines = []
    for line in extractor.split('\n'):
        if 'from app.core.logging' in line or 'from loguru' in line:
            continue
        if 'if __name__ ==' in line:
            break
        clean_lines.append(line)
    extractor_clean = '\n'.join(clean_lines)

    script = f'''# ==========================================
# PHISHING URL MODEL TRAINING - KAGGLE
# ==========================================

# --- STEP 1: AUTO-INSTALL MISSING PACKAGES ---
import subprocess
import sys

print("Installing missing packages (tldextract, validators, dnspython, etc). Please wait...")
subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "tldextract", "validators", "dnspython", "xgboost", "tqdm"])
print("Packages installed successfully!")

# --- STEP 2: DO THE IMPORTS ---
import os
import re
import math
import tldextract
import validators
import dns.resolver
from urllib.parse import urlparse, parse_qs
from collections import Counter
import pandas as pd
import numpy as np
import joblib
from tqdm.notebook import tqdm
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import xgboost as xgb
import logging

logger = logging.getLogger('kaggle')
logger.setLevel(logging.INFO)

# --- STEP 3: FEATURE EXTRACTOR LOGIC ---
{extractor_clean}

# --- STEP 4: DATASET LOADING ---
def load_kaggle_dataset():
    print("Looking for datasets in /kaggle/input...")
    dataset_path = None
    for root, dirs, files in os.walk('/kaggle/input'):
        for file in files:
            if file.endswith('.csv'):
                dataset_path = os.path.join(root, file)
                print(f"Found dataset: {{dataset_path}}")
                break
        if dataset_path:
            break
    
    if not dataset_path:
        print("\\n===========================")
        print("CRITICAL ERROR: DATASET NOT FOUND!")
        print("You must click '+ Add Data' on the right panel and search for: web-page-phishing-detection-dataset")
        print("===========================\\n")
        raise FileNotFoundError("Dataset missing.")
    
    df = pd.read_csv(dataset_path)
    print(f"Loaded dataset with {{len(df)}} rows.")
    
    url_col, label_col = None, None
    for col in df.columns:
        if 'url' in col.lower() or 'link' in col.lower(): url_col = col
        if 'label' in col.lower() or 'class' in col.lower() or 'target' in col.lower() or 'status' in col.lower(): label_col = col
        
    if not url_col or not label_col:
        print(f"ERROR: Could not find URL or Label column in: {{df.columns.tolist()}}")
        raise ValueError("Missing required columns in dataset.")
        
    df_clean = pd.DataFrame({{'url': df[url_col].astype(str), 'label': df[label_col]}})
    df_clean['label'] = df_clean['label'].apply(lambda x: 1 if str(x).lower() in ['1', 'phishing', 'bad'] else 0)
    
    # Keep it balanced and fast for this run (15000 each)
    phishing = df_clean[df_clean['label'] == 1]
    legit = df_clean[df_clean['label'] == 0]
    n_samples = min(len(phishing), len(legit), 15000)
    
    balanced = pd.concat([phishing.sample(n=n_samples, random_state=42), legit.sample(n=n_samples, random_state=42)])
    return balanced.sample(frac=1, random_state=42).reset_index(drop=True)

df = load_kaggle_dataset()

# --- STEP 5: FEATURE EXTRACTION ---
print("Extracting 40 robust features for 30,000 URLs (Takes ~2-3 minutes)...")
extractor = URLFeatureExtractor()
X_list, y_list = [], []

for idx, row in tqdm(df.iterrows(), total=len(df)):
    try:
        features = extractor.extract_feature_vector(row['url'])
        X_list.append(features)
        y_list.append(row['label'])
    except Exception:
        pass

X = np.array(X_list)
y = np.array(y_list)
print(f"Built dataset matrix: {{X.shape}}")

# --- STEP 6: TRAINING MODELS ---
print("Training Models...")
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

xgb_model = xgb.XGBClassifier(n_estimators=150, max_depth=8, learning_rate=0.1, random_state=42, n_jobs=-1)
xgb_model.fit(X_train, y_train)
xgb_preds = xgb_model.predict(X_test)
print("--- XGBoost Accuracy ---")
print(accuracy_score(y_test, xgb_preds))

joblib.dump(xgb_model, 'feature_classifier.joblib')
print("\\n=======================================================")
print("SUCCESS! Model saved as feature_classifier.joblib!")
print("Refresh the right Output panel and download the file!")
print("=======================================================\\n")
'''

    with open('single_cell_kaggle.txt', 'w', encoding='utf-8') as out:
        out.write(script)
    print("Successfully created single_cell_kaggle.txt")

if __name__ == "__main__":
    generate()
