@echo off
setlocal EnableDelayedExpansion
chcp 65001 >nul

echo ========================================================
echo AlphaAlign Installer (Windows)
echo ========================================================
echo.

set "INSTALL_DIR=%USERPROFILE%\AlphaAlign"
set "REPO_URL=https://github.com/AlphaHorizon-AI/AlphaAlign/archive/refs/heads/main.zip"
set "TEMP_ZIP=%TEMP%\AlphaAlign_main.zip"
set "TEMP_EXTRACT=%TEMP%\AlphaAlign_extract"

echo [1/4] Checking prerequisites...
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH. Please install Python 3.10 or higher.
    pause
    exit /b 1
)
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Node.js is not installed or not in PATH. Please install Node.js v18 or higher.
    pause
    exit /b 1
)

echo.
echo [2/4] Downloading AlphaAlign...
powershell -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%REPO_URL%' -OutFile '%TEMP_ZIP%'"
if not exist "%TEMP_ZIP%" (
    echo [ERROR] Failed to download AlphaAlign.
    pause
    exit /b 1
)

echo Extracting AlphaAlign...
if exist "%TEMP_EXTRACT%" rmdir /s /q "%TEMP_EXTRACT%"
powershell -Command "Expand-Archive -Path '%TEMP_ZIP%' -DestinationPath '%TEMP_EXTRACT%' -Force"

echo Installing to %INSTALL_DIR%...
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"
:: Copy files from extracted folder to install dir, excluding data and venv to preserve them on upgrades
robocopy "%TEMP_EXTRACT%\AlphaAlign-main" "%INSTALL_DIR%" /E /XD data backend\venv frontend\node_modules >nul
if %errorlevel% geq 8 (
    echo [ERROR] Failed to copy files.
    pause
    exit /b 1
)

:: Cleanup
del "%TEMP_ZIP%"
rmdir /s /q "%TEMP_EXTRACT%"

cd /d "%INSTALL_DIR%"

echo.
echo [3/4] Setting up Backend (Python)...
cd backend
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
)
echo Installing Python dependencies...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt >nul
cd ..

echo.
echo [4/4] Setting up Frontend (Node.js)...
cd frontend
echo Installing Node.js dependencies...
call npm install >nul
cd ..

echo.
echo Creating Desktop Shortcut...
set "VBS_SCRIPT=%TEMP%\create_shortcut.vbs"
echo Set oWS = WScript.CreateObject("WScript.Shell") > "%VBS_SCRIPT%"
echo sLinkFile = "%USERPROFILE%\Desktop\AlphaAlign.lnk" >> "%VBS_SCRIPT%"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%VBS_SCRIPT%"
echo oLink.TargetPath = "%INSTALL_DIR%\start.bat" >> "%VBS_SCRIPT%"
echo oLink.WorkingDirectory = "%INSTALL_DIR%" >> "%VBS_SCRIPT%"
echo oLink.Save >> "%VBS_SCRIPT%"
cscript /nologo "%VBS_SCRIPT%" >nul
del "%VBS_SCRIPT%"

echo.
echo ========================================================
echo Installation Complete!
echo.
echo AlphaAlign has been installed to %INSTALL_DIR%
echo A shortcut has been placed on your Desktop.
echo To start AlphaAlign, just double-click the desktop shortcut!
echo ========================================================
pause
