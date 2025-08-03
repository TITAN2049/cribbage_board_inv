@echo off
REM Update Script with Player Photo Support

echo ================================================================
echo        CRIBBAGE BOARD COLLECTION - PLAYER PHOTOS UPDATE
echo ================================================================
echo.
echo This update adds photo support for players!
echo.
echo New Features:
echo - Players can now have profile photos
echo - Enhanced player detail pages
echo - Photo management in edit player page
echo - Improved player cards with photos
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please run PROFESSIONAL_INSTALL.bat first
    pause
    exit /b 1
)

echo 🔄 Step 1: Creating backup of your current data...
echo.
python backup_data.py
if errorlevel 1 (
    echo ❌ Backup failed! Update cancelled for safety.
    pause
    exit /b 1
)

echo.
echo ✅ Backup completed successfully!
echo.

echo 🔄 Step 2: Migrating database to support player photos...
echo.
python migrate_player_photos.py
if errorlevel 1 (
    echo ⚠️  Migration had some issues, but continuing...
)

echo.
echo 🔄 Step 3: Testing the updated application...
echo.
echo Starting the app to test new features...
echo Open your browser to: http://127.0.0.1:5000
echo.
echo ✅ Go to Players page to see the new photo features!
echo.
echo Press Ctrl+C to stop the test, then close this window
echo ================================================================
echo.

python app/app_hybrid.py

pause
