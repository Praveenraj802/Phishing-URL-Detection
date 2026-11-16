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
import warnings
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import StratifiedKFold
import xgboost as xgb
import lightgbm as lgb
import optuna

from app.features.feature_extractor import URLFeatureExtractor
from app.core.config import settings

def load_or_extract_features():
    """Extract features or load from cache if already extracted"""
    cache_dir = Path("models/dataset_cache")
    cache_dir.mkdir(parents=True, exist_ok=True)
    
    x_cache = cache_dir / "X_10k.npy"
    y_cache = cache_dir / "y_10k.npy"
    
    if x_cache.exists() and y_cache.exists():
        print("Loading cached features from models/dataset_cache...")
        return np.load(x_cache), np.load(y_cache)
        
    print("Cache not found. Extracting 10k dataset from URL...")
    extractor = URLFeatureExtractor()
    url = "https://raw.githubusercontent.com/shreyagopal/Phishing-Website-Detection-by-Machine-Learning-Techniques/master/DataFiles/5.urldata.csv"
    try:
        df = pd.read_csv(url)
    except Exception as e:
        print(f"Failed to load dataset: {e}")
        return None, None

    domains = df['Domain'].tolist()
    labels = df['Label'].tolist()  # 1 for Phishing, 0 for Legitimate

    print(f"Loaded {len(domains)} URLs. Extracting features... This takes ~3 mins.")
    X = []
    y = []
    failed = 0

    start_time = time.time()
    for i, (domain, label) in enumerate(zip(domains, labels)):
        if i > 0 and i % 1000 == 0:
            print(f"Extracted {i}/{len(domains)} URLs...")
            
        test_url = domain if domain.startswith("http") else "http://" + domain

        try:
            vector = extractor.extract_feature_vector(test_url)
            X.append(vector)
            y.append(label)
        except Exception as e:
            failed += 1
            
    print(f"Extraction Complete in {time.time() - start_time:.2f}s! ({failed} failures)")
    
    X = np.array(X)
    y = np.array(y)
    
    # Save cache
    np.save(x_cache, X)
    np.save(y_cache, y)
    
    return X, y

def objective(trial, X_scaled, y):
    """Optuna objective for XGBoost"""
    param = {
        'verbosity': 0,
        'objective': 'binary:logistic',
        'eval_metric': 'logloss',
        'booster': 'gbtree',
        'learning_rate': trial.suggest_float('learning_rate', 1e-3, 0.3, log=True),
        'max_depth': trial.suggest_int('max_depth', 3, 15),
        'min_child_weight': trial.suggest_int('min_child_weight', 1, 10),
        'subsample': trial.suggest_float('subsample', 0.5, 1.0),
        'colsample_bytree': trial.suggest_float('colsample_bytree', 0.5, 1.0),
        'gamma': trial.suggest_float('gamma', 0.0, 5.0),
        'n_estimators': trial.suggest_int('n_estimators', 100, 1000),
        'early_stopping_rounds': 50
    }

    # Use Stratified K-Fold cross validation
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    scores = []
    
    for train_idx, val_idx in cv.split(X_scaled, y):
        X_train, X_val = X_scaled[train_idx], X_scaled[val_idx]
        y_train, y_val = y[train_idx], y[val_idx]
        
        model = xgb.XGBClassifier(**param, random_state=42)
        model.fit(X_train, y_train, 
                  eval_set=[(X_val, y_val)], 
                  verbose=False)
        
        # We optimize for negative log loss or F1 score. 
        # For simplicity, we'll just check accuracy on the validation set
        score = model.score(X_val, y_val)
        scores.append(score)

    return np.mean(scores)

def main():
    X, y = load_or_extract_features()
    if X is None:
        return
        
    print(f"Dataset shape: {X.shape}, {y.shape}")
    
    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # We will save the scaler so we don't accidentally use the old random forest scaler
    model_dir = Path(settings.model_path)
    model_dir.mkdir(parents=True, exist_ok=True)
    scaler_path = model_dir / "feature_scaler.joblib"
    joblib.dump(scaler, scaler_path)
    print(f"Saved new scaler to {scaler_path}")
    
    # Run Optuna Hyperparameter Tuning
    print("Starting Optuna Hyperparameter Tuning for XGBoost...")
    study = optuna.create_study(direction='maximize')
    # Run 20 trials for speed, increase for better precision
    study.optimize(lambda trial: objective(trial, X_scaled, y), n_trials=30)
    
    print('Number of finished trials:', len(study.trials))
    print('Best trial:', study.best_trial.params)
    print(f"Best cross-validation accuracy: {study.best_trial.value:.4f}")
    
    # Train finalized model on ALL data
    print("Training final XGBoost model on all data with best parameters...")
    final_params = study.best_trial.params
    final_params['objective'] = 'binary:logistic'
    final_params['eval_metric'] = 'logloss'
    final_params['random_state'] = 42
    
    final_model = xgb.XGBClassifier(**final_params)
    final_model.fit(X_scaled, y)
    
    # Evaluate on the training set just to see training accuracy
    y_pred = final_model.predict(X_scaled)
    train_acc = np.mean(y_pred == y)
    print(f"Final Model Training Accuracy: {train_acc:.4f}")
    
    # Save the model
    model_path = model_dir / "xgboost_classifier.joblib"
    joblib.dump(final_model, model_path)
    print(f"Saved optimal XGBoost model to {model_path}")

if __name__ == "__main__":
    main()
