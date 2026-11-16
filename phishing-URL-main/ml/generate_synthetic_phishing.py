"""
Generate Synthetic Phishing URLs
Creates realistic phishing URLs based on common attack patterns
This is a fallback when external datasets are unavailable
"""

import pandas as pd
from pathlib import Path
import random
from loguru import logger

class SyntheticPhishingGenerator:
    """Generate realistic synthetic phishing URLs"""
    
    LEGIT_BRANDS = [
        'google', 'facebook', 'amazon', 'paypal', 'netflix', 'microsoft',
        'apple', 'twitter', 'instagram', 'linkedin', 'yahoo', 'ebay',
        'spotify', 'dropbox', 'github', 'reddit', 'youtube', 'gmail',
       'outlook', 'chase', 'wellsfargo', 'bankofamerica', 'citibank',
        'americanexpress', 'discover', 'visa', 'mastercard', 'coinbase',
        'whatsapp', 'telegram', 'discord', 'zoom', 'slack', 'shopify',
        'walmart', 'target', 'bestbuy', 'adobe', 'salesforce', 'oracle'
    ]
    
    SUSPICIOUS_KEYWORDS = [
        'verify', 'account', 'update', 'confirm', 'login', 'signin',
        'secure', 'banking', 'suspended', 'locked', 'urgent', 'alert',
        'security', 'validate', 'authenticate', 'billing', 'payment',
        'winner', 'prize', 'claim', 'free', 'reactivate', 'support'
    ]
    
    SUSPICIOUS_TLDS = [
        '.xyz', '.tk', '.ml', '.ga', '.cf', '.info', '.biz', '.top',
        '.club', '.online', '.site', '.website', '.win', '.download'
    ]
    
    def __init__(self, output_dir="ml/data/raw"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_typosquatting(self, brand, num_per_brand=50):
        """Generate typosquatting variations of a brand"""
        variations = []
        
        # 1. Character substitution (0->o, 1->l, etc.)
        substitutions = {'o': '0', 'l': '1', 'i': '1', 'e': '3', 's': '5'}
        for _ in range(10):
            typo = brand
            for orig, sub in substitutions.items():
                if orig in typo and random.random() > 0.7:
                    typo = typo.replace(orig, sub, 1)
            if typo != brand:
                variations.append(f"http://www.{typo}.com")
        
        # 2. Character repetition
        for char_idx in range(len(brand)):
            char = brand[char_idx]
            if char.isalpha():
                repeated = brand[:char_idx] + char * random.choice([2, 3]) + brand[char_idx+1:]
                variations.append(f"http://www.{repeated}.com")
        
        # 3. Missing/extra characters
        for i in range(min(5, len(brand))):
            idx = random.randint(0, len(brand)-1)
            missing = brand[:idx] + brand[idx+1:]
            if len(missing) > 2:
                variations.append(f"http://www.{missing}.com")
        
        # 4. Brand + suspicious keyword
        for keyword in random.sample(self.SUSPICIOUS_KEYWORDS, min(10, len(self.SUSPICIOUS_KEYWORDS))):
            variations.append(f"http://{brand}-{keyword}.com")
            variations.append(f"http://{keyword}-{brand}.com")
            variations.append(f"http://{brand}{keyword}.com")
        
        # 5. Brand + suspicious TLD
        for tld in random.sample(self.SUSPICIOUS_TLDS, min(5, len(self.SUSPICIOUS_TLDS))):
            variations.append(f"http://www.{brand}{tld}")
            variations.append(f"http://{brand}-secure{tld}")
        
        # 6. Subdomain tricks
        for keyword in ['secure', 'login', 'account', 'verify']:
            variations.append(f"http://{brand}.{keyword}-site.com")
            variations.append(f"http://{keyword}.{brand}-check.com")
        
        # Randomly select requested number
        return random.sample(variations, min(num_per_brand, len(variations)))
    
    def generate_ip_based(self, num=500):
        """Generate IP-based phishing URLs"""
        ips = []
        for _ in range(num):
            ip = f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}"
            path = random.choice(['login', 'signin', 'account', 'verify', 'update'])
            ips.append(f"http://{ip}/{path}")
        return ips
    
    def generate_shortener_based(self, num=300):
        """Generate URL shortener-based phishing"""
        shorteners = ['bit.ly', 'tinyurl.com', 'goo.gl', 't.co', 'is.gd']
        urls = []
        for _ in range(num):
            shortener = random.choice(shorteners)
            code = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=7))
            urls.append(f"http://{shortener}/{code}")
        return urls
    
    def generate_dataset(self, num_urls=10000):
        """Generate complete synthetic phishing dataset"""
        logger.info(f"Generating {num_urls} synthetic phishing URLs...")
        
        all_phishing = []
        
        # Typosquatting variations (70% of dataset)
        num_per_brand = (num_urls * 7 // 10) // len(self.LEGIT_BRANDS)
        for brand in self.LEGIT_BRANDS:
            variations = self.generate_typosquatting(brand, num_per_brand)
            all_phishing.extend(variations)
        
        logger.info(f"Generated {len(all_phishing)} typosquatting URLs")
        
        # IP-based (15%)
        ip_urls = self.generate_ip_based(num_urls * 15 // 100)
        all_phishing.extend(ip_urls)
        logger.info(f"Generated {len(ip_urls)} IP-based URLs")
        
        # URL shorteners (15%)
        shortener_urls = self.generate_shortener_based(num_urls * 15 // 100)
        all_phishing.extend(shortener_urls)
        logger.info(f"Generated {len(shortener_urls)} shortener URLs")
        
        # Create DataFrame
        df = pd.DataFrame({
            'url': all_phishing[:num_urls],
            'label': 1,
            'source': 'synthetic'
        })
        
        # Remove duplicates
        df = df.drop_duplicates(subset=['url'])
        
        # Save
        output_file = self.output_dir / "synthetic_phishing.csv"
        df.to_csv(output_file, index=False)
        logger.success(f"Generated {len(df)} synthetic phishing URLs")
        logger.info(f"Saved to {output_file}")
        
        return df

def main():
    """Main execution"""
    generator = SyntheticPhishingGenerator()
    df = generator.generate_dataset(num_urls=50000)
    
    print("\n" + "="*70)
    print("SYNTHETIC PHISHING URLs GENERATED!")
    print("="*70)
    print(f"Total URLs: {len(df)}")
    print("\nSample URLs:")
    print(df.sample(20))
    print("\nDataset saved to: ml/data/raw/synthetic_phishing.csv")

if __name__ == "__main__":
    main()
