import os

kaggle_code = """
# ==========================================
# PHISHING DETECTOR - DEEP LSTM NLP TRAINING 
# ==========================================

# --- STEP 1: INSTALL PACKAGES ---
import subprocess, sys
print("Installing requirements...")
subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "tensorflow", "pandas", "scikit-learn"])
print("Packages installed!")

# --- STEP 2: IMPORTS ---
import os
import pandas as pd
import numpy as np
import pickle
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, LSTM, Dense, Dropout
from sklearn.model_selection import train_test_split
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint

# --- STEP 3: LOAD DATASET ---
def load_kaggle_dataset():
    print("Looking for datasets in /kaggle/input...")
    dataset_path = None
    for root, dirs, files in os.walk('/kaggle/input'):
        for file in files:
            if file.endswith('.csv'):
                dataset_path = os.path.join(root, file)
                print(f"Found dataset: {dataset_path}")
                break
        if dataset_path:
            break
            
    if not dataset_path:
        print("CRITICAL ERROR: DATASET NOT FOUND! Add 'web-page-phishing-detection-dataset'")
        raise FileNotFoundError("Dataset missing.")
        
    df = pd.read_csv(dataset_path)
    print(f"Loaded dataset with {len(df)} rows.")
    
    url_col, label_col = None, None
    for col in df.columns:
        if 'url' in col.lower() or 'link' in col.lower(): url_col = col
        if 'label' in col.lower() or 'class' in col.lower() or 'target' in col.lower() or 'status' in col.lower(): label_col = col
        
    if not url_col or not label_col:
        print(f"ERROR: Could not find URL or Label column in: {df.columns.tolist()}")
        raise ValueError("Missing required columns in dataset.")
        
    df_clean = pd.DataFrame({'url': df[url_col].astype(str), 'label': df[label_col]})
    df_clean['label'] = df_clean['label'].apply(lambda x: 1 if str(x).lower() in ['1', 'phishing', 'bad'] else 0)
    
    # Balanced dataset
    phishing = df_clean[df_clean['label'] == 1]
    legit = df_clean[df_clean['label'] == 0]
    n_samples = min(len(phishing), len(legit), 20000)
    
    balanced = pd.concat([phishing.sample(n=n_samples, random_state=42), legit.sample(n=n_samples, random_state=42)])
    return balanced.sample(frac=1, random_state=42).reset_index(drop=True)

df = load_kaggle_dataset()
urls = df['url'].values
labels = df['label'].values

# --- STEP 4: NLP TOKENIZATION (CHARACTER LEVEL) ---
print("Tokenizing URLs (Character level NLP)...")
# We analyze URLs by their characters to catch linguistic tricks!
tokenizer = Tokenizer(char_level=True, lower=True)
tokenizer.fit_on_texts(urls)

# Save tokenizer for the backend API
with open('lstm_tokenizer.pickle', 'wb') as handle:
    pickle.dump(tokenizer, handle, protocol=pickle.HIGHEST_PROTOCOL)

sequences = tokenizer.texts_to_sequences(urls)
max_len = 150 # Cap URL length at 150 chars for LSTM memory
X = pad_sequences(sequences, maxlen=max_len)
y = np.array(labels)

vocab_size = len(tokenizer.word_index) + 1
print(f"Vocabulary size (unique characters): {vocab_size}")
print(f"Shape of Data Tensor: {X.shape}")

# --- STEP 5: DEEP NEURAL NETWORK ARCHITECTURE ---
print("Building Deep LSTM Neural Network...")
model = Sequential([
    Embedding(input_dim=vocab_size, output_dim=32, input_length=max_len),
    LSTM(64, return_sequences=True),
    Dropout(0.2),
    LSTM(32),
    Dropout(0.2),
    Dense(16, activation='relu'),
    Dense(1, activation='sigmoid') # 0 to 1 confidence prediction
])

model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
model.summary()

# --- STEP 6: TRAINING ---
print("Training the Deep Brain (Takes a few minutes)...")
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

early_stop = EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True)

history = model.fit(
    X_train, y_train,
    epochs=15, 
    batch_size=128,
    validation_data=(X_test, y_test),
    callbacks=[early_stop]
)

# Evaluate
loss, acc = model.evaluate(X_test, y_test)
print(f"\\nFINAL LSTM NLP ACCURACY: {acc * 100:.2f}%")

# Save the brain!
model.save('lstm_model.h5')

print("\\n=======================================================")
print("SUCCESS! Deep Learning Engine Trained!")
print("Please download BOTH files:")
print("1. lstm_model.h5")
print("2. lstm_tokenizer.pickle")
print("Drop both into your backend/models/ folder!")
print("=======================================================\\n")
"""

with open("lstm_cell_kaggle.txt", "w", encoding="utf-8") as f:
    f.write(kaggle_code.strip())

print("Successfully created lstm_cell_kaggle.txt")
