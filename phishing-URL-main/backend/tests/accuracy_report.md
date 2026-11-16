# Phishing URL Detection Model Evaluation

## Summary of Results
- **Total URLs Tested**: 10000
- **Dataset**: `5.urldata.csv` (10,000 URLs)
- **Time Taken**: 58.16 seconds
- **Errors**: 0

## Key Metrics
- **Accuracy**:  89.01%
- **Precision**: 88.01%
- **Recall**:    90.32%
- **F1 Score**:  89.15%
- **False Positive Rate**: 12.30%

## Confusion Matrix
| | Predicted Legitimate | Predicted Phishing |
|---|---|---|
| **Actual Legitimate** | 4385 (TN) | 615 (FP) |
| **Actual Phishing** | 484 (FN) | 4516 (TP) |

## Analysis
The evaluation was run statically against the underlying machine learning model, skipping the more extensive Deep Analysis tool which evaluates full website content block-by-block. Considering that this is pure static extraction on domains without paths/queries, these metrics characterize the baseline model's reliability!
