@echo off
title AlphaAlign - Strategic AI Choice Engine

REM Always run from the directory where this script lives
pushd "%~dp0"

echo.
echo  ============================================
echo    AlphaAlign - Strategic AI Choice Engine
echo  ============================================
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python 3.10+ from https://python.org
    pause
    exit /b 1
)

REM Check Node
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js is not installed or not in PATH.
    echo Please install Node.js v18+ from https://nodejs.org
    pause
    exit /b 1
)

REM Create virtual environment if needed
if not exist "backend\venv\Scripts\python.exe" (
    echo [1/5] Creating Python virtual environment...
    python -m venv backend\venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
)

REM Install backend dependencies
echo [2/5] Installing backend dependencies...
"%~dp0backend\venv\Scripts\pip.exe" install -r "%~dp0backend\requirements.txt" -q
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install Python dependencies.
    echo Try deleting backend\venv and running again.
    pause
    exit /b 1
)

REM Install frontend dependencies if needed
if not exist "frontend\node_modules" (
    echo [3/5] Installing frontend dependencies...
    pushd "%~dp0frontend"
    call npm install
    popd
) else (
    echo [3/5] Frontend dependencies already installed.
)

REM Copy logo to public if not there
if not exist "frontend\public\logo.png" (
    echo [4/5] Copying logo...
    if exist "Build Assets\AlphaAlign - Logo.png" (
        copy "Build Assets\AlphaAlign - Logo.png" "frontend\public\logo.png" >nul
    )
) else (
    echo [4/5] Logo already in place.
)

REM Start servers
echo [5/5] Starting AlphaAlign...
echo.
echo  Backend:  http://localhost:8001
echo  Frontend: http://localhost:5173
echo  API Docs: http://localhost:8001/docs
echo.
echo  Press Ctrl+C in this window to stop the backend.
echo  Close the other window to stop the frontend.
echo.

REM Start frontend in a separate window
start "AlphaAlign Frontend" cmd /k "cd /d "%~dp0frontend" && npm run dev"

REM Wait for frontend to start
timeout /t 3 /nobreak >nul

REM Open the browser
start "" http://localhost:5173

REM Start backend in this window
"%~dp0backend\venv\Scripts\python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port 8001 --app-dir "%~dp0backend"

REM If we get here, backend exited
echo.
echo  Backend has stopped.
pause
