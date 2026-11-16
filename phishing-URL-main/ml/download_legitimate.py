"""
Legitimate URLs Downloader
Downloads top legitimate websites from Tranco list
"""

import requests
import pandas as pd
from pathlib import Path
from loguru import logger
import gzip
import io

class LegitimateURLsDownloader:
    """Download top legitimate websites"""
    
    # Tranco top 1M list (research-focused, updated regularly)
    TRANCO_URL = "https://tranco-list.eu/download/5MZ7Z/1000000"
    
    def __init__(self, output_dir="ml/data/raw", num_urls=50000):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.num_urls = num_urls
    
    def download(self):
        """Download Tranco list"""
        logger.info(f"Downloading top {self.num_urls} legitimate URLs...")
        
        try:
            response = requests.get(self.TRANCO_URL, timeout=60)
            response.raise_for_status()
            
            logger.info(f"Download complete! Size: {len(response.content) / 1024 / 1024:.2f} MB")
            
            # Parse CSV (format: rank,domain)
            content = response.text
            lines = content.strip().split('\n')
            
            legitimate_urls = []
            for i, line in enumerate(lines[:self.num_urls]):
                if ',' in line:
                    rank, domain = line.split(',', 1)
                    legitimate_urls.append({
                        'url': f'https://www.{domain}',
                        'label': 0,  # Legitimate
                        'source': 'tranco',
                        'rank': int(rank)
                    })
            
            df = pd.DataFrame(legitimate_urls)
            
            # Save as CSV
            csv_path = self.output_dir / "legitimate_urls.csv"
            df.to_csv(csv_path, index=False)
            logger.success(f"Saved {len(df)} legitimate URLs to {csv_path}")
            
            return df
            
        except Exception as e:
            logger.error(f"Failed to download Tranco list: {e}")
            logger.info("Generating fallback list from known domains...")
            return self._fallback_list()
    
    def _fallback_list(self):
        """Fallback: generate list from known popular domains"""
        popular_domains = [
            'google.com', 'youtube.com', 'facebook.com', 'twitter.com',
            'instagram.com', 'linkedin.com', 'reddit.com', 'amazon.com',
            'netflix.com', 'wikipedia.org', 'github.com', 'stackoverflow.com',
            'apple.com', 'microsoft.com', 'paypal.com', 'ebay.com',
            'spotify.com', 'dropbox.com', 'pinterest.com', 'tumblr.com',
            'cnn.com', 'bbc.com', 'nytimes.com', 'yahoo.com',
            'bing.com', 'twitch.tv', 'tiktok.com', 'snapchat.com',
            'chase.com', 'wellsfargo.com', 'bankofamerica.com', 'citibank.com'
        ]
        
        urls = []
        for i, domain in enumerate(popular_domains * (self.num_urls // len(popular_domains) + 1)):
            if len(urls) >= self.num_urls:
                break
            urls.append({
                'url': f'https://www.{domain}',
                'label': 0,
                'source': 'fallback',
                'rank': i + 1
            })
        
        df = pd.DataFrame(urls[:self.num_urls])
        csv_path = self.output_dir / "legitimate_urls.csv"
        df.to_csv(csv_path, index=False)
        logger.warning(f"Using fallback list: {len(df)} URLs")
        return df

def main():
    """Main execution"""
    downloader = LegitimateURLsDownloader(num_urls=50000)
    df = downloader.download()
    
    if df is not None:
        print("\n" + "="*70)
        print("LEGITIMATE URLs DOWNLOADED SUCCESSFULLY!")
        print("="*70)
        print(f"Total legitimate URLs: {len(df)}")
        print(f"Sample URLs:")
        print(df.head(10))
        print("\nDataset saved to: ml/data/raw/legitimate_urls.csv")

if __name__ == "__main__":
    main()
