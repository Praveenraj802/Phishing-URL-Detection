import sys
import os
import warnings

# Suppress annoying warnings for clean output
warnings.filterwarnings('ignore')

# Add the project directory to the path so we can import app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.models.predictor import get_predictor
from app.core.logging import setup_logging

# Setup minimal logging to avoid clutter
setup_logging()

def main():
    predictor = get_predictor()
    
    # Wait for models to load
    if not hasattr(predictor, 'is_ready') or not predictor.is_ready():
        print("Models are not fully loaded yet. Proceeding with available models.")
        
    test_urls = [
        # 1. Legitimate URLs with Long Paths
        "https://accounts.google.com/signin/v2/identifier",
        "https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
        "https://www.amazon.com/ap/signin",
        "https://secure.paypal.com/signin",
        
        # 2. Legitimate URLs with Subdomains
        "https://mail.google.com",
        "https://support.google.com",
        "https://developer.mozilla.org",
        "https://help.netflix.com",
        "https://business.facebook.com",
        
        # 3. Legitimate URLs with Numbers or Hyphens
        "https://aws.amazon.com",
        "https://store.playstation.com",
        "https://myaccount.google.com",
        "https://api.twitter.com",
        "https://login.live.com",
        
        # 4. Legitimate URLs that Look Like Login/Verification Pages
        "https://github.com/login",
        "https://stackoverflow.com/users/login",
        "https://www.linkedin.com/login",
        "https://accounts.google.com/ServiceLogin",
        
        # 5. Legitimate URLs Using URL Parameters
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://www.google.com/search?q=phishing+detection",
        "https://www.amazon.com/s?k=laptop",
        
        # Phishing Examples for comparison
        "https://paypal-login-verification.com",
        "https://amazon-secure-authentication.net",
        "https://secure-login-paypal.verify-user.com"
    ]
    
    # We expect these to be legitimate
    expected_legitimate = test_urls[:-3]
    expected_phishing = test_urls[-3:]
    
    print("=" * 80)
    print("EDGE CASE BLAST TESTING")
    print("=" * 80)
    
    correct_count = 0
    total_count = len(test_urls)
    
    for i, url in enumerate(test_urls):
        result = predictor.predict(url)
        
        if isinstance(result, tuple) and len(result) >= 2:
            prediction = result[0]
            confidence = result[1]
        else:
            prediction = result.get('prediction', 'unknown')
            confidence = result.get('confidence', 0.0)
            
        expected = "legitimate" if url in expected_legitimate else "phishing"
        is_correct = prediction == expected
        
        if is_correct:
            correct_count += 1
            
        status = "✅ PASS" if is_correct else "❌ FAIL"
        
        print(f"\n[{i+1}/{total_count}] {status}")
        print(f"URL:        {url}")
        print(f"Expected:   {expected}")
        print(f"Prediction: {prediction} (Confidence: {confidence:.4f})")
        
    print("\n" + "=" * 80)
    print(f"FINAL SCORE: {correct_count}/{total_count} ({correct_count/total_count*100:.1f}%)")
    print("=" * 80)
    
    if correct_count < total_count:
        print("\nNote: For failed cases, the model might be penalizing too heavily based on heuristics.")

if __name__ == "__main__":
    main()
