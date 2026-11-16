"""
Web Fetcher - Fetch website content with browser automation
Uses requests for simple fetching and browser automation for JavaScript-heavy sites
"""

import requests
from typing import Dict, Any, Optional
from urllib.parse import urlparse
import re
from loguru import logger


class WebFetcher:
    """Fetch and analyze website content"""
    
    def __init__(self, timeout: int = 10):
        """
        Initialize web fetcher
        
        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
    
    def fetch_website(self, url: str) -> Dict[str, Any]:
        """
        Fetch website content
        
        Args:
            url: URL to fetch
            
        Returns:
            Dictionary with response data
        """
        try:
            logger.info(f"Fetching website: {url}")
            
            response = self.session.get(
                url,
                timeout=self.timeout,
                allow_redirects=True,
                verify=True  # Verify SSL certificates
            )
            
            result = {
                'success': True,
                'status_code': response.status_code,
                'html_content': response.text,
                'headers': dict(response.headers),
                'final_url': response.url,
                'redirect_count': len(response.history),
                'response_time_ms': int(response.elapsed.total_seconds() * 1000),
                'content_length': len(response.content),
                'encoding': response.encoding,
            }
            
            # Check for SSL
            if response.url.startswith('https://'):
                result['has_ssl'] = True
            else:
                result['has_ssl'] = False
            
            logger.info(f"Successfully fetched {url} - Status: {response.status_code}")
            
            return result
            
        except requests.exceptions.SSLError as e:
            logger.warning(f"SSL error for {url}: {str(e)}")
            return {
                'success': False,
                'error': 'ssl_error',
                'error_message': 'Invalid or expired SSL certificate',
                'has_ssl': False
            }
            
        except requests.exceptions.Timeout:
            logger.warning(f"Timeout fetching {url}")
            return {
                'success': False,
                'error': 'timeout',
                'error_message': f'Request timed out after {self.timeout} seconds'
            }
            
        except requests.exceptions.ConnectionError as e:
            logger.warning(f"Connection error for {url}: {str(e)}")
            return {
                'success': False,
                'error': 'connection_error',
                'error_message': 'Could not connect to website'
            }
            
        except Exception as e:
            logger.error(f"Error fetching {url}: {str(e)}")
            return {
                'success': False,
                'error': 'unknown',
                'error_message': str(e)
            }
    
    def check_redirects(self, url: str) -> Dict[str, Any]:
        """
        Check if URL redirects and analyze redirect chain
        
        Args:
            url: URL to check
            
        Returns:
            Redirect information
        """
        try:
            response = self.session.get(url, timeout=self.timeout, allow_redirects=True)
            
            redirects = []
            for resp in response.history:
                redirects.append({
                    'url': resp.url,
                    'status_code': resp.status_code
                })
            
            return {
                'has_redirects': len(redirects) > 0,
                'redirect_count': len(redirects),
                'redirect_chain': redirects,
                'final_url': response.url
            }
            
        except Exception as e:
            logger.error(f"Error checking redirects for {url}: {str(e)}")
            return {'has_redirects': False, 'redirect_count': 0}
