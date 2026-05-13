@echo off
REM Stock Trading Dashboard - Quick Start Script
REM This script starts both backend and frontend servers

echo ======================================
echo  Stock Trading Dashboard - Quick Start
echo ======================================
echo.

REM Get the current directory
set ROOT_DIR=%~dp0

echo [1/4] Checking Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js not found! Please install Node.js first.
    pause
    exit /b 1
)
echo ✓ Node.js found

echo.
echo [2/4] Checking Python virtual environment...
if not exist "%ROOT_DIR%backend\venv" (
    echo ERROR: Python venv not found! Please run: python -m venv venv
    pause
    exit /b 1
)
echo ✓ Python venv found

echo.
echo [3/4] Installing frontend dependencies (if needed)...
cd "%ROOT_DIR%frontend"
if not exist "node_modules" (
    echo Installing npm packages...
    call npm install
) else (
    echo ✓ Dependencies already installed
)

echo.
echo [4/4] Starting servers...
echo.
echo ======================================
echo Backend will start on: http://localhost:8000
echo Frontend will start on: http://localhost:5173
echo ======================================
echo.

REM Start backend in new window
cd "%ROOT_DIR%backend"
start "Backend - Trading API" cmd /k "call venv\Scripts\activate && uvicorn app:app --reload --port 8000"

timeout /t 3 /nobreak

REM Start frontend in new window
cd "%ROOT_DIR%frontend"
start "Frontend - Trading Dashboard" cmd /k "npm run dev"

echo.
echo ✓ Both servers started in separate windows
echo ✓ Frontend will open at http://localhost:5173
echo ✓ Backend API at http://localhost:8000
echo.
echo Waiting for services to be ready...
timeout /t 5

REM Open browser
start http://localhost:5173

echo ✓ Dashboard opened in default browser
echo.
echo To stop the servers:
echo   - Close the command windows or press Ctrl+C
echo.
pause
