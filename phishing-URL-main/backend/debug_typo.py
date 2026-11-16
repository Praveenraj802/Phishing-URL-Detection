from app.features.feature_extractor import URLFeatureExtractor
import tldextract

def debug_typo():
    extractor = URLFeatureExtractor()
    urls = [
        "http://google.com",
        "https://www.google.com",
        "http://ecnavi.jp"
    ]
    
    for url in urls:
        print(f"\nEvaluating: {url}")
        extracted = tldextract.extract(url)
        domain = extracted.domain
        print(f"Extracted domain: {domain}")
        res = extractor._is_typosquatting(domain)
        print(f"is_typo: {res}")
        
if __name__ == "__main__":
    debug_typo()
