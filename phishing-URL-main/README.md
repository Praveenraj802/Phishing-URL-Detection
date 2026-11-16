# 🛡️ Adaptive and Explainable Real-Time Phishing URL Detection System

A production-grade, AI-powered phishing URL detection system with explainable predictions and modern UI.

## 🌟 Features

- **Real-Time Detection**: Scan URLs in <500ms
- **Hybrid AI Model**: Combines feature-based ML classifier with deep learning
- **Explainable AI**: Human-readable reasons for every prediction
- **Modern UI**: React + Vite + Tailwind CSS with glassmorphism design
- **RESTful API**: FastAPI backend with Swagger docs
- **Adaptive Learning**: Feedback collection for continuous improvement
- **34 URL Features**: Comprehensive feature engineering pipeline

## 🏗️ System Architecture

```
┌─────────────────────────────────────────┐
│      Modern UI (React + Tailwind)      │
├─────────────────────────────────────────┤
│        API Layer (FastAPI)              │
├─────────────────────────────────────────┤
│   Feature Engineering Pipeline          │
│   (34 URL features)                     │
├─────────────────────────────────────────┤
│   Hybrid AI Detection Engine            │
│   ├─ Random Forest/XGBoost              │
│   └─ LSTM (optional)                    │
├─────────────────────────────────────────┤
│   Explainability Engine                 │
│   (Human-readable reasons)              │
├─────────────────────────────────────────┤
│   Adaptive Learning Module              │
│   (Feedback & Retraining)               │
└─────────────────────────────────────────┘
```

## 📁 Project Structure

```
phishing-url-detector/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── api/               # API routes
│   │   ├── core/              # Configuration & logging
│   │   ├── features/          # Feature engineering
│   │   ├── models/            # ML models & inference
│   │   ├── explainability/    # Explanation engine
│   │   └── main.py            # FastAPI app
│   └── requirements.txt
├── frontend/                   # React + Vite frontend
│   ├── src/
│   │   ├── components/        # UI components
│   │   ├── services/          # API client
│   │   ├── App.jsx
│   │   └── main.jsx
│   └── package.json
├── ml/                         # ML training
│   ├── data/                  # Datasets
│   ├── prepare_dataset.py
│   └── train_classifier.py
├── models/                     # Saved models
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- pip and npm

### Backend Setup

1. **Install dependencies:**
   ```bash
   cd backend
   python -m venv venv
   venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   ```

2. **Prepare dataset and train model:**
   ```bash
   cd ..
   python -m ml.prepare_dataset
   python -m ml.train_classifier
   ```

3. **Run backend:**
   ```bash
   cd backend
   python -m app.main
   ```

   Backend will run on **http://localhost:8000**
   
   API docs: **http://localhost:8000/docs**

### Frontend Setup

1. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Run development server:**
   ```bash
   npm run dev
   ```

   Frontend will run on **http://localhost:5173**

## 🎯 Usage

### Web Interface

1. Open http://localhost:5173
2. Enter a URL to scan
3. Click "Scan URL"
4. View results with explanations

### API Usage

**Scan a URL:**
```bash
curl -X POST "http://localhost:8000/api/v1/scan-url" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

**Response:**
```json
{
  "url": "https://example.com",
  "prediction": "legitimate",
  "confidence": 0.9234,
  "risk_level": "low",
  "reasons": [
    "✓ Uses HTTPS (secure connection)",
    "✓ No suspicious keywords detected",
    "✓ Normal URL length"
  ],
  "scan_time_ms": 45.23,
  "features_extracted": 34
}
```

## 🧠 Feature Engineering

The system extracts **34 features** from each URL:

### URL Structure (4 features)
- URL length, domain length, path length, query length

### Character Counts (10 features)  
- Dots, hyphens, underscores, slashes, special characters

### Security Indicators (4 features)
- HTTPS presence, port number, IP address detection

### Lexical Features (5 features)
- Suspicious keywords, digit ratio, special char ratio, entropy

### Domain Features (5 features)
- Subdomains, domain characteristics

### Heuristics (6 features)
- URL shortener, excessive patterns, anomalies

## 🤖 Machine Learning Models

### Primary Model: Random Forest / XGBoost
- **Input**: 34 engineered features
- **Training**: 100 estimators, balanced classes
- **Performance**: >95% accuracy target
- **Inference**: <100ms

### Optional: LSTM Model
- **Input**: Character-level URL sequences
- **Architecture**: 2-layer LSTM
- **Advantage**: Learns patterns automatically

### Hybrid Fusion
- Combines strengths of both models
- Weighted ensemble (60% ML, 40% LSTM)

## 💡 Explainability

Every prediction comes with human-readable explanations:

**Phishing Example:**
- ✗ URL contains IP address instead of domain name
- ✗ Contains suspicious keyword 'verify'
- ✗ Uses HTTP instead of HTTPS
- ✗ Domain name contains digits

**Legitimate Example:**
- ✓ Uses HTTPS (secure connection)
- ✓ No suspicious keywords detected  
- ✓ Normal URL length

## 📊 Model Performance

| Metric | Target | Achieved* |
|--------|--------|-----------|
| Accuracy | >95% | ~90%+ |
| Precision | >93% | ~85%+ |
| Recall | >90% | ~85%+ |
| F1-Score | >92% | ~85%+ |
| Latency | <500ms | <100ms |

*On sample dataset. Performance improves with larger datasets.

## 🔄 Adaptive Learning

The system supports continuous improvement:

1. **Feedback Collection**: Users can report misclassifications
2. **Data Storage**: New URLs logged for retraining
3. **Periodic Retraining**: Batch retraining with new data
4. **Model Versioning**: Safe deployment with rollback support

## 🧪 Testing

### Test Backend
```bash
cd backend
pytest tests/
```

### Test Feature Extraction
```python
from app.features.feature_extractor import extract_features

features = extract_features("https://example.com")
print(features)
```

### Test API
```bash
# Health check
curl http://localhost:8000/api/v1/health

# Scan URL
curl -X POST http://localhost:8000/api/v1/scan-url \
  -H "Content-Type: application/json" \
  -d '{"url": "http://phishing-site.com"}'
```

## 🎓 For Viva / Presentation

### Key Talking Points

1. **Problem Statement**
   - Static blacklists are ineffective
   - Zero-day phishing detection
   - Need for explainability

2. **Solution**
   - Hybrid AI approach
   - 34 engineered features
   - Real-time detection (<500ms)
   - Human-readable explanations

3. **Technical Highlights**
   - Modern tech stack (React, FastAPI, scikit-learn)
   - Modular architecture
   - RESTful API with Swagger docs
   - Responsive UI with Tailwind CSS

4. **Challenges Solved**
   - Class imbalance → Class weights, SMOTE
   - Latency → Lightweight models, efficient features
   - Explainability → Rule-based mapping

5. **Results**
   - High accuracy (>90%)
   - Fast inference (<100ms)
   - Clear explanations
   - Production-ready deployment

## 🚢 Deployment

### Local Development
- Backend: `python -m app.main`
- Frontend: `npm run dev`

### Production Deployment

**Frontend (Vercel/Netlify):**
```bash
cd frontend
npm run build
# Deploy dist/ folder
```

**Backend (Render/Railway):**
```bash
cd backend
# Use Dockerfile or direct deployment
```

## 📝 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/scan-url` | POST | Scan a URL |
| `/api/v1/health` | GET | Health check |
| `/api/v1/feedback` | POST | Submit feedback |
| `/docs` | GET | Swagger API docs |

## 🛠️ Tech Stack

**Frontend:**
- React 18
- Vite
- Tailwind CSS
- Axios

**Backend:**
- FastAPI
- Pydantic
- Uvicorn
- Loguru

**Machine Learning:**
- scikit-learn
- XGBoost
- PyTorch (optional)
- NumPy, Pandas

## 🔐 Security Features

- Input validation & sanitization
- CORS configuration
-request/response logging
- Error handling with meaningful messages
- No sensitive data exposure

## 📈 Future Enhancements

- [ ] Browser extension integration
- [ ] Real-time model updates
- [ ] Multi-language support
- [ ] Advanced LSTM/Transformer models
- [ ] Database integration for analytics
- [ ] A/B testing for models
- [ ] Rate limiting & authentication

## 📄 License

This project is created as a final year major project for academic purposes.

## 👥 Contributors

*Your Name* - Final Year Project

## 🙏 Acknowledgments

- PhishTank for phishing URL datasets
- scikit-learn for ML framework
- FastAPI for modern Python API
- React community for frontend tools

---

**Built with ❤️ for cybersecurity education**
