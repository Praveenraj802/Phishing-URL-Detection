"""
JavaScript Analyzer - Detect malicious JavaScript patterns
"""

import re
from typing import Dict, Any, List
from loguru import logger


class JavaScriptAnalyzer:
    """Analyze JavaScript code for malicious patterns"""
    
    # Suspicious patterns
    MALICIOUS_PATTERNS = {
        'obfuscation': [
            r'eval\s*\(',
            r'atob\s*\(',  # base64 decode
            r'String\.fromCharCode',
            r'unescape\s*\(',
            r'document\.write\s*\(\s*unescape'
        ],
        'keylogger': [
            r'onkeypress\s*=',
            r'onkeydown\s*=',
            r'onkeyup\s*=',
            r'addEventListener\s*\(\s*["\']key',
            r'document\.getElementById\([^)]+\)\.onkey'
        ],
        'auto_submit': [
            r'\.submit\s*\(\s*\)',
            r'setTimeout\s*\([^)]*\.submit',
            r'setInterval\s*\([^)]*\.submit'
        ],
        'clipboard_access': [
            r'navigator\.clipboard',
            r'document\.execCommand\s*\(\s*["\']copy',
            r'document\.execCommand\s*\(\s*["\']paste'
        ],
        'redirect': [
            r'window\.location\s*=',
            r'window\.location\.replace',
            r'window\.location\.href\s*='
        ],
        'console_blocking': [
            r'addEventListener\s*\(\s*["\']contextmenu',
            r'preventDefault\s*\(\s*\)',
            r'addEventListener\s*\(\s*["\']keydown.*F12'
        ]
    }
    
    def __init__(self):
        """Initialize JavaScript analyzer"""
        pass
    
    def analyze(self, html_content: str) -> Dict[str, Any]:
        """
        Analyze JavaScript in HTML for malicious patterns
        
        Args:
            html_content: HTML content  containing scripts
            
        Returns:
            Dictionary with analysis results
        """
        try:
            # Extract all JavaScript
            scripts = self._extract_scripts(html_content)
            
            findings = {
                'total_scripts': len(scripts),
                'inline_scripts': 0,
                'external_scripts': 0,
                'malicious_patterns_found': [],
                'obfuscation_detected': False,
                'keylogger_detected': False,
                'auto_submit_detected': False,
                'suspicious_code_snippets': [],
                'risk_score': 0
            }
            
            all_js_code = '\n'.join(scripts)
            
            # Analyze each pattern category
            for category, patterns in self.MALICIOUS_PATTERNS.items():
                matches = self._check_patterns(all_js_code, patterns, category)
                if matches:
                    findings['malicious_patterns_found'].extend(matches)
                    
                    # Set specific flags
                    if category == 'obfuscation':
                        findings['obfuscation_detected'] = True
                        findings['risk_score'] += 2
                    elif category == 'keylogger':
                        findings['keylogger_detected'] = True
                        findings['risk_score'] += 4  # Critical
                    elif category == 'auto_submit':
                        findings['auto_submit_detected'] = True
                        findings['risk_score'] += 3
            
            # Extract suspicious code snippets
            findings['suspicious_code_snippets'] = self._extract_snippets(all_js_code, findings['malicious_patterns_found'])
            
            # Generate detailed explanations
            findings['detailed_findings'] = self._generate_explanations(findings)
            
            return findings
            
        except Exception as e:
            logger.error(f"Error analyzing JavaScript: {str(e)}")
            return {'error': str(e)}
    
    def _extract_scripts(self, html_content: str) -> List[str]:
        """Extract JavaScript from HTML"""
        scripts = []
        
        # Inline scripts
        inline_pattern = r'<script[^>]*>(.*?)</script>'
        for match in re.finditer(inline_pattern, html_content, re.DOTALL | re.IGNORECASE):
            scripts.append(match.group(1))
        
        # Event handlers
        event_pattern = r'on\w+\s*=\s*["\']([^"\']+)["\']'
        for match in re.finditer(event_pattern, html_content, re.IGNORECASE):
            scripts.append(match.group(1))
        
        return scripts
    
    def _check_patterns(self, code: str, patterns: List[str], category: str) -> List[Dict]:
        """Check code for suspicious patterns"""
        matches = []
        
        for pattern in patterns:
            found = re.finditer(pattern, code, re.IGNORECASE)
            for match in found:
                matches.append({
                    'category': category,
                    'pattern': pattern,
                    'matched_text': match.group(0),
                    'position': match.start()
                })
        
        return matches
    
    def _extract_snippets(self, code: str, patterns_found: List[Dict]) -> List[Dict]:
        """Extract code snippets around matches"""
        snippets = []
        
        for pattern in patterns_found[:5]:  # Limit to 5 snippets
            pos = pattern['position']
            start = max(0, pos - 50)
            end = min(len(code), pos + 100)
            
            snippet = code[start:end].strip()
            
            snippets.append({
                'category': pattern['category'],
                'code': snippet,
                'context': f"Found {pattern['category']} pattern"
            })
        
        return snippets
    
    def _generate_explanations(self, findings: Dict) -> List[str]:
        """Generate human-readable explanations"""
        explanations = []
        
        if findings['obfuscation_detected']:
            explanations.append({
                'severity': 'high',
                'finding': 'Obfuscated JavaScript code detected',
                'explanation': 'Code uses eval(), base64 encoding, or other obfuscation techniques to hide its true purpose'
            })
        
        if findings['keylogger_detected']:
            explanations.append({
                'severity': 'critical',
                'finding': 'Keylogger detected',
                'explanation': 'Code captures keyboard input, potentially stealing passwords and personal information as you type'
            })
        
        if findings['auto_submit_detected']:
            explanations.append({
                'severity': 'high',
                'finding': 'Auto-submit form detected',
                'explanation': 'Forms automatically submit without user interaction, potentially stealing credentials'
            })
        
        return explanations
