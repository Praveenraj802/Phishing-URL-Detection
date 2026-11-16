# Quick Start Script - Run Backend and Frontend Together

Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "  Starting Phishing URL Detector...        " -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

# Start backend in background
Write-Host "[1/2] Starting backend server..." -ForegroundColor Yellow
$backendJob = Start-Job -ScriptBlock {
    Set-Location "$using:PSScriptRoot\backend"
    .\venv\Scripts\Activate.ps1
    python -m app.main
}

Start-Sleep -Seconds 3

# Start frontend
Write-Host "[2/2] Starting frontend server..." -ForegroundColor Yellow
Set-Location frontend
npm run dev

# Cleanup on exit
Stop-Job $backendJob
Remove-Job $backendJob
