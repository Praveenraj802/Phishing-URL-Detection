"""
HTML Analyzer - Analyze HTML structure for phishing indicators
"""

from bs4 import BeautifulSoup
from typing import Dict, Any, List
import re
from loguru import logger


class HTMLAnalyzer:
    """Analyze HTML content for suspicious patterns"""
    
    def __init__(self):
        """Initialize HTML analyzer"""
        pass
    
    def analyze(self, html_content: str, url: str) -> Dict[str, Any]:
        """
        Analyze HTML for phishing indicators
        
        Args:
            html_content: HTML content string
            url: Original URL
            
        Returns:
            Dictionary with analysis results
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            findings = {
'has_title': False,
                'title_text': '',
                'has_favicon': False,
                'hidden_elements': [],
                'suspicious_meta_tags': [],
                'external_forms': [],
                'hidden_iframes': [],
                'password_fields_count': 0,
                'input_fields_count': 0,
                'suspicious_scripts': [],
                'missing_elements': [],
                'content_issues': []
            }
            
            # 1. Check for title
            title_tag = soup.find('title')
            if title_tag:
                findings['has_title'] = True
                findings['title_text'] = title_tag.get_text()
            else:
                findings['missing_elements'].append('No <title> tag')
            
            # 2. Check for favicon
            favicon = soup.find('link', rel=re.compile(r'icon', re.I))
            findings['has_favicon'] = favicon is not None
            if not favicon:
                findings['missing_elements'].append('No favicon')
            
            # 3. Check for hidden elements
            hidden_elements = soup.find_all(style=re.compile(r'display\s*:\s*none', re.I))
            hidden_elements += soup.find_all(style=re.compile(r'visibility\s*:\s*hidden', re.I))
            findings['hidden_elements'] = [str(elem)[:100] for elem in hidden_elements[:5]]
            
            # 4. Check meta tags
            meta_refresh = soup.find('meta', attrs={'http-equiv': re.compile(r'refresh', re.I)})
            if meta_refresh:
                findings['suspicious_meta_tags'].append({
                    'type': 'auto-refresh',
                    'content': meta_refresh.get('content', '')
                })
            
            # 5. Check for hidden iframes
            iframes = soup.find_all('iframe')
            for iframe in iframes:
                style = iframe.get('style', '')
                if 'display:none' in style or 'visibility:hidden' in style:
                    findings['hidden_iframes'].append({
                        'src': iframe.get('src', ''),
                        'style': style
                    })
            
            # 6. Count password fields
            password_fields = soup.find_all('input', type='password')
            findings['password_fields_count'] = len(password_fields)
            
            # 7. Count total input fields
            input_fields = soup.find_all('input')
            findings['input_fields_count'] = len(input_fields)
            
            # 8. Check for external forms
            forms = soup.find_all('form')
            for form in forms:
                action = form.get('action', '')
                if action and action.startswith('http') and url not in action:
                    findings['external_forms'].append({
                        'action': action,
                        'method': form.get('method', 'GET'),
                        'has_password_field': len(form.find_all('input', type='password')) > 0
                    })
            
            # 9. Check for content issues
            body_text = soup.get_text()
            
            # Common typos/issues
            if 'copywrite' in body_text.lower():  # Should be "copyright"
                findings['content_issues'].append('Typo: "copywrite" instead of "copyright"')
            
            if 'click here' in body_text.lower():
                findings['content_issues'].append('Suspicious: Generic "click here" links')
            
            # 10. Generate risk indicators
            findings['risk_indicators'] = self._generate_risk_indicators(findings)
            
            return findings
            
        except Exception as e:
            logger.error(f"Error analyzing HTML: {str(e)}")
            return {'error': str(e)}
    
    def _generate_risk_indicators(self, findings: Dict) -> List[str]:
        """Generate list of risk indicators"""
        indicators = []
        
        if not findings['has_title']:
            indicators.append('Missing title tag - unprofessional')
        
        if not findings['has_favicon']:
            indicators.append('No favicon - suspicious')
        
        if len(findings['hidden_elements']) > 0:
            indicators.append(f'Found {len(findings["hidden_elements"])} hidden elements')
        
        if len(findings['hidden_iframes']) > 0:
            indicators.append(f'Hidden iframes detected - may load malicious content')
        
        if len(findings['external_forms']) > 0:
            indicators.append(f'Form submits to external domain - credential theft risk')
        
        if findings['password_fields_count'] > 0 and len(findings['external_forms']) > 0:
            indicators.append('CRITICAL: Password field submitting to external site')
        
        if len(findings['suspicious_meta_tags']) > 0:
            indicators.append('Auto-refresh meta tag - potential redirect scam')
        
        if len(findings['content_issues']) > 0:
            indicators.extend(findings['content_issues'])
        
        return indicators
