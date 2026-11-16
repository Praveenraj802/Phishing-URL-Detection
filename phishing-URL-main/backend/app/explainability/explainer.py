"""
Explainability Engine
Generates human-readable explanations for phishing URL predictions
"""

from typing import List, Dict, Any


class ExplainabilityEngine:
    """Generate human-readable explanations for URL classification"""
    
    def __init__(self):
        """Initialize the explainability engine"""
        self.explanation_templates = self._load_explanation_templates()
    
    def _load_explanation_templates(self) -> Dict[str, str]:
        """Load explanation templates for different features"""
        return {
            # URL Structure
            'long_url': "Unusually long URL (>75 characters) - often used to hide malicious intent",
            'excessive_dots': "Excessive dots in URL - common in phishing attempts",
            'excessive_hyphens': "Excessive hyphens in URL - suspicious pattern",
            'has_ip_address': "URL contains IP address instead of domain name - highly suspicious",
            'typosquatting': "Domain name is a misspelling of a popular brand (typosquatting attack)",
            
            # Security
            'no_https': "Uses HTTP instead of HTTPS - not secure",
            'has_port': "Contains non-standard port number - potentially suspicious",
            
            # Suspicious Keywords
            'suspicious_keywords': "Contains suspicious keywords like 'login', 'verify', 'account'",
            
            # URL Shortener
            'url_shortener': "Uses URL shortener - makes it difficult to verify destination",
            
            # Subdomain
            'many_subdomains': "Contains multiple subdomains - common phishing tactic",
            
            # Domain
            'domain_has_digits': "Domain name contains digits - often seen in phishing",
            'domain_has_hyphens': "Domain name contains hyphens - suspicious pattern",
            
            # Character Patterns
            'high_special_char_ratio': "High ratio of special characters - unusual pattern",
            'high_digit_ratio': "High ratio of digits in URL - suspicious",
            
            # Entropy
            'high_entropy': "URL appears random or obfuscated - possible phishing",
            
            # Path/Query
            'long_path': "Unusually long path - may be hiding parameters",
            'many_query_params': "Many query parameters - potentially suspicious",
        }
    
    def generate_explanations(
        self,
        features: Dict[str, Any],
        prediction: str,
        confidence: float
    ) -> List[str]:
        """
        Generate human-readable explanations based on features
        
        Args:
            features: Dictionary of extracted features
            prediction: Model prediction ('phishing' or 'legitimate')
            confidence: Prediction confidence score
            
        Returns:
            List of explanation strings
        """
        explanations = []
        
        # Only generate explanations for phishing predictions
        if prediction == 'legitimate':
            if features.get('is_https', 0) == 1:
                explanations.append("✓ Uses HTTPS (secure connection)")
            if features.get('num_suspicious_keywords', 0) == 0:
                explanations.append("✓ No suspicious keywords detected")
            if features.get('url_length', 0) < 50:
                explanations.append("✓ Normal URL length")
            return explanations or ["URL appears legitimate based on multiple checks"]
        
        # Phishing explanations - check features and add relevant explanations
        
        # Check critical indicators first
        # 0. Invalid URL format (MOST CRITICAL)
        if features.get('invalid_format'):
            error_msg = features.get('error_reason', 'malformed URL structure')
            explanations.append(f"✗ Invalid or malformed URL format - {error_msg}")
        
        # 1. Typosquatting
        if features.get('is_typosquatting', 0) == 1:
            explanations.append(self.explanation_templates['typosquatting'])
        
        # 2. IP Address (moved up as critical)
        if features.get('has_ip_address', 0) == 1:
            explanations.append(self.explanation_templates['has_ip_address'])
        
        # 1. URL Length
        if features.get('long_url', 0) == 1:
            explanations.append(self.explanation_templates['long_url'])
        
        # 3. HTTPS
        if features.get('is_https', 0) == 0:
            explanations.append(self.explanation_templates['no_https'])
        
        # 4. Suspicious Keywords
        num_keywords = features.get('num_suspicious_keywords', 0)
        if num_keywords > 0:
            keyword_explanation = f"Contains {num_keywords} suspicious keyword(s) like 'login', 'verify', or 'account'"
            explanations.append(keyword_explanation)
        
        # 5. URL Shortener
        if features.get('is_url_shortener', 0) == 1:
            explanations.append(self.explanation_templates['url_shortener'])
        
        # 6. Excessive Patterns
        if features.get('excessive_dots', 0) == 1:
            explanations.append(self.explanation_templates['excessive_dots'])
        
        if features.get('excessive_hyphens', 0) == 1:
            explanations.append(self.explanation_templates['excessive_hyphens'])
        
        # 7. Subdomains
        num_subdomains = features.get('num_subdomains', 0)
        if num_subdomains > 2:
            explanations.append(f"Contains {num_subdomains} subdomains - potentially hiding true destination")
        
        # 8. Domain Characteristics
        if features.get('domain_has_digits', 0) == 1:
            explanations.append(self.explanation_templates['domain_has_digits'])
        
        if features.get('domain_has_hyphens', 0) == 1:
            explanations.append(self.explanation_templates['domain_has_hyphens'])
        
        # 9. Port Number
        if features.get('has_port', 0) == 1:
            port = features.get('port_number', 0)
            explanations.append(f"Uses non-standard port {port} - suspicious")
        
        # 10. Character Ratios
        special_char_ratio = features.get('special_char_ratio', 0)
        if special_char_ratio > 0.3:
            explanations.append(self.explanation_templates['high_special_char_ratio'])
        
        digit_ratio = features.get('digit_ratio', 0)
        if digit_ratio > 0.2:
            explanations.append(self.explanation_templates['high_digit_ratio'])
        
        # 11. Entropy
        entropy = features.get('url_entropy', 0)
        if entropy > 4.5:
            explanations.append(self.explanation_templates['high_entropy'])
        
        # 12. Query Parameters
        num_query_params = features.get('num_query_params', 0)
        if num_query_params > 5:
            explanations.append(f"Contains {num_query_params} query parameters - may be trying to obfuscate URL")
        
        # If no specific explanations but high confidence phishing
        if not explanations and confidence > 0.7:
            explanations.append("URL structure matches known phishing patterns")
        
        # Limit to top 5 most important explanations
        return explanations[:5] if explanations else ["Suspicious patterns detected in URL structure"]
    
    def get_risk_level(self, confidence: float) -> str:
        """
        Determine risk level based on confidence score
        
        Args:
            confidence: Prediction confidence (0-1)
            
        Returns:
            Risk level string
        """
        if confidence >= 0.8:
            return "high"
        elif confidence >= 0.5:
            return "medium"
        else:
            return "low"
    
    def format_explanation_response(
        self,
        url: str,
        prediction: str,
        confidence: float,
        features: Dict[str, Any],
        scan_time_ms: float
    ) -> Dict[str, Any]:
        """
        Format complete explanation response
        
        Args:
            url: The analyzed URL
            prediction: Model prediction
            confidence: Confidence score
            features: Extracted features
            scan_time_ms: Time taken for scan
            
        Returns:
            Formatted response dictionary
        """
        explanations = self.generate_explanations(features, prediction, confidence)
        risk_level = self.get_risk_level(confidence)
        
        return {
            "url": url,
            "prediction": prediction,
            "confidence": round(confidence, 4),
            "risk_level": risk_level,
            "reasons": explanations,
            "scan_time_ms": round(scan_time_ms, 2),
            "features_extracted": len(features)
        }


# Convenience function
def explain_prediction(
    url: str,
    prediction: str,
    confidence: float,
    features: Dict[str, Any],
    scan_time_ms: float = 0
) -> Dict[str, Any]:
    """
    Generate explanation for a prediction
    
    Args:
        url: The analyzed URL
        prediction: Model prediction
        confidence: Confidence score
        features: Extracted features
        scan_time_ms: Time taken for scan
        
    Returns:
        Explanation response
    """
    engine = ExplainabilityEngine()
    return engine.format_explanation_response(
        url, prediction, confidence, features, scan_time_ms
    )
