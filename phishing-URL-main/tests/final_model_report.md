# Final ML Model Evaluation

## Summary of Results
- **Total URLs Tested**: 2000 (1,000 Legitimate, 1,000 Phishing)
- **Time Taken**: 140.61 seconds
- **Overall Accuracy**: 68.70%

## Confusion Matrix
| | Predicted Legitimate | Predicted Phishing |
|---|---|---|
| **Actual Legitimate** | 844 | 156 |
| **Actual Phishing** | 470 | 530 |

## Deep Metrics
- **Precision**: 77.26% (When it says Phishing, it's correct 77.26% of the time)
- **Recall**: 53.00% (It successfully catches 53.00% of all true Phishing URLs)
- **F1 Score**: 62.87%
- **False Positive Rate**: 15.60% (Only 15.60% of safe sites are incorrectly flagged)
