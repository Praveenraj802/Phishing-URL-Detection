"""
Feature Extractor for URL Analysis
Extracts 35 features from URLs for phishing detection
"""

import re
import math
import tldextract
import validators
from urllib.parse import urlparse, parse_qs
from typing import Dict, Any, List
from loguru import logger
from collections import Counter
import dns.resolver


class URLFeatureExtractor:
    """Extract features from URLs for phishing detection"""
    
    # WHITELISTED DOMAINS - Known legitimate sites that should NEVER be flagged as phishing
    # These are exact domain matches (without TLD) that are safe
    WHITELISTED_DOMAINS = {
        # Top tech companies
        'google', 'youtube', 'gmail', 'googleplex', 'googleusercontent',
        'facebook', 'fbcdn', 'instagram', 'whatsapp',
        'microsoft', 'outlook', 'office365', 'live', 'msn', 'bing',
        'apple', 'icloud', 'itunes', 'appstore',
        'amazon', 'amazonws', 'aws', 'cloudfront',
        
        # Financial institutions - Major banks
        'chase', 'wellsfargo', 'bankofamerica', 'citi', 'citibank',
        'usbank', 'pnc', 'capitalone', 'tdbank', 'schwab', 'fidelity',
        
        # Payment services
        'paypal', 'stripe', 'square', 'venmo', 'cashapp',
        
        # Social media
        'twitter', 'linkedin', 'reddit', 'pinterest', 'snapchat', 'tiktok',
        
        # Streaming services
        'netflix', 'hulu', 'disneyplus', 'primevideo', 'spotify', 'pandora',
        
        # E-commerce
        
        # Banking (Common targets)
        'chase', 'bankofamerica', 'wellsfargo', 'citibank', 'paypal',
        'venmo', 'cashapp', 'stripe',
        
        # Other Common Brands
        'wikipedia', 'craigslist', 'zillow', 'indeed', 'etsy'
    }
    
    # Common suspicious keywords
    SUSPICIOUS_KEYWORDS = [
        'verify', 'account', 'update', 'confirm', 'login', 'signin',
        'secure', 'banking', 'suspended', 'locked', 'urgent', 'alert',
        'security', 'validate', 'authenticate', 'credential', 'password',
        'billing', 'payment', 'winner', 'prize', 'claim', 'free',
        'suspended', 'verify', 'reactivate', 'confirm'
    ]
    
    # Common URL shorteners
    URL_SHORTENERS = [
        'bit.ly', 'goo.gl', 'tinyurl.com', 'ow.ly', 't.co',
        'is.gd', 'buff.ly', 'adf.ly', 'bit.do', 'short.link'
    ]
    
    def __init__(self):
        """Initialize the feature extractor"""
        pass
    
    @staticmethod
    def _levenshtein_distance(s1: str, s2: str) -> int:
        """
        Calculate Levenshtein distance between two strings
        Used to detect typosquatting
        """
        if len(s1) < len(s2):
            return URLFeatureExtractor._levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    @staticmethod
    def _is_typosquatting(domain: str) -> bool:
        """
        STRICT typosquatting detection with whitelist protection
        Now checks against whitelist FIRST to prevent false positives
        """
        domain = domain.lower().strip()
        
        # If domain is empty or too short, skip
        if len(domain) < 3:
            return False
        
        # CRITICAL FIX: Check whitelist FIRST!
        # If domain is whitelisted, it's legitimate - NEVER flag as typosquatting
        if domain in URLFeatureExtractor.WHITELISTED_DOMAINS:
            return False
        
        # Also check if main domain (before first hyphen) is whitelisted
        main_part = domain.split('-')[0] if '-' in domain else domain
        if main_part in URLFeatureExtractor.WHITELISTED_DOMAINS:
            return False
        
        # Brand names to check for typosquatting
        BRAND_NAMES = {
            'google', 'facebook', 'amazon', 'paypal', 'netflix', 'microsoft',
            'apple', 'twitter', 'instagram', 'linkedin', 'yahoo', 'ebay',
            'spotify', 'dropbox', 'github', 'reddit', 'youtube',
            'gmail', 'outlook', 'chase', 'wellsfargo', 'bankofamerica', 'citibank'
        }
        
        # Split domain by hyphens to check each part
        # Example: "amaz0n-support" -> ["amaz0n", "support"]
        domain_parts = domain.split('-')
        
        # Check both the full domain AND individual parts
        domains_to_check = [domain] + domain_parts
        
        for domain_to_test in domains_to_check:
            if len(domain_to_test) < 3:  # Skip very short parts
                continue
            
            # Skip if this part is whitelisted
            if domain_to_test in URLFeatureExtractor.WHITELISTED_DOMAINS:
                continue
                
            for brand in BRAND_NAMES:
                # CRITICAL: Skip exact matches!
                if domain_to_test == brand:
                    continue  # Exact match is legit, not typosquatting
                
                # Method 1: Levenshtein distance (stricter threshold)
                distance = URLFeatureExtractor._levenshtein_distance(domain_to_test, brand)
                
                # Allow max 3 character difference
                # Catches: facebook->faceeebook (3), paypal->paypai (1)
                if distance <= 3 and distance > 0:
                    # Length check - domains should be similar length
                    length_diff = abs(len(domain_to_test) - len(brand))
                    
                    # Allow up to 3 characters difference in length
                    if length_diff <= 3:
                        return True  # Found typosquatting!
                
                # Method 2: Check for character repetition attacks
                # Examples: facebook -> faceeebook (extra 'e's)
                if URLFeatureExtractor._has_character_repetition(domain_to_test, brand):
                    return True
                
                # Method 3: Check if domain contains the brand name with extra chars
                # BUT: Don't trigger if it's just a subdomain like "secure.paypal"
                # Only flag if brand appears with suspicious suffix/prefix
                if brand in domain_to_test and domain_to_test != brand:
                    # Check for suspicious patterns
                    # Flag: "paypal-verify", "secure-paypal", "paypal123"
                    # Don't flag: "paypal" (exact), or whitelisted variations
                    if len(domain_to_test) - len(brand) <= 10:
                        # Additional check: is extra content suspicious keywords?
                        extra_parts = domain_to_test.replace(brand, '')
                        suspicious_suffixes = ['verify', 'secure', 'login', 'account', 'support', 'help', 'billing']
                        if any(suffix in extra_parts for suffix in suspicious_suffixes):
                            return True
                
                # Method 4: Check for common character substitutions
                # 0->o, 1->l, etc.
                if URLFeatureExtractor._has_character_substitution(domain_to_test, brand):
                    return True
        
        return False  # No typosquatting detected
    
    @staticmethod
    def _has_character_repetition(domain: str, legit: str) -> bool:
        """
        Check if domain has repeated characters compared to legitimate domain
        Example: facebook vs faceeebook (extra 'e's)
        """
        # Remove consecutive duplicate characters from both
        def remove_duplicates(s):
            if not s:
                return s
            result = [s[0]]
            for char in s[1:]:
                if char != result[-1]:
                    result.append(char)
            return ''.join(result)
        
        domain_normalized = remove_duplicates(domain)
        legit_normalized = remove_duplicates(legit)
        
        # If they match after removing duplicates, it's character repetition attack
        if domain_normalized == legit_normalized and domain != legit:
            return True
        
        # Also check if normalized version is very similar (distance 1-2)
        distance = URLFeatureExtractor._levenshtein_distance(domain_normalized, legit_normalized)
        if distance <= 2 and distance > 0:
            return True
        
        return False
    
    @staticmethod
    def _has_character_substitution(domain: str, legit: str) -> bool:
        """
        Check for common character substitutions
        0->o, 1->l, i->l, etc.
        """
        substitutions = {
            '0': 'o',
            'o': '0',
            '1': 'l',
            'l': '1',
            'i': 'l',
            '5': 's',
            's': '5',
            '8': 'b',
            'b': '8'
        }
        
        # Try substituting characters
        for i, char in enumerate(domain):
            if char in substitutions:
                # Create a version with substitution
                test_domain = domain[:i] + substitutions[char] + domain[i+1:]
                if test_domain == legit:
                    return True
        
        return False

    def _is_valid_ip(self, ip_string: str) -> bool:
        """Check if the string is a valid IPv4 or IPv6 address."""
        try:
            # Check for IPv4
            if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", ip_string):
                parts = list(map(int, ip_string.split('.')))
                if all(0 <= part <= 255 for part in parts):
                    return True
            # Check for IPv6 (simplified check)
            if ':' in ip_string and validators.ipv6(ip_string):
                return True
        except Exception:
            pass
        return False

    def _check_dns(self, hostname: str, domain: str) -> tuple:
        """Check for A and MX records with a tight timeout to avoid hanging"""
        has_a = 0
        has_mx = 0
        
        if not hostname:
            return 0, 0
            
        # Don't resolve IPs
        if self._is_valid_ip(hostname):
            return 1, 0 # If it's an IP, it effectively has an A record (itself)
            
        try:
            resolver = dns.resolver.Resolver()
            resolver.timeout = 1.0
            resolver.lifetime = 1.0
            
            try:
                resolver.resolve(hostname, 'A')
                has_a = 1
            except Exception:
                try:
                    # Fallback to root domain if hostname fails
                    resolver.resolve(domain, 'A')
                    has_a = 1
                except Exception:
                    pass
                
            try:
                resolver.resolve(domain, 'MX')
                has_mx = 1
            except Exception:
                pass
        except Exception:
            pass
            
        return has_a, has_mx
    
    def extract_all_features(self, url: str) -> Dict[str, Any]:
        """
        Extract all features from a URL
        
        Args:
            url: The URL string to analyze
            
        Returns:
            Dictionary containing all extracted features
        """
        # Validate URL format (permissive - let analysis determine quality)
        # Just log if format seems odd, but continue with analysis
        if not self._is_valid_url(url):
            logger.warning(f"URL format may be unusual: {url}")
            # Continue anyway - analysis will catch issues
        
        features = {}
        
        # Save original url
        features['url'] = url
        
        # Parse URL
        parsed = urlparse(url)
        extracted = tldextract.extract(url)
        
        # 1. URL Structure Features
        features['url_length'] = len(url)
        features['domain_length'] = len(extracted.domain)
        features['path_length'] = len(parsed.path)
        features['query_length'] = len(parsed.query) if parsed.query else 0
        
        # 2. Character Count Features
        features['num_dots'] = url.count('.')
        features['num_hyphens'] = url.count('-')
        features['num_underscores'] = url.count('_')
        features['num_slashes'] = url.count('/')
        features['num_at_symbols'] = url.count('@')
        features['num_question_marks'] = url.count('?')
        features['num_ampersands'] = url.count('&')
        features['num_equal_signs'] = url.count('=')
        features['num_percent_signs'] = url.count('%')
        
        # 3. Subdomain Features
        subdomain = extracted.subdomain
        features['has_subdomain'] = 1 if subdomain else 0
        features['num_subdomains'] = len(subdomain.split('.')) if subdomain else 0
        
        # 4. Security Features
        features['is_https'] = 1 if parsed.scheme == 'https' else 0
        features['has_port'] = 1 if parsed.port else 0
        features['port_number'] = parsed.port if parsed.port else 0
        features['has_ip_address'] = 1 if self._has_ip_in_url(url) else 0
        
        # 5. Suspicious Keyword Features
        url_lower = url.lower()
        features['num_suspicious_keywords'] = sum(
            1 for keyword in self.SUSPICIOUS_KEYWORDS if keyword in url_lower
        )
        features['has_suspicious_keyword'] = 1 if features['num_suspicious_keywords'] > 0 else 0
        
        # 6. URL Shortener Detection
        domain_full = f"{extracted.domain}.{extracted.suffix}"
        features['is_url_shortener'] = 1 if domain_full in self.URL_SHORTENERS else 0
        
        # 7. Lexical Features
        features['digit_ratio'] = self._calculate_digit_ratio(url)
        features['special_char_ratio'] = self._calculate_special_char_ratio(url)
        features['letter_ratio'] = self._calculate_letter_ratio(url)
        
        # 8. Entropy (Randomness Measure)
        features['url_entropy'] = self._calculate_entropy(url)
        
        # 9. Path Features
        features['num_path_segments'] = len([p for p in parsed.path.split('/') if p])
        features['has_query_string'] = 1 if parsed.query else 0
        features['num_query_params'] = len(parse_qs(parsed.query)) if parsed.query else 0
        
        # 10. Domain Features
        features['domain_has_digits'] = 1 if any(c.isdigit() for c in extracted.domain) else 0
        features['domain_has_hyphens'] = 1 if '-' in extracted.domain else 0
        
        # 10.5 Typosquatting Detection (NEW)
        features['is_typosquatting'] = 1 if self._is_typosquatting(extracted.domain) else 0
        
        # 10.8 Live DNS Checks (for rule-based engine only)
        hostname = parsed.hostname or domain_full
        has_a, has_mx = self._check_dns(hostname, domain_full)
        features['has_a_record'] = has_a
        features['has_mx_record'] = has_mx
        
        # 11. Additional Heuristics
        features['excessive_dots'] = 1 if features['num_dots'] > 5 else 0
        features['excessive_hyphens'] = 1 if features['num_hyphens'] > 3 else 0
        features['long_url'] = 1 if features['url_length'] > 75 else 0
        
        # 12. Advanced Lexical Features (High Accuracy Optimizations)
        features['max_consecutive_digits'] = self._get_max_consecutive_digits(url)
        features['longest_path_segment_length'] = self._get_longest_path_segment(parsed.path)
        features['vowel_consonant_ratio'] = self._get_vowel_consonant_ratio(extracted.domain)
        suspicious_tlds = {'xyz', 'top', 'online', 'site', 'vip', 'club', 'cc', 'pw', 'su', 'tk', 'info', 'biz'}
        features['has_suspicious_tld'] = 1 if extracted.suffix.lower() in suspicious_tlds else 0
        features['longest_subdomain_length'] = max([len(part) for part in subdomain.split('.')]) if subdomain else 0
        
        return features
    
    def _is_valid_url(self, url: str) -> bool:
        """
        Permissive URL validation - allows all URLs through for analysis
        Analysis features will determine if URL is phishing
        """
        # Just check it's not empty and has minimum length
        return bool(url and len(url) >= 7)
    
    def _has_ip_in_url(self, url: str) -> bool:
        """Check if URL contains an IP address"""
        # IPv4 pattern
        ipv4_pattern = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
        return bool(re.search(ipv4_pattern, url))
    
    def _calculate_digit_ratio(self, url: str) -> float:
        """Calculate ratio of digits in URL"""
        if not url:
            return 0.0
        digit_count = sum(1 for c in url if c.isdigit())
        return digit_count / len(url)
    
    def _calculate_letter_ratio(self, url: str) -> float:
        """Calculate ratio of letters in URL"""
        if not url:
            return 0.0
        letter_count = sum(1 for c in url if c.isalpha())
        return letter_count / len(url)
    
    def _calculate_special_char_ratio(self, url: str) -> float:
        """Calculate ratio of special characters in URL"""
        if not url:
            return 0.0
        special_count = sum(1 for c in url if not c.isalnum())
        return special_count / len(url)
    
    def _calculate_entropy(self, text: str) -> float:
        """Calculate Shannon entropy of text (measure of randomness)"""
        if not text:
            return 0.0
        
        import math
        from collections import Counter
        
        # Count character frequencies
        counter = Counter(text)
        length = len(text)
        
        # Calculate entropy
        entropy = 0.0
        for count in counter.values():
            probability = count / length
            entropy -= probability * math.log2(probability)
        
        return entropy
    
    def _get_max_consecutive_digits(self, text: str) -> int:
        """Find max consecutive digits in text"""
        if not text: return 0
        import re
        matches = re.findall(r'\d+', text)
        return max(len(m) for m in matches) if matches else 0
        
    def _get_longest_path_segment(self, path: str) -> int:
        """Find longest segment between slashes in a URL path"""
        if not path: return 0
        segments = [p for p in path.split('/') if p]
        return max((len(seg) for seg in segments), default=0)
        
    def _get_vowel_consonant_ratio(self, text: str) -> float:
        """Calculate vowel to consonant ratio"""
        if not text: return 0.0
        text = text.lower()
        vowels = sum(1 for c in text if c in 'aeiou')
        consonants = sum(1 for c in text if c.isalpha() and c not in 'aeiou')
        if consonants == 0: return float(vowels)  # Prevent division by zero
        return vowels / consonants
    
    def get_feature_names(self) -> list:
        """Get list of all feature names"""
        return [
            'url_length', 'domain_length', 'path_length', 'query_length',
            'num_dots', 'num_hyphens', 'num_underscores', 'num_slashes',
            'num_at_symbols', 'num_question_marks', 'num_ampersands',
            'num_equal_signs', 'num_percent_signs',
            'has_subdomain', 'num_subdomains',
            'is_https', 'has_port', 'port_number', 'has_ip_address',
            'num_suspicious_keywords', 'has_suspicious_keyword',
            'is_url_shortener',
            'digit_ratio', 'special_char_ratio', 'letter_ratio',
            'url_entropy',
            'num_path_segments', 'has_query_string', 'num_query_params',
            'domain_has_digits', 'domain_has_hyphens',
            'is_typosquatting',
            'excessive_dots', 'excessive_hyphens', 'long_url',
            'max_consecutive_digits', 'longest_path_segment_length', 'vowel_consonant_ratio',
            'has_suspicious_tld', 'longest_subdomain_length'
        ]
    
    def extract_feature_vector(self, url: str) -> list:
        """
        Extract features as a numerical vector
        
        Args:
            url: The URL to analyze
            
        Returns:
            List of feature values in consistent order
        """
        features_dict = self.extract_all_features(url)
        feature_names = self.get_feature_names()
        return [features_dict[name] for name in feature_names]


# Convenience function
def extract_features(url: str) -> Dict[str, Any]:
    """
    Extract features from a URL
    
    Args:
        url: The URL to analyze
        
    Returns:
        Dictionary of features
    """
    extractor = URLFeatureExtractor()
    return extractor.extract_all_features(url)


if __name__ == "__main__":
    # Test the feature extractor
    test_urls = [
        "https://www.google.com",
        "http://secure-login-verify.suspicious-domain.com/account/verify?token=abc123",
        "http://192.168.1.1/login",
        "https://bit.ly/abc123"
    ]
    
    extractor = URLFeatureExtractor()
    
    for url in test_urls:
        print(f"\n{'='*60}")
        print(f"URL: {url}")
        print(f"{'='*60}")
        
        try:
            features = extractor.extract_all_features(url)
            for key, value in features.items():
                print(f"{key:30s}: {value}")
        except Exception as e:
            print(f"Error: {e}")
