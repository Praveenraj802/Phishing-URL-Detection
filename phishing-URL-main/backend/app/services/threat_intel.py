import requests
import json
from loguru import logger
from typing import Optional
from app.core.config import settings

class ThreatIntelligence:
    """Service for querying external Threat Intelligence APIs"""
    
    def __init__(self):
        self.google_api_key = settings.google_safe_browsing_api_key
        self.google_api_url = f"https://safebrowsing.googleapis.com/v4/threatMatches:find?key={self.google_api_key}"
        
    def check_url(self, url: str) -> Optional[bool]:
        """
        Check if a URL is flagged by Threat Intelligence APIs.
        Returns:
            True if flagged as malicious
            False if not flagged
            None if API key is missing or request failed
        """
        if not self.google_api_key:
            return None
            
        try:
            payload = {
                "client": {
                    "clientId": "phishing-detector",
                    "clientVersion": "1.0.0"
                },
                "threatInfo": {
                    "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING", "UNWANTED_SOFTWARE", "POTENTIALLY_HARMFUL_APPLICATION"],
                    "platformTypes": ["ANY_PLATFORM"],
                    "threatEntryTypes": ["URL"],
                    "threatEntries": [
                        {"url": url}
                    ]
                }
            }
            
            response = requests.post(self.google_api_url, json=payload, timeout=2.0)
            
            if response.status_code == 200:
                data = response.json()
                # If matches exist, it's flagged
                if "matches" in data and len(data["matches"]) > 0:
                    logger.warning(f"THREAT INTEL: URL flagged by Google Safe Browsing! {url}")
                    return True
                return False
            else:
                logger.error(f"Safe Browsing API Error: {response.status_code}")
                return None
                
        except requests.exceptions.Timeout:
            logger.warning("Threat Intel API Timeout. Proceeding with local ensemble.")
            return None
        except Exception as e:
            logger.error(f"Threat Intel API Error: {e}")
            return None

intel_service = ThreatIntelligence()
