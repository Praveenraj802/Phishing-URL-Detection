# Quick Start Guide

## ✅ Backend is Running!

Your backend server is already running on **http://localhost:8000**

API Documentation: **http://localhost:8000/docs**

## Next Step: Start the Frontend

Open a **NEW PowerShell terminal** and run:

```powershell
cd "c:\Users\Sai Kumar\Desktop\SAI\phishing URL\frontend"
npm install
npm run dev
```

Then open **http://localhost:5173** in your browser!

## Testing the API

While the frontend installs, you can test the API directly:

**1. Health Check:**
```powershell
curl http://localhost:8000/api/v1/health
```

**2. Scan a URL:**
```powershell
curl -X POST "http://localhost:8000/api/v1/scan-url" `
  -H "Content-Type: application/json" `
  -d '{\"url\": \"http://paypal-security-alert.com/update\"}'
```

## System Status

✅ Backend: Running on port 8000  
✅ ML Model: Trained and loaded  
✅ API Endpoints: Ready  
⏳ Frontend: Needs npm install + npm run dev  

## Troubleshooting

If you need to restart the backend:
```powershell
cd backend
.\venv\Scripts\activate
python -m app.main
```

---

**Your phishing detection system is almost ready! Just start the frontend and you're good to go!**
