# ──────────────────────────────────────────────────────────
# Citizen Services Assistant - Startup Script
# ──────────────────────────────────────────────────────────

Write-Host "Starting Citizen Services Assistant..." -ForegroundColor Cyan

# 1. Check if virtual environment exists
if (-Not (Test-Path ".\venv")) {
    Write-Host "Error: Virtual environment not found. Please run 'python -m venv venv' and install dependencies first." -ForegroundColor Red
    exit
}

# 2. Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Green
& .\venv\Scripts\Activate.ps1

# 3. Start the backend API in a background job
Write-Host "Starting LLM Backend API on port 5000..." -ForegroundColor Green
Start-Job -Name "CSABackend" -ScriptBlock {
    Set-Location $using:PWD
    & .\venv\Scripts\python.exe -m app.main
} | Out-Null

# Give the backend a few seconds to start up
Start-Sleep -Seconds 3

# 4. Start the Streamlit frontend
Write-Host "Starting Streamlit Frontend on port 8501..." -ForegroundColor Green
Write-Host "The app will open in your default browser shortly." -ForegroundColor Yellow
Write-Host "(Press Ctrl+C to stop both servers when you are done)" -ForegroundColor Magenta
Write-Host "──────────────────────────────────────────────────────────" -ForegroundColor Cyan

try {
    # Run Streamlit in the foreground so Ctrl+C stops it
    & .\venv\Scripts\streamlit.exe run ui\streamlit_app.py
}
finally {
    # Ensure backend is stopped when Streamlit exits or is interrupted
    Write-Host "Stopping backend services..." -ForegroundColor Yellow
    Get-Job -Name "CSABackend" | Stop-Job
    Get-Job -Name "CSABackend" | Remove-Job
    Write-Host "Goodbye!" -ForegroundColor Cyan
}
