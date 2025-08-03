@echo off
REM Test the Railway-compatible version locally

echo ================================================================
echo         TESTING RAILWAY-COMPATIBLE VERSION LOCALLY
echo ================================================================
echo.
echo This will test your app using the same code that runs on Railway
echo but with SQLite database (since PostgreSQL is not available locally)
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please run PROFESSIONAL_INSTALL.bat first
    pause
    exit /b 1
)

echo 🔄 Starting hybrid app (Railway-compatible version)...
echo.
echo ✅ Using SQLite for local development
echo 🌐 App will be available at: http://127.0.0.1:5000
echo.
echo Press Ctrl+C to stop the server
echo ================================================================
echo.

python app/app_hybrid.py

pause
