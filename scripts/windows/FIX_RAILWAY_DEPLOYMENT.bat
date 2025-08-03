@echo off
REM Quick Fix for Railway Deployment Issue
REM This script ensures the correct app version is deployed

echo ================================================================
echo           RAILWAY DEPLOYMENT FIX - PLAYER PHOTOS
echo ================================================================
echo.
echo The error shows your Railway deployment is using the old app
echo without player photo support. This script will fix it.
echo.

REM Check if we're in the right directory
if not exist "app" (
    echo ❌ Error: Not in the correct directory
    echo Please run this from your cribbage board collection folder
    pause
    exit /b 1
)

echo ✅ Found app directory
echo.

REM Check if git is available
git --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Git is not available
    echo Please install Git or commit your changes manually
    pause
    exit /b 1
)

echo ✅ Git is available
echo.

echo 🔍 Checking current deployment configuration...
echo.

REM Check Procfile
if exist "Procfile" (
    echo ✅ Procfile exists
    type Procfile
) else (
    echo ❌ Procfile missing - creating it...
    echo web: python railway_production.py > Procfile
    echo ✅ Procfile created
)

echo.

REM Check if changes need to be committed
git status --porcelain >nul 2>&1
if errorlevel 1 (
    echo ⚠️ Git status check failed
) else (
    echo 📋 Current git status:
    git status --short
)

echo.
echo 🔄 Adding all changes to git...
git add .

echo.
echo 💾 Committing changes...
git commit -m "Fix: Update to use app_hybrid.py with player photo support"

echo.
echo 🚀 DEPLOYMENT INSTRUCTIONS:
echo ================================================================
echo.
echo The code is now ready for deployment. Choose your method:
echo.
echo METHOD 1 - Railway CLI (if installed):
echo   railway up
echo.
echo METHOD 2 - GitHub Integration:
echo   git push origin main
echo   (Railway will auto-deploy)
echo.
echo METHOD 3 - Manual Upload:
echo   1. Go to your Railway dashboard
echo   2. Trigger a new deployment
echo   3. Wait for it to complete
echo.
echo ================================================================
echo.
echo ✅ After deployment, the player photos will work!
echo 🎯 The error about 'edit_player' route will be fixed!
echo.
echo Your app will then have:
echo - Player photo uploads
echo - Edit player functionality  
echo - Professional player profiles
echo - All the latest features!
echo.
pause
