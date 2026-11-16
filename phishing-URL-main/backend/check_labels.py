import pandas as pd
url = "https://raw.githubusercontent.com/shreyagopal/Phishing-Website-Detection-by-Machine-Learning-Techniques/master/DataFiles/5.urldata.csv"
df = pd.read_csv(url)
print("Unique Labels:", df['Label'].unique())
print("First few labels:\n", df[['Domain', 'Label']].head())
