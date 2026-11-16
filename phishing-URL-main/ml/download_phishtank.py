"""
PhishTank Dataset Downloader
Downloads verified phishing URLs from PhishTank
"""

import requests
import json
import pandas as pd
from pathlib import Path
import time
from loguru import logger

class PhishTankDownloader:
    """Download and process PhishTank dataset"""
    
    # Public data feed (no API key needed)
    DATA_URL = "http://data.phishtank.com/data/online-valid.json"
    
    def __init__(self, output_dir="ml/data/raw"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def download(self):
        """Download PhishTank dataset"""
        logger.info("Downloading PhishTank dataset...")
        logger.info(f"URL: {self.DATA_URL}")
        
        try:
            # Download with user agent (PhishTank requires this)
            headers = {
                'User-Agent': 'phishing-detector/1.0'
            }
            
            response = requests.get(self.DATA_URL, headers=headers, timeout=60)
            response.raise_for_status()
            
            logger.info(f"Download complete! Size: {len(response.content) / 1024 / 1024:.2f} MB")
            
            # Parse JSON
            data = response.json()
            logger.info(f"Found {len(data)} phishing URLs")
            
            # Save raw JSON
            json_path = self.output_dir / "phishtank_raw.json"
            with open(json_path, 'w') as f:
                json.dump(data, f)
            logger.info(f"Saved raw JSON: {json_path}")
            
            # Convert to DataFrame
            df = pd.DataFrame(data)
            
            # Extract relevant columns
            phishing_urls = []
            for entry in data:
                phishing_urls.append({
                    'url': entry.get('url', ''),
                    'label': 1,  # All are phishing
                    'source': 'phishtank',
                    'verified': entry.get('verified', 'unknown'),
                    'submission_time': entry.get('submission_time', '')
                })
            
            df_clean = pd.DataFrame(phishing_urls)
            
            # Save as CSV
            csv_path = self.output_dir / "phishtank_phishing.csv"
            df_clean.to_csv(csv_path, index=False)
            logger.success(f"Saved {len(df_clean)} phishing URLs to {csv_path}")
            
            return df_clean
            
        except Exception as e:
            logger.error(f"Failed to download PhishTank data: {e}")
            logger.info("Alternative: Download manually from https://phishtank.org/developer_info.php")
            return None

def main():
    """Main execution"""
    downloader = PhishTankDownloader()
    df = downloader.download()
    
    if df is not None:
        print("\n" + "="*70)
        print("PHISHTANK DATASET DOWNLOADED SUCCESSFULLY!")
        print("="*70)
        print(f"Total phishing URLs: {len(df)}")
        print(f"Sample URLs:")
        print(df.head(10))
        print("\nDataset saved to: ml/data/raw/phishtank_phishing.csv")
    else:
        print("\nDownload failed. Please download manually.")

if __name__ == "__main__":
    main()
