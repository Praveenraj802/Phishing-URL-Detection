"""
Dataset Combiner and Processor
Combines PhishTank + Tranco datasets and processes them for ML training
"""

import pandas as pd
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

from app.features.feature_extractor import URLFeatureExtractor
from sklearn.model_selection import train_test_split
from loguru import logger
from tqdm import tqdm
import numpy as np

class DatasetProcessor:
    """Process and combine large datasets"""
    
    def __init__(self, raw_dir="ml/data/raw", output_dir="ml/data"):
        self.raw_dir = Path(raw_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.feature_extractor = URLFeatureExtractor()
    
    def load_datasets(self):
        """Load all downloaded datasets"""
        logger.info("Loading datasets...")
        
        datasets = []
        
        # Load PhishTank (phishing)
        phishtank_path = self.raw_dir / "phishtank_phishing.csv"
        if phishtank_path.exists():
            df_phishing = pd.read_csv(phishtank_path)
            logger.info(f"Loaded {len(df_phishing)} PhishTank URLs")
            datasets.append(df_phishing[['url', 'label']])
        
        # Load Synthetic Phishing
        synthetic_path = self.raw_dir / "synthetic_phishing.csv"
        if synthetic_path.exists():
            df_synthetic = pd.read_csv(synthetic_path)
            logger.info(f"Loaded {len(df_synthetic)} synthetic phishing URLs")
            datasets.append(df_synthetic[['url', 'label']])
        
        # Load Legitimate URLs
        legit_path = self.raw_dir / "legitimate_urls.csv"
        if legit_path.exists():
            df_legit = pd.read_csv(legit_path)
            logger.info(f"Loaded {len(df_legit)} legitimate URLs")
            datasets.append(df_legit[['url', 'label']])
        
        if not datasets:
            raise FileNotFoundError("No datasets found! Please download them first.")
        
        # Combine
        df_combined = pd.concat(datasets, ignore_index=True)
        logger.success(f"Combined dataset: {len(df_combined)} URLs")
        
        return df_combined
    
    def balance_dataset(self, df, max_per_class=50000):
        """Balance the dataset (equal phishing and legitimate)"""
        logger.info("Balancing dataset...")
        
        phishing = df[df['label'] == 1]
        legitimate = df[df['label'] == 0]
        
        logger.info(f"Phishing: {len(phishing)}, Legitimate: {len(legitimate)}")
        
        # Sample equally from both
        n_samples = min(len(phishing), len(legitimate), max_per_class)
        
        phishing_sample = phishing.sample(n=n_samples, random_state=42)
        legitimate_sample = legitimate.sample(n=n_samples, random_state=42)
        
        balanced = pd.concat([phishing_sample, legitimate_sample], ignore_index=True)
        balanced = balanced.sample(frac=1, random_state=42).reset_index(drop=True)
        
        logger.success(f"Balanced dataset: {len(balanced)} URLs ({n_samples} each class)")
        return balanced
    
    def extract_features(self, df):
        """Extract features from URLs with progress bar"""
        logger.info("Extracting features from URLs...")
        
        features_list = []
        urls_processed = []
        labels = []
        
        for idx, row in tqdm(df.iterrows(), total=len(df), desc="Processing URLs"):
            try:
                url = row['url']
                label = row['label']
                
                # Extract features
                features = self.feature_extractor.extract_all_features(url)
                
                # Convert to list (35 features)
                feature_values = [
                    features.get('url_length', 0),
                    features.get('path_length', 0),
                    features.get('query_length', 0),
                    features.get('fragment_length', 0),
                    features.get('num_dots', 0),
                    features.get('num_hyphens', 0),
                    features.get('num_underscores', 0),
                   features.get('num_slashes', 0),
                    features.get('num_question_marks', 0),
                    features.get('num_equals', 0),
                    features.get('num_amps', 0),
                    features.get('num_percent', 0),
                    features.get('num_at', 0),
                    features.get('is_https', 0),
                    features.get('num_subdomains', 0),
                    features.get('is_www', 0),
                    features.get('has_port', 0),
                    features.get('port_number', 0),
                    features.get('has_ip_address', 0),
                    features.get('num_query_params', 0),
                    features.get('num_suspicious_keywords', 0),
                    features.get('is_url_shortener', 0),
                    features.get('special_char_ratio', 0),
                    features.get('digit_ratio', 0),
                    features.get('letter_ratio', 0),
                    features.get('url_entropy', 0),
                    features.get('path_depth', 0),
                    features.get('domain_has_digits', 0),
                    features.get('domain_has_hyphens', 0),
                    features.get('long_url', 0),
                    features.get('excessive_dots', 0),
                    features.get('excessive_hyphens', 0),
                    features.get('suspicious_tld', 0),
                    features.get('has_redirect', 0),
                    features.get('is_typosquatting', 0)
                ]
                
                features_list.append(feature_values)
                urls_processed.append(url)
                labels.append(label)
                
            except Exception as e:
                logger.warning(f"Failed to process URL {url}: {e}")
                continue
        
        logger.success(f"Extracted features for {len(features_list)} URLs")
        
        # Create DataFrame
        X = np.array(features_list)
        y = np.array(labels)
        urls = np.array(urls_processed)
        
        return X, y, urls
    
    def split_and_save(self, X, y, urls):
        """Split into train/test/val and save"""
        logger.info("Splitting dataset...")
        
        # Split: 80% train, 15% test, 5% val
        X_train, X_temp, y_train, y_temp, urls_train, urls_temp = train_test_split(
            X, y, urls, test_size=0.20, random_state=42, stratify=y
        )
        
        X_test, X_val, y_test, y_val, urls_test, urls_val = train_test_split(
            X_temp, y_temp, urls_temp, test_size=0.25, random_state=42, stratify=y_temp
        )
        
        logger.info(f"Train: {len(X_train)}, Test: {len(X_test)}, Val: {len(X_val)}")
        
        # Save numpy arrays
        np.save(self.output_dir / 'X_train.npy', X_train)
        np.save(self.output_dir / 'X_test.npy', X_test)
        np.save(self.output_dir / 'X_val.npy', X_val)
        np.save(self.output_dir / 'y_train.npy', y_train)
        np.save(self.output_dir / 'y_test.npy', y_test)
        np.save(self.output_dir / 'y_val.npy', y_val)
        
        # Save CSVs with URLs for reference
        pd.DataFrame({
            'X': [list(x) for x in X_train],
            'y': y_train,
            'url': urls_train
        }).to_csv(self.output_dir / 'train.csv', index=False)
        
        pd.DataFrame({
            'X': [list(x) for x in X_test],
            'y': y_test,
            'url': urls_test
        }).to_csv(self.output_dir / 'test.csv', index=False)
        
        pd.DataFrame({
            'X': [list(x) for x in X_val],
            'y': y_val,
            'url': urls_val
        }).to_csv(self.output_dir / 'val.csv', index=False)
        
        logger.success("Datasets saved successfully!")
        
        return X_train, X_test, X_val, y_train, y_test, y_val

def main():
    """Main execution"""
    processor = DatasetProcessor()
    
    # Load
    df = processor.load_datasets()
    
    # Balance
    df_balanced = processor.balance_dataset(df, max_per_class=50000)
    
    # Extract features
    X, y, urls = processor.extract_features(df_balanced)
    
    # Split and save
    processor.split_and_save(X, y, urls)
    
    print("\n" + "="*70)
    print("DATASET PROCESSING COMPLETE!")
    print("="*70)
    print(f"Total URLs processed: {len(X)}")
    print(f"Phishing: {sum(y)} | Legitimate: {len(y) - sum(y)}")
    print("\nReady for training!")

if __name__ == "__main__":
    main()
