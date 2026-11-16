import os
import time
import pandas as pd
import numpy as np
import joblib
import json
from pathlib import Path
from sklearn.model_selection import train_test_split
from app.core.config import settings

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Suppress TF warnings
import tensorflow as tf
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, LSTM, Dense, Dropout

def train_lstm_model():
    print("Loading 10k dataset from URL...")
    url = "https://raw.githubusercontent.com/shreyagopal/Phishing-Website-Detection-by-Machine-Learning-Techniques/master/DataFiles/5.urldata.csv"
    try:
        df = pd.read_csv(url)
    except Exception as e:
        print(f"Failed to load dataset: {e}")
        return

    # We use 'Domain' column, but actually we should use the raw URLs if available.
    # For this dataset, 'Domain' acts as the URL string.
    urls = df['Domain'].tolist()
    labels = df['Label'].tolist()  # 1 for Phishing, 0 for Legitimate
    
    # Prepend http:// to domains to make them realistic URLs
    urls = [u if u.startswith("http") else "http://" + u for u in urls]
    
    print(f"Loaded {len(urls)} URLs. Preprocessing for LSTM...")
    
    # Text tokenization (Character-level)
    max_url_length = 200  # truncate/pad URLs to 200 chars
    tokenizer = Tokenizer(char_level=True, lower=True, oov_token='<OOV>')
    tokenizer.fit_on_texts(urls)
    
    # Sequence mapping and padding
    sequences = tokenizer.texts_to_sequences(urls)
    X = pad_sequences(sequences, maxlen=max_url_length, padding='post', truncating='post')
    y = np.array(labels)
    
    # Split
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    vocab_size = len(tokenizer.word_index) + 1
    
    print(f"Vocab size (unique chars): {vocab_size}")
    print(f"Training shape: {X_train.shape}, Validation shape: {X_val.shape}")
    
    # Build LSTM Model
    model = Sequential([
        Embedding(input_dim=vocab_size, output_dim=32, input_length=max_url_length),
        LSTM(64, return_sequences=False),
        Dropout(0.5),
        Dense(32, activation='relu'),
        Dropout(0.5),
        Dense(1, activation='sigmoid')
    ])
    
    model.compile(optimizer='adam', 
                  loss='binary_crossentropy', 
                  metrics=['accuracy'])
    
    model.summary()
    
    print("Training Character-Level LSTM...")
    early_stop = tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True)
    
    history = model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=15,
        batch_size=128,
        callbacks=[early_stop]
    )
    
    # Evaluate
    val_loss, val_acc = model.evaluate(X_val, y_val)
    print(f"Final LSTM Validation Accuracy: {val_acc:.4f}")
    
    # Save Model and Tokenizer
    model_dir = Path(settings.model_path)
    model_dir.mkdir(parents=True, exist_ok=True)
    
    # Save TF model (.h5 format or saved_model)
    model_path = model_dir / "lstm_classifier.h5"
    model.save(model_path)
    
    # Save Tokenizer Config
    tokenizer_json = tokenizer.to_json()
    with open(model_dir / "lstm_tokenizer.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(tokenizer_json, ensure_ascii=False))
        
    print(f"Successfully saved LSTM model to {model_path} and tokenizer to lstm_tokenizer.json")

if __name__ == "__main__":
    train_lstm_model()
