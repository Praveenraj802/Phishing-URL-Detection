"""
Dataset Preparation Script
Downloads and prepares phishing datasets for training
"""

import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split
from app.features.feature_extractor import URLFeatureExtractor
from app.core.logging import app_logger as logger


def prepare_sample_dataset():
    """
    Create a sample dataset for testing
    In production, replace this with actual PhishTank/OpenPhish data
    """
    logger.info("Creating sample dataset...")
    
    # Sample phishing URLs (expanded for better training)
    phishing_urls = [
        # Typosquatting attacks
        "http://www.paypai.com/signin",
        "http://www.amazom.com/login",
        "http://www.faceboook.com/security",
        "http://www.gooogle.com/verify",
        "http://www.micros0ft.com/account",
        
        # Subdomain attacks
        "http://secure-login-verify.suspicious-domain.com/account/verify?token=abc123",
        "http://paypal.secure-login.com/update",
        "http://amazon.account-verify.com/signin",
        "http://facebook.security-check.com/login",
        "http://google.account-recovery.net/reset",
        
        # IP-based URLs
        "http://192.168.1.1/admin/login.php",
        "http://45.142.212.61/paypal/login",
        "http://103.224.182.251/banking/secure",
        
        # Suspicious keywords
        "http://paypal-security-alert.com/update-account",
        "http://amazon-account-locked.com/verify/signin",
        "http://apple-id-verify.com/account/locked",
        "http://banking-alert.suspicious.com/confirm",
        "http://microsoft-account-suspended.com/reactivate",
        "http://google-security-alert.xyz/verify",
        "http://ebay-account-verification.com/update",
        "http://netflix-billing-problem.com/payment",
        "http://your-account-paypal.com/security/update",
        
        # Non-HTTPS with sensitive operations
        "http://secure-signin-banking.com/login.aspx",
        "http://www.apple-support-verification.com/account",
        "http://amazon-prime-renewal.com/billing/update",
        "http://facebook-security-department.com/verify",
        "http://microsoft-windows-update.com/security/patch",
        "http://paypal-resolution-center.com/dispute",
        
        # URL shorteners
        "http://bit.ly/suspicious123",
        "http://tinyurl.com/bank-verify",
        "http://goo.gl/paypal-login",
        
        # Long obfuscated URLs
        "http://secure-account.verification-required.payment-update.confirm-identity.suspended-account.com/login",
        "http://www.secure-login.com/verify/account/update/confirm/validate/authenticate/signin",
        
        # Homograph attacks (look-alike characters)
        "http://www.gооgle.com/signin",  # Cyrillic 'o'
        "http://www.аpple.com/verify",   # Cyrillic 'a'
        
        # Fake security certificates
        "http://ssl-secure-banking.com/login",
        "http://https-secure-paypal.com/signin",
        
        # Urgent/threatening language
        "http://account-will-be-closed.com/verify-now",
        "http://immediate-action-required.com/confirm",
        "http://final-warning-suspended.com/reactivate",
        
        # Free/prize scams
        "http://claim-your-prize-amazon.com/winner",
        "http://free-iphone-giveaway.com/claim",
        
        # Multiple subdomains
        "http://login.secure.account.paypal.verification.com/signin",
        "http://www.security.verify.amazon.account.com/update",
        
        # Misspelled TLDs
        "http://www.paypal.com.secure-login.net/verify",
        "http://www.amazon.co.uk.verify.com/signin",
    ]
    
    # Sample legitimate URLs (expanded)
    legitimate_urls = [
        # Major tech companies
        "https://www.google.com",
        "https://www.github.com",
        "https://www.stackoverflow.com",
        "https://www.microsoft.com",
        "https://www.apple.com",
        
        # E-commerce
        "https://www.amazon.com",
        "https://www.ebay.com",
        "https://www.etsy.com",
        "https://www.shopify.com",
        
        # Social media
        "https://www.facebook.com",
        "https://www.twitter.com",
        "https://www.linkedin.com",
        "https://www.instagram.com",
        "https://www.reddit.com",
        "https://www.youtube.com",
        "https://www.tiktok.com",
        
        # Financial services
        "https://www.paypal.com",
        "https://www.stripe.com",
        "https://www.chase.com",
        "https://www.bankofamerica.com",
        
        # Streaming services
        "https://www.netflix.com",
        "https://www.spotify.com",
        "https://www.hulu.com",
        
        # News and media
        "https://www.cnn.com",
        "https://www.bbc.com",
        "https://www.nytimes.com",
        "https://www.theguardian.com",
        
        # Reference
        "https://www.wikipedia.org",
        "https://www.merriam-webster.com",
        
        # Cloud services
        "https://drive.google.com",
        "https://www.dropbox.com",
        "https://onedrive.live.com",
        
        # Development
        "https://www.github.io",
        "https://docs.python.org",
        "https://developer.mozilla.org",
        
        # Education
        "https://www.coursera.org",
        "https://www.udemy.com",
        "https://www.khanacademy.org",
        
        # Government
        "https://www.usa.gov",
        "https://www.gov.uk",
        
        # Search engines
        "https://www.bing.com",
        "https://www.duckduckgo.com",
        
        # Email providers
        "https://mail.google.com",
        "https://outlook.live.com",
        
        # Travel
        "https://www.booking.com",
        "https://www.airbnb.com",
    ]
    
    # Create dataframe
    urls = phishing_urls + legitimate_urls
    labels = [1] * len(phishing_urls) + [0] * len(legitimate_urls)  # 1 = phishing, 0 = legitimate
    
    df = pd.DataFrame({
        'url': urls,
        'label': labels
    })
    
    # Shuffle the dataset
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    logger.info(f"Created sample dataset with {len(df)} URLs")
    logger.info(f"Phishing: {sum(labels)}, Legitimate: {len(labels) - sum(labels)}")
    
    return df


def extract_features_from_dataset(df):
    """
    Extract features from all URLs in the dataset
    
    Args:
        df: DataFrame with 'url' and 'label' columns
        
    Returns:
        DataFrame with features and labels
    """
    logger.info("Extracting features from URLs...")
    
    extractor = URLFeatureExtractor()
    feature_names = extractor.get_feature_names()
    
    features_list = []
    labels_list = []
    valid_urls = []
    
    for idx, row in df.iterrows():
        try:
            features = extractor.extract_feature_vector(row['url'])
            features_list.append(features)
            labels_list.append(row['label'])
            valid_urls.append(row['url'])
        except Exception as e:
            logger.warning(f"Failed to extract features from {row['url']}: {e}")
    
    # Create features DataFrame
    features_df = pd.DataFrame(features_list, columns=feature_names)
    features_df['url'] = valid_urls
    features_df['label'] = labels_list
    
    logger.info(f"Successfully extracted features from {len(features_df)} URLs")
    
    return features_df


def prepare_train_test_split(features_df, test_size=0.2, val_size=0.1):
    """
    Split dataset into train, validation, and test sets
    
    Args:
        features_df: DataFrame with features and labels
        test_size: Proportion of test set
        val_size: Proportion of validation set
        
    Returns:
        Dictionary with train, val, and test splits
    """
    logger.info("Splitting dataset...")
    
    # Separate features and labels
    X = features_df.drop(['url', 'label'], axis=1)
    y = features_df['label']
    urls = features_df['url']
    
    # First split: train+val vs test
    X_temp, X_test, y_temp, y_test, urls_temp, urls_test = train_test_split(
        X, y, urls, test_size=test_size, random_state=42, stratify=y
    )
    
    # Second split: train vs val
    val_size_adjusted = val_size / (1 - test_size)
    X_train, X_val, y_train, y_val, urls_train, urls_val = train_test_split(
        X_temp, y_temp, urls_temp, test_size=val_size_adjusted, random_state=42, stratify=y_temp
    )
    
    logger.info(f"Train set: {len(X_train)} samples")
    logger.info(f"Validation set: {len(X_val)} samples")
    logger.info(f"Test set: {len(X_test)} samples")
    
    return {
        'X_train': X_train,
        'y_train': y_train,
        'urls_train': urls_train,
        'X_val': X_val,
        'y_val': y_val,
        'urls_val': urls_val,
        'X_test': X_test,
        'y_test': y_test,
        'urls_test': urls_test,
        'feature_names': X.columns.tolist()
    }


def save_dataset(data_dict, output_dir='ml/data'):
    """
    Save prepared dataset to disk
    
    Args:
        data_dict: Dictionary with train/val/test splits
        output_dir: Output directory path
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Saving dataset to {output_dir}...")
    
    # Save as CSV
    pd.DataFrame({
        'X': data_dict['X_train'].values.tolist(),
        'y': data_dict['y_train'],
        'url': data_dict['urls_train']
    }).to_csv(output_path / 'train.csv', index=False)
    
    pd.DataFrame({
        'X': data_dict['X_val'].values.tolist(),
        'y': data_dict['y_val'],
        'url': data_dict['urls_val']
    }).to_csv(output_path / 'val.csv', index=False)
    
    pd.DataFrame({
        'X': data_dict['X_test'].values.tolist(),
        'y': data_dict['y_test'],
        'url': data_dict['urls_test']
    }).to_csv(output_path / 'test.csv', index=False)
    
    # Save as numpy arrays for faster loading
    np.save(output_path / 'X_train.npy', data_dict['X_train'].values)
    np.save(output_path / 'y_train.npy', data_dict['y_train'].values)
    np.save(output_path / 'X_val.npy', data_dict['X_val'].values)
    np.save(output_path / 'y_val.npy', data_dict['y_val'].values)
    np.save(output_path / 'X_test.npy', data_dict['X_test'].values)
    np.save(output_path / 'y_test.npy', data_dict['y_test'].values)
    
    # Save feature names
    with open(output_path / 'feature_names.txt', 'w') as f:
        f.write('\n'.join(data_dict['feature_names']))
    
    logger.info("Dataset saved successfully!")


if __name__ == "__main__":
    # Prepare sample dataset
    df = prepare_sample_dataset()
    
    # Extract features
    features_df = extract_features_from_dataset(df)
    
    # Split dataset
    data_dict = prepare_train_test_split(features_df)
    
    # Save dataset
    save_dataset(data_dict)
    
    print("\n✓ Dataset preparation complete!")
    print(f"  Train samples: {len(data_dict['X_train'])}")
    print(f"  Validation samples: {len(data_dict['X_val'])}")
    print(f"  Test samples: {len(data_dict['X_test'])}")
    print(f"  Features: {len(data_dict['feature_names'])}")
