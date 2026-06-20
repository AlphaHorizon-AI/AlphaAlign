@echo off
echo ========================================================
echo AlphaAlign Installer (Windows)
echo ========================================================

echo.
echo [1/3] Checking prerequisites...
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH. Please install Python 3.10 or higher.
    exit /b 1
)
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Node.js is not installed or not in PATH. Please install Node.js v18 or higher.
    exit /b 1
)

echo.
echo [2/3] Setting up Backend (Python)...
cd backend
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
)
echo Installing Python dependencies...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
cd ..

echo.
echo [3/3] Setting up Frontend (Node.js)...
cd frontend
echo Installing Node.js dependencies...
call npm install
cd ..

echo.
echo ========================================================
echo Installation Complete!
echo.
echo To start AlphaAlign, just double-click start.bat
echo ========================================================
pause
