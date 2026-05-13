# Stock Trading Dashboard - Quick Start (PowerShell)
# Run this to start both backend and frontend servers

Write-Host "======================================" -ForegroundColor Cyan
Write-Host " Stock Trading Dashboard - Quick Start" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

$RootDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Check Node.js
Write-Host "[1/4] Checking Node.js..." -ForegroundColor Yellow
$nodeCheck = node --version 2>$null
if (-not $nodeCheck) {
    Write-Host "ERROR: Node.js not found! Please install Node.js first." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "✓ Node.js found: $nodeCheck" -ForegroundColor Green

# Check Python venv
Write-Host "[2/4] Checking Python virtual environment..." -ForegroundColor Yellow
$venvPath = Join-Path $RootDir "backend\venv"
if (-not (Test-Path $venvPath)) {
    Write-Host "ERROR: Python venv not found at $venvPath" -ForegroundColor Red
    Write-Host "Run: python -m venv backend\venv" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "✓ Python venv found" -ForegroundColor Green

# Check frontend dependencies
Write-Host "[3/4] Checking frontend dependencies..." -ForegroundColor Yellow
$frontendDir = Join-Path $RootDir "frontend"
$nodeModulesPath = Join-Path $frontendDir "node_modules"
if (-not (Test-Path $nodeModulesPath)) {
    Write-Host "Installing npm packages..." -ForegroundColor Yellow
    Push-Location $frontendDir
    npm install
    Pop-Location
} else {
    Write-Host "✓ Dependencies already installed" -ForegroundColor Green
}

Write-Host ""
Write-Host "[4/4] Starting servers..." -ForegroundColor Yellow
Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "Backend will start on: http://localhost:8000" -ForegroundColor Green
Write-Host "Frontend will start on: http://localhost:5173" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Start backend
$backendDir = Join-Path $RootDir "backend"
$backendCmd = "cd $backendDir && .\venv\Scripts\Activate.ps1; uvicorn app:app --reload --port 8000"
Start-Process powershell -ArgumentList "-NoExit -Command `"$backendCmd`"" -WindowStyle Normal

Start-Sleep -Seconds 3

# Start frontend
$frontendCmd = "cd $frontendDir && npm run dev"
Start-Process powershell -ArgumentList "-NoExit -Command `"$frontendCmd`"" -WindowStyle Normal

Write-Host "✓ Both servers started in separate windows" -ForegroundColor Green
Write-Host "✓ Frontend will open at http://localhost:5173" -ForegroundColor Green
Write-Host "✓ Backend API at http://localhost:8000" -ForegroundColor Green
Write-Host ""
Write-Host "Opening dashboard in browser..." -ForegroundColor Yellow

Start-Sleep -Seconds 5
Start-Process "http://localhost:5173"

Write-Host "✓ Dashboard opened in default browser" -ForegroundColor Green
Write-Host ""
Write-Host "To stop the servers:" -ForegroundColor Yellow
Write-Host "  - Close the command windows or press Ctrl+C" -ForegroundColor White
Write-Host ""
Read-Host "Press Enter to exit this window"
