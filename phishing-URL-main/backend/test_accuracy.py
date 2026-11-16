import pandas as pd
import requests
import json
import time

print("Downloading dataset...")
url = "https://raw.githubusercontent.com/shreyagopal/Phishing-Website-Detection-by-Machine-Learning-Techniques/master/DataFiles/5.urldata.csv"
try:
    df = pd.read_csv(url)
    print("Columns:", df.columns.tolist())
    print("Shape:", df.shape)
except Exception as e:
    print("Failed to download or read:", e)

# Trying another just in case
url2 = "https://raw.githubusercontent.com/surajkmrtiwari/Phishing-URL-Detection/master/phishing_site_urls.csv"
try:
    df2 = pd.read_csv(url2)
    print("\nDataset 2 Columns:", df2.columns.tolist())
    print("Dataset 2 Shape:", df2.shape)
    print(df2.head())
except Exception as e:
    print("Failed to download dataset 2:", e)
