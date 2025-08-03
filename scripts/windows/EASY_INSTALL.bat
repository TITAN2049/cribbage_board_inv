@echo off
setlocal
title Cribbage Board Collection - Easy Install

:: Simple, clean installer
cls
echo.
echo ================================
echo  Cribbage Board Collection
echo  Easy One-Click Installer  
echo ================================
echo.
echo Installing... Please wait...
echo.

:: Try to run with Python first
python silent_install.py 2>nul
if not errorlevel 1 (
    echo.
    echo ✅ Installation completed successfully!
    echo Look for "Cribbage Board Collection" on your desktop
    goto :end
)

:: If Python not found, try to install it first
echo Python not found. Attempting to install...

:: Check if we can download Python
powershell -Command "Test-NetConnection -ComputerName www.python.org -Port 443 -InformationLevel Quiet" >nul 2>&1
if errorlevel 1 (
    echo.
    echo ❌ Cannot connect to internet to download Python.
    echo Please install Python manually from https://python.org
    echo Then run this installer again.
    echo.
    pause
    goto :end
)

:: Download and install Python
echo Downloading Python...
powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe' -OutFile '%TEMP%\python_installer.exe'" >nul 2>&1

if not exist "%TEMP%\python_installer.exe" (
    echo ❌ Failed to download Python installer
    pause
    goto :end
)

echo Installing Python (this may take a few minutes)...
"%TEMP%\python_installer.exe" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
timeout /t 30 /nobreak >nul

:: Clean up
del "%TEMP%\python_installer.exe" >nul 2>&1

:: Refresh environment and try again
call refreshenv >nul 2>&1
python silent_install.py

:end
echo.
echo Installation process completed.
pause
