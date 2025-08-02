@echo off
echo ====================================
echo   Starting Cribbage Board Collection
echo ====================================
echo.

:: Check if virtual environment exists
if not exist venv\ (
    echo ERROR: Virtual environment not found
    echo Please run windows_setup.bat first
    pause
    exit /b 1
)

:: Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

:: Check if database exists
if not exist app\database.db (
    echo Database not found. Creating from schema...
    sqlite3 app\database.db < schema.sql
    if %errorlevel% neq 0 (
        echo ERROR: Failed to create database
        pause
        exit /b 1
    )
    echo Database created successfully!
)

:: Set Flask app
set FLASK_APP=app\app.py

:: Function to check if port is in use (simplified for Windows)
:: Try different ports
set PORT=5000

echo.
echo Starting server on port %PORT%...
echo.
echo ====================================
echo   Server Information
echo ====================================
echo Open your web browser and go to:
echo.
echo     http://localhost:%PORT%
echo.
echo Press Ctrl+C to stop the server
echo ====================================
echo.

:: Start Flask app
python -m flask run --port=%PORT% --host=0.0.0.0
