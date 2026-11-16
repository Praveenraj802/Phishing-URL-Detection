import json
from pathlib import Path

def create_notebook():
    try:
        # Read the exact feature extractor from the project
        with open('backend/app/features/feature_extractor.py', 'r', encoding='utf-8') as f:
            extractor_code = f.read()
    except Exception as e:
        print(f"Error reading feature_extractor.py: {e}")
        return

    # Filter out local imports and __main__ block
    clean_lines = []
    for line in extractor_code.split('\n'):
        if 'from app.core.logging' in line or 'from loguru' in line:
            continue
        if 'if __name__ == "__main__":' in line:
            break
        clean_lines.append(line + '\n')
    extractor_code_clean = "".join(clean_lines)

    # Notebook structure
    notebook = {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "# 🛡️ Phishing URL Detection - Kaggle Training Pipeline\n",
                    "**Instructions:**\n",
                    "1. Click **Add Data** on the right side panel in Kaggle.\n",
                    "2. Search for and add: `web-page-phishing-detection-dataset`.\n",
                    "3. Click **Run All** to train the XGBoost model and generate `feature_classifier.joblib`."
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "!pip install tldextract validators loguru xgboost scikit-learn dnspython\n"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "import os\n",
                    "import pandas as pd\n",
                    "import numpy as np\n",
                    "import joblib\n",
                    "from tqdm.notebook import tqdm\n",
                    "from sklearn.ensemble import RandomForestClassifier\n",
                    "from sklearn.model_selection import train_test_split\n",
                    "from sklearn.metrics import classification_report, accuracy_score\n",
                    "import xgboost as xgb\n",
                    "import logging\n\n",
                    "# Fallback logger since we removed loguru\n",
                    "logger = logging.getLogger('kaggle')\n",
                    "logger.setLevel(logging.INFO)\n"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# --- FEATURE EXTRACTOR LOGIC --- \n\n" + extractor_code_clean
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "def load_kaggle_dataset():\n",
                    "    print('Looking for datasets in /kaggle/input...')\n",
                    "    dataset_path = None\n",
                    "    for root, dirs, files in os.walk('/kaggle/input'):\n",
                    "        for file in files:\n",
                    "            if file.endswith('.csv'):\n",
                    "                dataset_path = os.path.join(root, file)\n",
                    "                print(f'Found dataset: {dataset_path}')\n",
                    "                break\n",
                    "        if dataset_path:\n",
                    "            break\n",
                    "    \n",
                    "    if not dataset_path:\n",
                    "        raise FileNotFoundError('Please add the dataset (web-page-phishing-detection-dataset) to this notebook!')\n",
                    "    \n",
                    "    df = pd.read_csv(dataset_path)\n",
                    "    print(f'Loaded dataset with {len(df)} rows.')\n",
                    "    \n",
                    "    # Clean data (ensure 'url' and 'label' columns exist)\n",
                    "    url_col, label_col = None, None\n",
                    "    for col in df.columns:\n",
                    "        if 'url' in col.lower() or 'link' in col.lower(): url_col = col\n",
                    "        if 'label' in col.lower() or 'class' in col.lower() or 'target' in col.lower() or 'type' in col.lower(): label_col = col\n",
                    "    \n",
                    "    # Standardize\n",
                    "    df_clean = pd.DataFrame({'url': df[url_col], 'label': df[label_col]})\n",
                    "    \n",
                    "    # Convert string labels ('phishing', 'benign') to ints\n",
                    "    df_clean['label'] = df_clean['label'].apply(lambda x: 1 if str(x).lower() in ['1', 'phishing', 'bad', 'malicious'] else 0)\n",
                    "    \n",
                    "    # Balance dataset to save time\n",
                    "    phishing = df_clean[df_clean['label'] == 1]\n",
                    "    legit = df_clean[df_clean['label'] == 0]\n",
                    "    n_samples = min(len(phishing), len(legit), 15000)\n",
                    "    \n",
                    "    balanced = pd.concat([phishing.sample(n=n_samples, random_state=42), legit.sample(n=n_samples, random_state=42)])\n",
                    "    return balanced.sample(frac=1, random_state=42).reset_index(drop=True)\n",
                    "\n",
                    "df = load_kaggle_dataset()\n",
                    "print(df['label'].value_counts())\n"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "print('Extracting features (This will take a few minutes)...')\n",
                    "extractor = URLFeatureExtractor()\n",
                    "X_list, y_list = [], []\n",
                    "\n",
                    "for idx, row in tqdm(df.iterrows(), total=len(df)):\n",
                    "    try:\n",
                    "        features = extractor.extract_feature_vector(row['url'])\n",
                    "        X_list.append(features)\n",
                    "        y_list.append(row['label'])\n",
                    "    except Exception:\n",
                    "        pass\n",
                    "\n",
                    "X = np.array(X_list)\n",
                    "y = np.array(y_list)\n",
                    "print(f'Successfully built dataset matrix: {X.shape}')\n"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "print('Training Models...')\n",
                    "X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)\n",
                    "\n",
                    "# Random Forest\n",
                    "rf = RandomForestClassifier(n_estimators=100, max_depth=15, random_state=42, n_jobs=-1)\n",
                    "rf.fit(X_train, y_train)\n",
                    "rf_preds = rf.predict(X_test)\n",
                    "print('--- Random Forest Accuracy ---')\n",
                    "print(accuracy_score(y_test, rf_preds))\n",
                    "\n",
                    "# XGBoost\n",
                    "xgb_model = xgb.XGBClassifier(n_estimators=150, max_depth=8, learning_rate=0.1, random_state=42, n_jobs=-1)\n",
                    "xgb_model.fit(X_train, y_train)\n",
                    "xgb_preds = xgb_model.predict(X_test)\n",
                    "print('--- XGBoost Accuracy ---')\n",
                    "print(accuracy_score(y_test, xgb_preds))\n",
                    "\n",
                    "# Save the best one\n",
                    "best_model = xgb_model if accuracy_score(y_test, xgb_preds) > accuracy_score(y_test, rf_preds) else rf\n",
                    "joblib.dump(best_model, 'feature_classifier.joblib')\n",
                    "print('Model saved as feature_classifier.joblib! You can now download it from the output panel.')\n"
                ]
            }
        ],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 4
    }

    with open('phishing_model_training_kaggle.ipynb', 'w', encoding='utf-8') as f:
        json.dump(notebook, f, indent=1)
    
    print("Notebook 'phishing_model_training_kaggle.ipynb' created successfully!")

if __name__ == "__main__":
    create_notebook()
