"""
Comprehensive Test - Whitelist Fix Validation
Tests both legitimate and phishing URLs
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.models.predictor import get_predictor

def test_whitelist_fix():
    """Test that whitelist prevents false positives"""
    
    predictor = get_predictor()
    
    # Legitimate URLs that should NOT be flagged
    legitimate_urls = [
        ('https://www.paypal.com', 'Official PayPal'),
        ('https://www.netflix.com', 'Official Netflix'),
        ('https://www.google.com', 'Official Google'),
        ('https://www.amazon.com', 'Official Amazon'),
        ('https://www.bankofamerica.com', 'Official Bank of America'),
        ('https://secure.chase.com', 'Chase secure subdomain'),
        ('https://www.microsoft.com', 'Official Microsoft'),
        ('https://www.facebook.com', 'Official Facebook'),
    ]
    
    # Phishing URLs that SHOULD be flagged
    phishing_urls = [
        ('http://paypal-security.com', 'Brand + suspicious keyword'),
        ('http://g00gle.com', 'Character substitution'),
        ('http://amaz0n-support.in', 'Character substitution + compound'),
        ('http://faceeebook.com', 'Character repetition'),
        ('http://netflix-billing.info', 'Brand + suspicious keyword'),
        ('http://paypal-verify.com', 'Brand + verify keyword'),
    ]
    
    print("=" * 80)
    print("WHITELIST FIX VALIDATION TEST")
    print("=" * 80)
    print()
    
    # Test legitimate URLs
    print("Testing LEGITIMATE URLs (Should be SAFE):")
    print("-" * 80)
    legit_correct = 0
    legit_wrong = 0
    
    for url, description in legitimate_urls:
        prediction, confidence, _ = predictor.predict(url)
        
        if prediction.lower() != "phishing":
            status = "[PASS]"
            legit_correct += 1
        else:
            status = "[FAIL]"
            legit_wrong += 1
        
        print(f"{status} {url:<45} -> {prediction.upper():<10} ({confidence:.0%}) - {description}")
    
    print()
    print(f"Legitimate URLs: {legit_correct}/{len(legitimate_urls)} correct ({legit_correct/len(legitimate_urls)*100:.0f}% accuracy)")
    print()
    
    # Test phishing URLs
    print("=" * 80)
    print("Testing PHISHING URLs (Should be PHISHING):")
    print("-" * 80)
    phish_correct = 0
    phish_wrong = 0
    
    for url, description in phishing_urls:
        prediction, confidence, _ = predictor.predict(url)
        
        if prediction.lower() == "phishing":
            status = "[PASS]"
            phish_correct += 1
        else:
            status = "[FAIL]"
            phish_wrong += 1
        
        print(f"{status} {url:<45} -> {prediction.upper():<10} ({confidence:.0%}) - {description}")
    
    print()
    print(f"Phishing URLs: {phish_correct}/{len(phishing_urls)} correct ({phish_correct/len(phishing_urls)*100:.0f}% accuracy)")
    print()
    
    # Overall results
    print("=" * 80)
    print("OVERALL RESULTS")
    print("=" * 80)
    total_correct = legit_correct + phish_correct
    total_tested = len(legitimate_urls) + len(phishing_urls)
    
    print(f"Total Tested: {total_tested}")
    print(f"Total Correct: {total_correct}")
    print(f"Overall Accuracy: {total_correct/total_tested*100:.1f}%")
    print()
    print(f"False Positives: {legit_wrong} (legitimate URLs wrongly flagged)")
    print(f"False Negatives: {phish_wrong} (phishing URLs missed)")
    print()
    
    if legit_wrong == 0 and phish_wrong == 0:
        print("[SUCCESS] All tests passed!")
        return 0
    else:
        print("[ISSUES FOUND] Some tests failed")
        return 1

if __name__ == "__main__":
    exit_code = test_whitelist_fix()
    sys.exit(exit_code)
