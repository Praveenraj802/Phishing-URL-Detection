"""
Kaggle Dataset Downloader
Downloads phishing dataset from Kaggle (alternative to PhishTank)

INSTRUCTIONS:
1. Install kaggle CLI: pip install kaggle
2. Get API token from https://www.kaggle.com/settings
3. Save to ~/.kaggle/kaggle.json (or %USERPROFILE%\.kaggle\kaggle.json on Windows)
"""

import subprocess
import pandas as pd
from pathlib import Path
from loguru import logger
import os

class KaggleDatasetDownloader:
    """Download phishing datasets from Kaggle"""
    
    # Popular phishing datasets on Kaggle
    DATASETS = [
        "shashwatwork/web-page-phishing-detection-dataset",
        "eswarchandt/phishing-website-detector",
        "akashkr/phishing-website-dataset"
    ]
    
    def __init__(self, output_dir="ml/data/raw"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def check_kaggle_setup(self):
        """Check if Kaggle CLI is configured"""
        try:
            result = subprocess.run(['kaggle', '--version'], capture_output=True, text=True)
            logger.info(f"Kaggle CLI version: {result.stdout.strip()}")
            return True
        except FileNotFoundError:
            logger.error("Kaggle CLI not found! Install with: pip install kaggle")
            return False
    
    def download_dataset(self, dataset_name):
        """Download a specific dataset from Kaggle"""
        logger.info(f"Downloading {dataset_name}...")
        
        try:
            # Download using kaggle CLI
            cmd = ['kaggle', 'datasets', 'download', '-d', dataset_name, '-p', str(self.output_dir), '--unzip']
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.success(f"Downloaded {dataset_name}")
                return True
            else:
                logger.error(f"Failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error downloading {dataset_name}: {e}")
            return False
    
    def process_downloaded_files(self):
        """Process downloaded CSV files and standardize format"""
        logger.info("Processing downloaded files...")
        
        all_phishing = []
        
        # Find all CSV files in output directory
        csv_files = list(self.output_dir.glob("*.csv"))
        logger.info(f"Found {len(csv_files)} CSV files")
        
        for csv_file in csv_files:
            try:
                df = pd.read_csv(csv_file)
                logger.info(f"Processing {csv_file.name}: {len(df)} rows")
                
                # Try to identify URL and label columns
                url_col = None
                label_col = None
                
                for col in df.columns:
                    col_lower = col.lower()
                    if 'url' in col_lower or 'link' in col_lower:
                        url_col = col
                    if 'label' in col_lower or 'class' in col_lower or 'target' in col_lower:
                        label_col = col
                
                if url_col and label_col:
                    # Extract and standardize
                    df_clean = pd.DataFrame({
                        'url': df[url_col],
                        'label': df[label_col].apply(lambda x: 1 if x in [1, 'phishing', 'bad', '1'] else 0),
                        'source': f'kaggle_{csv_file.stem}'
                    })
                    
                    # Filter only phishing URLs
                    phishing_urls = df_clean[df_clean['label'] == 1]
                    all_phishing.append(phishing_urls)
                    logger.info(f"  Found {len(phishing_urls)} phishing URLs")
                
            except Exception as e:
                logger.warning(f"Skipped {csv_file.name}: {e}")
                continue
        
        if all_phishing:
            # Combine all phishing URLs
            df_combined = pd.concat(all_phishing, ignore_index=True)
            df_combined = df_combined.drop_duplicates(subset=['url'])
            
            # Save
            output_file = self.output_dir / "kaggle_phishing.csv"
            df_combined.to_csv(output_file, index=False)
            logger.success(f"Saved {len(df_combined)} phishing URLs to {output_file}")
            return df_combined
        
        return None
    
    def download_all(self):
        """Try to download multiple datasets"""
        if not self.check_kaggle_setup():
            logger.error("Please set up Kaggle CLI first!")
            logger.info("Instructions:")
            logger.info("1. pip install kaggle")
            logger.info("2. Get API token from https://www.kaggle.com/settings")
            logger.info("3. Save to ~/.kaggle/kaggle.json")
            return None
        
        success_count = 0
        for dataset in self.DATASETS:
            if self.download_dataset(dataset):
                success_count += 1
        
        logger.info(f"Downloaded {success_count}/{len(self.DATASETS)} datasets")
        
        # Process all downloaded files
        return self.process_downloaded_files()

def main():
    """Main execution"""
    downloader = KaggleDatasetDownloader()
    df = downloader.download_all()
    
    if df is not None:
        print("\n" + "="*70)
        print("KAGGLE DATASETS DOWNLOADED SUCCESSFULLY!")
        print("="*70)
        print(f"Total phishing URLs: {len(df)}")
        print(f"Sample URLs:")
        print(df.head(10))
        print("\nDataset saved to: ml/data/raw/kaggle_phishing.csv")
    else:
        print("\nDownload failed or Kaggle not configured.")
        print("Please follow setup instructions above.")

if __name__ == "__main__":
    main()
