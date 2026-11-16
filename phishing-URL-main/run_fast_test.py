import os
import sys
import time
import pandas as pd
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add the backend directory to sys.path to ensure 'app' can be imported
backend_dir = Path(__file__).resolve().parent / 'backend'
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.models.predictor import get_predictor
from loguru import logger

# Suppress debug logs from app to speed up the test
logger.remove()

def process_url(predictor, domain, true_label):
    test_url = domain if domain.startswith("http") else "http://" + domain
    try:
        pred_str, conf, _ = predictor.predict(test_url)
        pred_label = 1 if pred_str == 'phishing' else 0
        return pred_label, true_label, None
    except Exception as e:
        return None, true_label, str(e)

def run_test():
    print("Loading dataset...")
    # Use the same dataset URL as before, but it only has 10,000 URLs anyway
    url = "https://raw.githubusercontent.com/shreyagopal/Phishing-Website-Detection-by-Machine-Learning-Techniques/master/DataFiles/5.urldata.csv"
    df = pd.read_csv(url)
    
    # Take 2000 URLs to test quickly (1000 of each class)
    phishing_df = df[df['Label'] == 1].head(1000)
    legit_df = df[df['Label'] == 0].head(1000)
    test_df = pd.concat([phishing_df, legit_df]).sample(frac=1, random_state=42).reset_index(drop=True)
    
    domains = test_df['Domain'].tolist()
    labels = test_df['Label'].tolist()
    
    print(f"Loaded {len(domains)} URLs for rapid testing (50% split).")
    print("Initializing predictor with our newly trained model...")
    
    predictor = get_predictor()
    if not predictor.is_ready():
        print("Model failed to load, used fallback.")
    else:
        print("New Model Loaded Successfully!")
    
    true_positives = 0
    false_positives = 0
    true_negatives = 0
    false_negatives = 0
    errors = 0
    
    total = len(domains)
    print(f"Starting test on {total} URLs with 40 parallel threads...")
    start_time = time.time()
    
    completed = 0
    with ThreadPoolExecutor(max_workers=40) as executor:
        future_to_url = {executor.submit(process_url, predictor, d, l): (d, l) for d, l in zip(domains, labels)}
        for future in as_completed(future_to_url):
            try:
                pred_label, true_label, error = future.result()
                if error:
                    errors += 1
                else:
                    if pred_label == 1 and true_label == 1:
                        true_positives += 1
                    elif pred_label == 1 and true_label == 0:
                        false_positives += 1
                    elif pred_label == 0 and true_label == 0:
                        true_negatives += 1
                    elif pred_label == 0 and true_label == 1:
                        false_negatives += 1
            except Exception:
                errors += 1
                
            completed += 1
            if completed > 0 and completed % 200 == 0:
                print(f"Processed {completed}/{total}...")
                
    end_time = time.time()
    
    print("\\n" + "="*50)
    print("--- AUTOMATED TESTING RESULTS ---")
    print("="*50)
    print(f"Total Tested: {total}")
    print(f"Time Taken: {end_time - start_time:.2f} seconds")
    print(f"Errors during extraction: {errors}")
    print("\\nConfusion Matrix:")
    print(f"True Positives (Phishing correctly identified): {true_positives}")
    print(f"True Negatives (Legit correctly identified):   {true_negatives}")
    print(f"False Positives (Legit incorrectly flagged):   {false_positives}")
    print(f"False Negatives (Phishing missed):             {false_negatives}")
    
    accuracy = (true_positives + true_negatives) / total if total > 0 else 0
    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
    recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
    fpr = false_positives / (false_positives + true_negatives) if (false_positives + true_negatives) > 0 else 0
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    print(f"\\nKEY METRICS:")
    print(f"Overall Accuracy:       {accuracy:.2%}")
    print(f"Precision (Phishing):   {precision:.2%}")
    print(f"Call Rate (Recall):     {recall:.2%}")
    print(f"F1 Risk Score:          {f1_score:.2%}")
    print(f"False Positive Rate:    {fpr:.2%}")
    print("==================================================")
    
    report = f"""# Final ML Model Evaluation

## Summary of Results
- **Total URLs Tested**: {total} (1,000 Legitimate, 1,000 Phishing)
- **Time Taken**: {end_time - start_time:.2f} seconds
- **Overall Accuracy**: {accuracy:.2%}

## Confusion Matrix
| | Predicted Legitimate | Predicted Phishing |
|---|---|---|
| **Actual Legitimate** | {true_negatives} | {false_positives} |
| **Actual Phishing** | {false_negatives} | {true_positives} |

## Deep Metrics
- **Precision**: {precision:.2%} (When it says Phishing, it's correct {precision:.2%} of the time)
- **Recall**: {recall:.2%} (It successfully catches {recall:.2%} of all true Phishing URLs)
- **F1 Score**: {f1_score:.2%}
- **False Positive Rate**: {fpr:.2%} (Only {fpr:.2%} of safe sites are incorrectly flagged)
"""
    os.makedirs("tests", exist_ok=True)
    with open("tests/final_model_report.md", "w", encoding="utf-8") as f:
        f.write(report)
    print("\\nSaved detailed report to tests/final_model_report.md")

if __name__ == "__main__":
    run_test()
