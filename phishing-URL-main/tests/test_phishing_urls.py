"""
QA Test Suite: Testing Phishing URL Detection
Comprehensive testing with known phishing patterns
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.models.predictor import get_predictor

# Comprehensive test suite of known phishing URLs
PHISHING_TEST_URLS = {
    "Typosquatting - Character Repetition": [
        "https://faceeebook.com",
        "https://gooogle.com",
        "https://twittter.com",
        "https://amazoon.com",
        "https://payypal.com",
    ],
    
    "Typosquatting - Character Substitution": [
        "http://amaz0n.com",
        "http://g00gle.com",
        "http://micr0soft.com",
        "http://paypa1.com",
        "http://netf1ix.com",
    ],
    
    "Typosquatting - Simple Misspelling": [
        "https://facebok.com",
        "https://googel.com",
        "https://amazom.com",
        "https://instgram.com",
        "https://aplle.com",
    ],
    
    "Brand + Suspicious Keywords": [
        "http://amazon-verify.com",
        "http://paypal-secure.com",
        "http://facebook-login.com",
        "http://apple-support.com",
        "http://netflix-billing.com",
        "http://microsoft-security.com",
        "http://google-account-recovery.com",
    ],
    
    "Hyphenated Compound Fake Domains": [
        "http://amaz0n-support.in",
        "http://paypal-verify-account.com",
        "http://secure-facebook-login.com",
        "http://apple-id-unlock.com",
        "http://netflix-payment-update.com",
    ],
    
    "IP Address URLs": [
        "http://192.168.1.100/login",
        "http://123.45.67.89/paypal",
        "http://8.8.8.8/secure",
    ],
    
    "URL Shorteners (Suspicious)": [
        "http://bit.ly/2xYz3aB",
        "http://tinyurl.com/suspicious",
        "http://goo.gl/abcdef",
    ],
    
    "Suspicious TLDs": [
        "http://amazon.tk",
        "http://paypal.ml",
        "http://facebook.ga",
        "http://apple.cf",
    ],
    
    "Multiple Suspicious Indicators": [
        "http://secure-paypal-verify.tk",
        "http://facebook-account-recovery.ml",
        "http://apple-icloud-unlock.ga",
        "http://amazon-prize-winner.cf",
    ],
    
    "Subdomain Abuse": [
        "http://paypal.fake-site.com",
        "http://login.amazon.phishing.net",
        "http://secure.facebook.malicious.org",
    ],
}

def test_phishing_detection():
    """Test each phishing URL and report results"""
    
    predictor = get_predictor()
    
    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    failed_urls = []
    
    print("=" * 80)
    print("PHISHING URL DETECTION TEST SUITE")
    print("=" * 80)
    print()
    
    for category, urls in PHISHING_TEST_URLS.items():
        print(f"\nTesting Category: {category}")
        print("-" * 80)
        
        for url in urls:
            total_tests += 1
            
            try:
                prediction, confidence, features = predictor.predict(url)
                
                # A phishing URL should be detected as "phishing"
                if prediction == "phishing":
                    status = "[PASS]"
                    passed_tests += 1
                else:
                    status = "[FAIL]"
                    failed_tests += 1
                    failed_urls.append({
                        'url': url,
                        'category': category,
                        'prediction': prediction,
                        'confidence': confidence
                    })
                
                print(f"{status} | {url}")
                print(f"     Prediction: {prediction} | Confidence: {confidence:.2%}")
                
            except Exception as e:
                print(f"[ERROR] | {url}")
                print(f"     Error: {str(e)}")
                failed_tests += 1
                failed_urls.append({
                    'url': url,
                    'category': category,
                    'prediction': 'ERROR',
                    'confidence': 0,
                    'error': str(e)
                })
    
    # Summary Report
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Total Tests:  {total_tests}")
    print(f"Passed:       {passed_tests} ({passed_tests/total_tests*100:.1f}%)")
    print(f"Failed:       {failed_tests} ({failed_tests/total_tests*100:.1f}%)")
    print()
    
    # Detailed Failure Report
    if failed_urls:
        print("=" * 80)
        print("FAILED TESTS - URLs INCORRECTLY MARKED AS SAFE")
        print("=" * 80)
        
        for idx, failure in enumerate(failed_urls, 1):
            print(f"\n{idx}. Category: {failure['category']}")
            print(f"   URL: {failure['url']}")
            print(f"   Prediction: {failure['prediction']} (Expected: phishing)")
            print(f"   Confidence: {failure.get('confidence', 0):.2%}")
            if 'error' in failure:
                print(f"   Error: {failure['error']}")
    else:
        print("ALL TESTS PASSED! No false negatives detected.")
    
    print("\n" + "=" * 80)
    
    return failed_urls

if __name__ == "__main__":
    failed = test_phishing_detection()
    
    # Exit with error code if tests failed
    sys.exit(1 if failed else 0)
