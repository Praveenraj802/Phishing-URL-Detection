"""
Train Feature-Based Classifier
Random Forest model for phishing detection
"""

import sys
from pathlib import Path
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, precision_recall_fscore_support
import xgboost as xgb

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.core.logging import app_logger as logger


def load_data(data_dir='ml/data'):
    """Load prepared dataset"""
    logger.info(f"Loading dataset from {data_dir}...")
    
    data_path = Path(data_dir)
    
    X_train = np.load(data_path / 'X_train.npy')
    y_train = np.load(data_path / 'y_train.npy')
    X_val = np.load(data_path / 'X_val.npy')
    y_val = np.load(data_path / 'y_val.npy')
    X_test = np.load(data_path / 'X_test.npy')
    y_test = np.load(data_path / 'y_test.npy')
    
    logger.info(f"Loaded {len(X_train)} training samples")
    logger.info(f"Loaded {len(X_val)} validation samples")
    logger.info(f"Loaded {len(X_test)} test samples")
    
    return X_train, y_train, X_val, y_val, X_test, y_test


def train_random_forest(X_train, y_train, X_val, y_val):
    """
    Train Random Forest classifier
    
    Args:
        X_train, y_train: Training data
        X_val, y_val: Validation data
        
    Returns:
        Trained model
    """
    logger.info("Training Random Forest classifier...")
    
    # Initialize model
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1,
        class_weight='balanced'  # Handle class imbalance
    )
    
    # Train model
    model.fit(X_train, y_train)
    
    # Evaluate on validation set
    y_val_pred = model.predict(X_val)
    val_accuracy = accuracy_score(y_val, y_val_pred)
    
    logger.info(f"Validation Accuracy: {val_accuracy:.4f}")
    
    return model


def train_xgboost(X_train, y_train, X_val, y_val):
    """
    Train XGBoost classifier
    
    Args:
        X_train, y_train: Training data
        X_val, y_val: Validation data
        
    Returns:
        Trained model
    """
    logger.info("Training XGBoost classifier...")
    
    # Calculate scale_pos_weight for imbalanced data
    scale_pos_weight = len(y_train[y_train == 0]) / len(y_train[y_train == 1])
    
    # Initialize model
    model = xgb.XGBClassifier(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        scale_pos_weight=scale_pos_weight,
        random_state=42,
        n_jobs=-1
    )
    
    # Train model
    model.fit(
        X_train, y_train,
        eval_set=[(X_val, y_val)],
        verbose=False
    )
    
    # Evaluate on validation set
    y_val_pred = model.predict(X_val)
    val_accuracy = accuracy_score(y_val, y_val_pred)
    
    logger.info(f"Validation Accuracy: {val_accuracy:.4f}")
    
    return model


def evaluate_model(model, X_test, y_test):
    """
    Evaluate model on test set
    
    Args:
        model: Trained model
        X_test, y_test: Test data
    """
    logger.info("\n" + "="*60)
    logger.info("EVALUATION ON TEST SET")
    logger.info("="*60)
    
    # Predictions
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)
    
    # Accuracy
    accuracy = accuracy_score(y_test, y_pred)
    logger.info(f"\nAccuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
    
    # Precision, Recall, F1-Score
    precision, recall, f1, _ = precision_recall_fscore_support(y_test, y_pred, average='binary')
    logger.info(f"Precision: {precision:.4f}")
    logger.info(f"Recall: {recall:.4f}")
    logger.info(f"F1-Score: {f1:.4f}")
    
    # Confusion Matrix
    cm = confusion_matrix(y_test, y_pred)
    logger.info(f"\nConfusion Matrix:")
    logger.info(f"  TN: {cm[0,0]}, FP: {cm[0,1]}")
    logger.info(f"  FN: {cm[1,0]}, TP: {cm[1,1]}")
    
    # Classification Report
    logger.info(f"\nClassification Report:")
    logger.info("\n" + classification_report(y_test, y_pred, target_names=['Legitimate', 'Phishing']))
    
    return {
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'confusion_matrix': cm
    }


def save_model(model, model_path='models/feature_classifier.joblib'):
    """Save trained model"""
    model_dir = Path(model_path).parent
    model_dir.mkdir(parents=True, exist_ok=True)
    
    joblib.dump(model, model_path)
    logger.info(f"Model saved to {model_path}")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("PHISHING URL DETECTOR - MODEL TRAINING")
    print("="*60 + "\n")
    
    # Load data
    X_train, y_train, X_val, y_val, X_test, y_test = load_data()
    
    # Train both models and compare
    print("\n--- Training Random Forest ---")
    rf_model = train_random_forest(X_train, y_train, X_val, y_val)
    rf_metrics = evaluate_model(rf_model, X_test, y_test)
    
    print("\n--- Training XGBoost ---")
    xgb_model = train_xgboost(X_train, y_train, X_val, y_val)
    xgb_metrics = evaluate_model(xgb_model, X_test, y_test)
    
    # Select best model
    if xgb_metrics['f1'] > rf_metrics['f1']:
        best_model = xgb_model
        best_model_name = "XGBoost"
    else:
        best_model = rf_model
        best_model_name = "Random Forest"
    
    print(f"\n✓ Best Model: {best_model_name}")
    
    # Save best model
    save_model(best_model)
    
    print("\n✓ Training complete! Model ready for use.")
