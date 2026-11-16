"""
Form Analyzer - Analyze forms for credential theft patterns
"""

from bs4 import BeautifulSoup
from typing import Dict, Any, List
from urllib.parse import urlparse
from loguru import logger


class FormAnalyzer:
    """Analyze HTML forms for phishing indicators"""
    
    SENSITIVE_FIELD_NAMES = [
        'password', 'pass', 'pwd', 'passwd',
        'credit_card', 'creditcard', 'cc', 'cvv', 'card',
        'ssn', 'social_security',
        'pin', 'security_code'
    ]
    
    def __init__(self):
        """Initialize form analyzer"""
        pass
    
    def analyze(self, html_content: str, original_url: str) -> Dict[str, Any]:
        """
        Analyze forms in HTML
        
        Args:
            html_content: HTML content
            original_url: Original page URL
            
        Returns:
            Analysis results
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            forms = soup.find_all('form')
            
            findings = {
                'total_forms': len(forms),
                'forms_with_passwords': 0,
                'forms_to_external_domains': 0,
                'forms_using_http': 0,
                'suspicious_forms': [],
                'risk_score': 0
            }
            
            original_domain = urlparse(original_url).netloc
            
            for i, form in enumerate(forms):
                form_analysis = self._analyze_single_form(form, original_url, original_domain)
                
                if form_analysis['is_suspicious']:
                    findings['suspicious_forms'].append(form_analysis)
                    findings['risk_score'] += form_analysis['risk_points']
                
                if form_analysis['has_password_field']:
                    findings['forms_with_passwords'] += 1
                
                if form_analysis['submits_to_external_domain']:
                    findings['forms_to_external_domains'] += 1
                
                if form_analysis['uses_http']:
                    findings['forms_using_http'] += 1
            
            # Generate explanations
            findings['detailed_findings'] = self._generate_explanations(findings)
            
            return findings
            
        except Exception as e:
            logger.error(f"Error analyzing forms: {str(e)}")
            return {'error': str(e)}
    
    def _analyze_single_form(self, form, original_url: str, original_domain: str) -> Dict[str, Any]:
        """Analyze a single form"""
        analysis = {
            'action': form.get('action', ''),
            'method': form.get('method', 'GET').upper(),
            'fields': [],
            'has_password_field': False,
            'has_sensitive_fields': False,
            'submits_to_external_domain': False,
            'uses_http': False,
            'is_suspicious': False,
            'risk_points': 0,
            'issues': []
        }
        
        # Analyze fields
        inputs = form.find_all(['input', 'textarea'])
        for inp in inputs:
            field_type = inp.get('type', 'text').lower()
            field_name = inp.get('name', '').lower()
            
            analysis['fields'].append({
                'name': field_name,
                'type': field_type
            })
            
            if field_type == 'password':
                analysis['has_password_field'] = True
            
            if any(sensitive in field_name for sensitive in self.SENSITIVE_FIELD_NAMES):
                analysis['has_sensitive_fields'] = True
        
        # Check form action
        action = analysis['action']
        if action:
            # External domain check
            if action.startswith('http'):
                action_domain = urlparse(action).netloc
                if action_domain != original_domain:
                    analysis['submits_to_external_domain'] = True
                    analysis['is_suspicious'] = True
                    analysis['risk_points'] += 3
                    analysis['issues'].append(f'Form submits to external domain: {action_domain}')
            
            # HTTP check (insecure)
            if action.startswith('http://'):
                analysis['uses_http'] = True
                analysis['is_suspicious'] = True
                analysis['risk_points'] += 2
                analysis['issues'].append('Form uses insecure HTTP instead of HTTPS')
        
        # Critical: Password field submitting externally or over HTTP
        if analysis['has_password_field']:
            if analysis['submits_to_external_domain']:
                analysis['risk_points'] += 4  # CRITICAL
                analysis['issues'].append('CRITICAL: Password field submits to external site')
            
            if analysis['uses_http']:
                analysis['risk_points'] += 3
                analysis['issues'].append('CRITICAL: Password sent over insecure connection')
        
        return analysis
    
    def _generate_explanations(self, findings: Dict) -> List[Dict]:
        """Generate explanations for findings"""
        explanations = []
        
        if findings['forms_with_passwords'] > 0 and findings['forms_to_external_domains'] > 0:
            explanations.append({
                'severity': 'critical',
                'finding': 'Password form submits to external domain',
                'explanation': 'Login credentials are being sent to a different website - clear sign of credential theft'
            })
        
        if findings['forms_using_http'] > 0:
            explanations.append({
                'severity': 'high',
                'finding': 'Forms use insecure HTTP protocol',
                'explanation': 'Data is transmitted without encryption, making it easy for attackers to intercept'
            })
        
        for form in findings['suspicious_forms']:
            if form['issues']:
                for issue in form['issues']:
                    explanations.append({
                        'severity': 'critical' if 'CRITICAL' in issue else 'high',
                        'finding': issue,
                        'form_action': form['action']
                    })
        
        return explanations
