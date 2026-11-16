"""
Deep Scanner - Orchestrates content analysis for phishing detection
Combines web fetching, HTML analysis, JavaScript analysis, and form analysis
"""

from typing import Dict, Any
from loguru import logger

from .web_fetcher import WebFetcher
from .html_analyzer import HTMLAnalyzer
from .javascript_analyzer import JavaScriptAnalyzer
from .form_analyzer import FormAnalyzer


class DeepScanner:
    """
    Orchestrates deep content analysis for URLs
    """
    
    def __init__(self):
        """Initialize deep scanner with all analyzers"""
        self.web_fetcher = WebFetcher(timeout=10)
        self.html_analyzer = HTMLAnalyzer()
        self.js_analyzer = JavaScriptAnalyzer()
        self.form_analyzer = FormAnalyzer()
    
    def perform_deep_scan(self, url: str, static_score: float) -> Dict[str, Any]:
        """
        Perform comprehensive content analysis
        
        Args:
            url: URL to analyze
            static_score: Initial risk score from static URL analysis
            
        Returns:
            Comprehensive analysis results
        """
        logger.info(f"Starting deep scan for: {url}")
        
        result = {
            'url': url,
            'scan_type': 'deep_scan',
            'static_risk_score': static_score,
            'content_risk_score': 0.0,
            'combined_risk_score': 0.0,
            'evidence': {
                'web_fetch': {},
                'html_analysis': {},
                'javascript_analysis': {},
                'form_analysis': {}
            },
            'critical_findings': [],
            'high_findings': [],
            'medium_findings': [],
            'detailed_reasons': [],
            'scan_successful': False
        }
        
        try:
            # Step 1: Fetch website
            logger.info("Step 1: Fetching website...")
            fetch_result = self.web_fetcher.fetch_website(url)
            result['evidence']['web_fetch'] = fetch_result
            
            if not fetch_result.get('success'):
                # Site couldn't be fetched
                error_type = fetch_result.get('error', 'unknown')
                
                if error_type == 'ssl_error':
                    result['critical_findings'].append('SSL certificate validation failed')
                    result['content_risk_score'] += 0.3
                elif error_type == 'connection_error':
                    result['medium_findings'].append('Website could not be reached')
                
                result['scan_successful'] = False
                result['combined_risk_score'] = min(1.0, static_score + result['content_risk_score'])
                return result
            
            html_content = fetch_result.get('html_content', '')
            
            # Step 2: Analyze HTML
            logger.info("Step 2: Analyzing HTML structure...")
            html_analysis = self.html_analyzer.analyze(html_content, url)
            result['evidence']['html_analysis'] = html_analysis
            
            # Add HTML findings
            if html_analysis.get('risk_indicators'):
                for indicator in html_analysis['risk_indicators']:
                    if 'CRITICAL' in indicator:
                        result['critical_findings'].append(indicator)
                        result['content_risk_score'] += 0.15
                    elif 'external' in indicator.lower() and 'password' in indicator.lower():
                        result['critical_findings'].append(indicator)
                        result['content_risk_score'] += 0.25
                    else:
                        result['medium_findings'].append(indicator)
                        result['content_risk_score'] += 0.05
            
            # Step 3: Analyze JavaScript
            logger.info("Step 3: Analyzing JavaScript code...")
            js_analysis = self.js_analyzer.analyze(html_content)
            result['evidence']['javascript_analysis'] = js_analysis
            
            # Add JS findings
            if js_analysis.get('keylogger_detected'):
                result['critical_findings'].append('CRITICAL: Keylogger JavaScript detected - captures passwords as you type')
                result['content_risk_score'] += 0.4  # Very high risk
            
            if js_analysis.get('obfuscation_detected'):
                result['high_findings'].append('Obfuscated JavaScript code detected (eval, base64)')
                result['content_risk_score'] += 0.2
            
            if js_analysis.get('auto_submit_detected'):
                result['high_findings'].append('Auto-submit form detected - may steal credentials automatically')
                result['content_risk_score'] += 0.15
            
            # Step 4: Analyze Forms
            logger.info("Step 4: Analyzing forms...")
            form_analysis = self.form_analyzer.analyze(html_content, url)
            result['evidence']['form_analysis'] = form_analysis
            
            # Add form findings
            if form_analysis.get('detailed_findings'):
                for finding in form_analysis['detailed_findings']:
                    severity = finding.get('severity', 'medium')
                    message = finding.get('finding', '')
                    
                    if severity == 'critical':
                        result['critical_findings'].append(message)
                        result['content_risk_score'] += 0.25
                    elif severity == 'high':
                        result['high_findings'].append(message)
                        result['content_risk_score'] += 0.15
            
            # Step 5: Calculate combined score
            result['combined_risk_score'] = min(1.0, static_score + result['content_risk_score'])
            
            # Step 6: Generate detailed reasons
            result['detailed_reasons'] = self._generate_detailed_reasons(result)
            
            result['scan_successful'] = True
            logger.info(f"Deep scan complete. Content risk: {result['content_risk_score']:.2f}, Combined: {result['combined_risk_score']:.2f}")
            
        except Exception as e:
            logger.error(f"Error during deep scan: {str(e)}")
            result['scan_successful'] = False
            result['error'] = str(e)
        
        return result
    
    def _generate_detailed_reasons(self, result: Dict) -> list:
        """Generate human-readable detailed reasons"""
        reasons = []
        
        # Critical findings first
        for finding in result['critical_findings']:
            reasons.append(f"✗ {finding}")
        
        # High severity findings
        for finding in result['high_findings'][:3]:  # Limit to top 3
            reasons.append(f"⚠ {finding}")
        
        # Medium findings
        for finding in result['medium_findings'][:2]:  # Limit to top 2
            reasons.append(f"• {finding}")
        
        # Add fetch info
        web_fetch = result['evidence'].get('web_fetch', {})
        if web_fetch.get('redirect_count', 0) > 2:
            reasons.append(f"• Multiple redirects detected ({web_fetch['redirect_count']})")
        
        return reasons
    
    def should_perform_deep_scan(self, static_score: float, threshold: float = 0.10) -> bool:
        """
        Determine if deep scan should be performed
        
        Args:
            static_score: Static analysis risk score (0-1)
            threshold: Minimum score to trigger deep scan
            
        Returns:
            True if deep scan should be performed
        """
        return static_score >= threshold
