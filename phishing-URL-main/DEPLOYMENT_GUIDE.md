# Phishing URL Detection: Deployment Guide

This guide explains exactly how to deploy and run this project from absolute scratch on a brand new laptop.

## 1. Prerequisites 
Before starting, ensure the new laptop has the following installed:
- **Python 3.10+** (Check "Add Python to PATH" during installation)
- **Node.js 18+** (Includes npm for the frontend)
- **Git** (For downloading the repository)

## 2. Clone the Repository
Open a terminal (PowerShell or Command Prompt) and run:
```bash
git clone https://github.com/Luckysai07/phishing-URL.git
cd phishing-URL
```

*(Note: Depending on how the `.gitignore` was handled when pushing the dataset and models, you may need to manually copy the `backend/models/*.joblib` and `.h5` files over via a USB drive if they were excluded from Git due to their massive file sizes).*

## 3. Setup the Backend API (Python)
Open a new terminal in the `phishing-URL/backend` directory:

1. Create a fresh virtual environment:
```bash
python -m venv venv
```

2. Activate the virtual environment:
**Windows:**
```bash
.\venv\Scripts\activate
```
**Mac/Linux:**
```bash
source venv/bin/activate
```

3. Install the dependencies:
```bash
pip install -r requirements.txt
pip install tensorflow  # Required for the Deep NLP LSTM engine
```

4. Start the backend server:
```bash
python -m app.main
```
If successful, you will see `Uvicorn running on http://0.0.0.0:8000`. Leave this terminal open!

## 4. Setup the Frontend UI (React)
Open a **second, separate terminal** in the `phishing-URL/frontend` directory:

1. Install Node.js dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

## 5. View the Project!
1. Open up a web browser (Chrome, Edge, Safari).
2. Go to: **http://localhost:5173**
3. You should see the sleek UI! Paste a URL into the scanner to test your Hybrid AI system in real-time.
