@echo off
title Cribbage Board Collection - Complete Installer

:: Set colors for better visibility
color 0A

echo.
echo  ██████╗██████╗ ██╗██████╗ ██████╗  █████╗  ██████╗ ███████╗
echo ██╔════╝██╔══██╗██║██╔══██╗██╔══██╗██╔══██╗██╔════╝ ██╔════╝
echo ██║     ██████╔╝██║██████╔╝██████╔╝███████║██║  ███╗█████╗  
echo ██║     ██╔══██╗██║██╔══██╗██╔══██╗██╔══██║██║   ██║██╔══╝  
echo ╚██████╗██║  ██║██║██████╔╝██████╔╝██║  ██║╚██████╔╝███████╗
echo  ╚═════╝╚═╝  ╚═╝╚═╝╚═════╝ ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚══════╝
echo.
echo            Board Collection Manager - Complete Setup
echo ========================================================================
echo.

:: Check admin privileges
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  For best results, consider running as administrator
    echo    Right-click this file and select "Run as administrator"
    echo.
    timeout /t 3 >nul
)

:: Step 1: Install the application
echo 📦 STEP 1: Installing Application...
echo ========================================================================
call windows_setup.bat
if %errorlevel% neq 0 (
    echo ❌ Installation failed!
    pause
    exit /b 1
)

echo.
echo ✅ Application installed successfully!
echo.

:: Step 2: Create desktop shortcut
echo 🔗 STEP 2: Creating Desktop Shortcut...
echo ========================================================================
call create_shortcut.bat

echo.
echo 🚀 STEP 3: Testing Application...
echo ========================================================================
echo Starting the application for first-time test...
echo The app will open in your browser automatically.
echo.
echo ⚠️  IMPORTANT: After testing, close the browser and press Ctrl+C 
echo    in the server window to continue with setup completion.
echo.
pause

:: Test run the application
python start_app.py

echo.
echo ========================================================================
echo 🎉 SETUP COMPLETE!
echo ========================================================================
echo.
echo Your Cribbage Board Collection app is now ready to use!
echo.
echo 📋 HOW TO USE:
echo   • Double-click "Cribbage Board Collection" on your desktop
echo   • Or double-click "start_app.py" in this folder
echo   • Or run "windows_run.bat"
echo.
echo 🌐 The app will open at: http://localhost:5000
echo.
echo 📁 IMPORTANT FILE LOCATIONS:
echo   • Your database: app\database.db
echo   • Board photos: app\static\uploads\
echo   • Backup these folders to save your data!
echo.
echo 🔧 TROUBLESHOOTING:
echo   • If the app won't start, try running "windows_setup.bat" again
echo   • Make sure Python is installed with "Add to PATH" checked
echo   • Check WINDOWS_README.md for detailed help
echo.
echo ========================================================================
echo 💾 Don't forget to backup your data regularly!
echo ========================================================================
echo.
pause
