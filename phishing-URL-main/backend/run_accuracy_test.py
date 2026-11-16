import os
import sys
from pathlib import Path

# Add the backend directory to sys.path to ensure 'app' can be imported
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.append(str(backend_dir))

import time
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from app.models.predictor import get_predictor
from app.core.config import settings
from loguru import logger
import json

# Suppress debug logs from app to speed up the test
logger.remove()

def run_test():
    print("Loading dataset...")
    url = "https://raw.githubusercontent.com/shreyagopal/Phishing-Website-Detection-by-Machine-Learning-Techniques/master/DataFiles/5.urldata.csv"
    df = pd.read_csv(url)
    
    # Dataset has 'Domain' and 'Label' (0 = legit, 1 = phishing)
    domains = df['Domain'].tolist()
    labels = df['Label'].tolist()
    
    print(f"Loaded {len(domains)} URLs.")
    print("Initializing predictor...")
    
    predictor = get_predictor()
    if not predictor.is_ready():
        print("Model failed to load, using fallback.")
    else:
        print("Model loaded successfully.")
    
    true_positives = 0
    false_positives = 0
    true_negatives = 0
    false_negatives = 0
    errors = 0
    
    total = len(domains)
    print(f"Starting test on {total} URLs...")
    start_time = time.time()
    
    # Process synchronously first to avoid GIL/thread overhead if not needed
    # Or batch them
    for i, (domain, true_label) in enumerate(zip(domains, labels)):
        if i > 0 and i % 1000 == 0:
            print(f"Processed {i}/{total}...")
        
        # Prepend scheme if missing (so urlparse works)
        # Assuming most from this dataset are domains
        test_url = domain
        if not test_url.startswith("http"):
            test_url = "http://" + domain
            
        try:
            pred_str, conf, _ = predictor.predict(test_url)
            # pred_str is 'phishing' or 'legitimate'
            pred_label = 1 if pred_str == 'phishing' else 0
            
            if pred_label == 1 and true_label == 1:
                true_positives += 1
            elif pred_label == 1 and true_label == 0:
                false_positives += 1
            elif pred_label == 0 and true_label == 0:
                true_negatives += 1
            elif pred_label == 0 and true_label == 1:
                false_negatives += 1
                
        except Exception as e:
            errors += 1
            
    end_time = time.time()
    
    print("\n--- TEST RESULTS ---")
    print(f"Total Tested: {total}")
    print(f"Time Taken: {end_time - start_time:.2f} seconds")
    print(f"Errors: {errors}")
    print("\nConfusion Matrix:")
    print(f"True Positives (Phishing correctly identified): {true_positives}")
    print(f"True Negatives (Legit correctly identified): {true_negatives}")
    print(f"False Positives (Legit incorrectly flagged): {false_positives}")
    print(f"False Negatives (Phishing missed): {false_negatives}")
    
    accuracy = (true_positives + true_negatives) / total if total > 0 else 0
    
    # Precision: TP / (TP + FP)
    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
    
    # Recall (Sensitivity/TPR): TP / (TP + FN)
    recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
    
    # False Positive Rate (FPR): FP / (FP + TN)
    fpr = false_positives / (false_positives + true_negatives) if (false_positives + true_negatives) > 0 else 0
    
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    print(f"\nMetrics:")
    print(f"Accuracy:  {accuracy:.2%}")
    print(f"Precision: {precision:.2%}")
    print(f"Recall:    {recall:.2%}")
    print(f"F1 Score:  {f1_score:.2%}")
    print(f"False Pos. Rate: {fpr:.2%}")
    
    # Save the results to artifact format string
    report = f"""# Phishing URL Detection Model Evaluation

## Summary of Results
- **Total URLs Tested**: {total}
- **Dataset**: `5.urldata.csv` (10,000 URLs)
- **Time Taken**: {end_time - start_time:.2f} seconds
- **Errors**: {errors}

## Key Metrics
- **Accuracy**:  {accuracy:.2%}
- **Precision**: {precision:.2%}
- **Recall**:    {recall:.2%}
- **F1 Score**:  {f1_score:.2%}
- **False Positive Rate**: {fpr:.2%}

## Confusion Matrix
| | Predicted Legitimate | Predicted Phishing |
|---|---|---|
| **Actual Legitimate** | {true_negatives} (TN) | {false_positives} (FP) |
| **Actual Phishing** | {false_negatives} (FN) | {true_positives} (TP) |

## Analysis
The evaluation was run statically against the underlying machine learning model, skipping the more extensive Deep Analysis tool which evaluates full website content block-by-block. Considering that this is pure static extraction on domains without paths/queries, these metrics characterize the baseline model's reliability!
"""
    with open("tests/accuracy_report.md", "w", encoding="utf-8") as f:
        f.write(report)
    print("\nReport saved to tests/accuracy_report.md")

if __name__ == "__main__":
    run_test()
