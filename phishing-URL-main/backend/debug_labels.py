import pandas as pd

def debug_labels():
    url = "https://raw.githubusercontent.com/shreyagopal/Phishing-Website-Detection-by-Machine-Learning-Techniques/master/DataFiles/5.urldata.csv"
    print("Loading df...")
    df = pd.read_csv(url)
    
    print("\nLabel distribution:")
    print(df['Label'].value_counts())
    
    print("\nSample Legit URLs (Label 0):")
    for d in df[df['Label'] == 0]['Domain'].head(5):
        print(d)
        
    print("\nSample Phishing URLs (Label 1):")
    for d in df[df['Label'] == 1]['Domain'].head(5):
        print(d)

if __name__ == "__main__":
    debug_labels()
