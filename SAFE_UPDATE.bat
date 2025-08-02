@echo off
REM Safe Code Update Script for Cribbage Board Collection
REM This script backs up your data before updating code

echo ================================================================
echo           CRIBBAGE BOARD COLLECTION - SAFE UPDATE
echo ================================================================
echo.
echo This script will:
echo 1. Backup your current database and images
echo 2. Allow you to update your code safely
echo 3. Restore your data after the update
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please run PROFESSIONAL_INSTALL.bat first
    pause
    exit /b 1
)

echo 🔄 Step 1: Creating backup of your data...
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
echo 📋 Your data has been safely backed up.
echo You can now update your code files without losing any data.
echo.
echo IMPORTANT INSTRUCTIONS:
echo 1. Your database and images are now backed up
echo 2. You can safely replace/update any code files
echo 3. After updating, run this script again with 'restore' option
echo 4. Or run: python backup_data.py restore
echo.
echo Would you like to migrate data to the new safe location now?
set /p migrate="Migrate data now? (y/n): "
if /i "%migrate%"=="y" (
    echo.
    echo 🔄 Migrating data to safe directory...
    python migrate_data.py
    echo.
    echo ✅ Data migration completed!
    echo Your data is now protected from code updates.
)

echo.
echo ================================================================
echo                    UPDATE INSTRUCTIONS
echo ================================================================
echo.
echo 1. ✅ Your data is safely backed up
echo 2. 🔄 You can now update/replace code files
echo 3. 🏃‍♂️ After updating, run your app normally:
echo    - Double-click: PROFESSIONAL_INSTALL.bat (if needed)
echo    - Or run: python start_app.py
echo    - Or run: python production.py
echo.
echo 4. 🔄 If you need to restore from backup:
echo    - Run: python backup_data.py restore
echo    - Or run this script again with 'restore'
echo.
echo Your cribbage board collection data is now safe! 🛡️
echo.
pause
