# Setup Script for Phishing URL Detector
# Run this script to set up the entire project

Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "  Phishing URL Detector - Setup Script     " -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

# 1. Backend Setup
Write-Host "[1/5] Setting up Python backend..." -ForegroundColor Yellow
Set-Location backend

# Create virtual environment
if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Gray
    python -m venv venv
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Gray
.\venv\Scripts\Activate.ps1

# Install requirements
Write-Host "Installing Python dependencies..." -ForegroundColor Gray
pip install -r requirements.txt

# Copy environment file
if (-not (Test-Path ".env")) {
    Write-Host "Creating .env file..." -ForegroundColor Gray
    Copy-Item ".env.example" ".env" -ErrorAction SilentlyContinue
}

Set-Location ..

Write-Host "✓ Backend setup complete!" -ForegroundColor Green
Write-Host ""

# 2. Frontend Setup
Write-Host "[2/5] Setting up React frontend..." -ForegroundColor Yellow
Set-Location frontend

# Install npm packages
Write-Host "Installing npm dependencies..." -ForegroundColor Gray
npm install

# Copy environment file
if (-not (Test-Path ".env")) {
    Write-Host "Creating .env file..." -ForegroundColor Gray
    Copy-Item ".env.example" ".env" -ErrorAction SilentlyContinue
}

Set-Location ..

Write-Host "✓ Frontend setup complete!" -ForegroundColor Green
Write-Host ""

# 3. Prepare Dataset
Write-Host "[3/5] Preparing dataset..." -ForegroundColor Yellow
cd backend
.\venv\Scripts\Activate.ps1
cd ..
python -m ml.prepare_dataset

Write-Host "✓ Dataset prepared!" -ForegroundColor Green
Write-Host ""

# 4. Train Model
Write-Host "[4/5] Training ML model (this may take a minute)..." -ForegroundColor Yellow
python -m ml.train_classifier

Write-Host "✓ Model trained!" -ForegroundColor Green
Write-Host ""

# 5. Done
Write-Host "[5/5] Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "  Next Steps:                               " -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Start the backend:" -ForegroundColor White
Write-Host "   cd backend" -ForegroundColor Gray
Write-Host "   .\venv\Scripts\Activate.ps1" -ForegroundColor Gray
Write-Host "   python -m app.main" -ForegroundColor Gray
Write-Host ""
Write-Host "2. In a new terminal, start the frontend:" -ForegroundColor White
Write-Host "   cd frontend" -ForegroundColor Gray
Write-Host "   npm run dev" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Open http://localhost:5173 in your browser" -ForegroundColor White
Write-Host ""
Write-Host "API Documentation: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
