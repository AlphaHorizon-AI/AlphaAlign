@echo off
echo ========================================================
echo Starting AlphaAlign
echo ========================================================

:: Start Backend
echo Starting Backend Server (port 8000)...
start "AlphaAlign Backend" cmd /k "cd backend & call venv\Scripts\activate.bat & uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"

:: Wait 3 seconds
timeout /t 3 /nobreak >nul

:: Start Frontend
echo Starting Frontend Development Server (port 5173)...
start "AlphaAlign Frontend" cmd /k "cd frontend & npm run dev"

echo.
echo Both servers have been started in new windows.
echo Please go to http://localhost:5173 in your browser.
