@echo off
echo ====================================
echo   Cribbage Board Collection Setup
echo ====================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or later from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo Python found!
python --version

:: Create virtual environment
echo.
echo Creating virtual environment...
python -m venv venv
if %errorlevel% neq 0 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

:: Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

:: Upgrade pip
echo.
echo Upgrading pip...
python -m pip install --upgrade pip

:: Install requirements
echo.
echo Installing required packages...
pip install flask werkzeug

:: Create database
echo.
echo Setting up database...
if not exist app\database.db (
    echo Creating database from schema...
    sqlite3 app\database.db < schema.sql
    if %errorlevel% neq 0 (
        echo ERROR: Failed to create database
        echo Make sure SQLite3 is installed
        pause
        exit /b 1
    )
    echo Database created successfully!
) else (
    echo Database already exists, skipping creation...
)

:: Create uploads directory
if not exist app\static\uploads (
    mkdir app\static\uploads
    echo Created uploads directory
)

echo.
echo ====================================
echo   Setup Complete!
echo ====================================
echo.
echo To start the application, run: windows_run.bat
echo.
pause
