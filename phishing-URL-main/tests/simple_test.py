"""
Simple QA Test - Testing each phishing URL individually
No logging to avoid encoding issues
"""

import sys
import os

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__), '..', 'backend')
sys.path.insert(0, backend_path)

from app.models.predictor import get_predictor

# Test URLs - known phishing patterns
TEST_URLS = [
    # Typosquatting
    ("https://faceeebook.com", "Typosquatting (facebook)"),
    ("https://gooogle.com", "Typosquatting (google)"),
    ("http://amaz0n.com", "Character substitution"),
    ("http://g00gle.com", "Character substitution"),
    ("https://facebok.com", "Misspelling"),
    
    # Brand abuse
    ("http://amazon-verify.com", "Brand + suspicious keyword"),
    ("http://paypal-secure.com", "Brand + suspicious keyword"),
    ("http://amaz0n-support.in", "Compound fake"),
    
    # Other patterns
    ("http://192.168.1.100/login", "IP address"),
    ("http://bit.ly/2xYz3aB", "URL shortener"),
]

def run_tests():
    print("=" * 70)
    print("SIMPLE PHISHING URL DETECTION TEST")
    print("=" * 70)
    
    predictor = get_predictor()
    
    passed = 0
    failed = 0
    failed_urls = []
    
    for url, description in TEST_URLS:
        try:
            prediction, confidence, _ = predictor.predict(url)
            
            if prediction == "phishing":
                status = "PASS"
                passed += 1
            else:
                status = "FAIL"
                failed += 1
                failed_urls.append((url, prediction, confidence, description))
            
            print(f"[{status}] {url}")
            print(f"      {description} -> {prediction} ({confidence:.0%})")
            
        except Exception as e:
            print(f"[ERROR] {url}")
            print(f"      Error: {e}")
            failed += 1
            failed_urls.append((url, "ERROR", 0, str(e)))
    
    # Summary
    total = len(TEST_URLS)
    print("\n" + "=" * 70)
    print(f"RESULTS: {passed}/{total} passed ({passed/total*100:.1%})")
    print("=" * 70)
    
    # Failed URLs
    if failed_urls:
        print("\nFAILED URLS (Incorrectly marked as safe):")
        print("-" * 70)
        for url, pred, conf, desc in failed_urls:
            print(f"  {url}")
            print(f"    Description: {desc}")
            print(f"    Got: {pred} (Expected: phishing)")
            if pred != "ERROR":
                print(f"    Confidence: {conf:.0%}")
            print()
    
    return failed_urls

if __name__ == "__main__":
    failed = run_tests()
    sys.exit(1 if failed else 0)
