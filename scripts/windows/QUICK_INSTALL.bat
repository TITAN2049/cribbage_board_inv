@echo off
title Cribbage Board Collection - Quick Install

:: Simple, fast installation with minimal interaction
cls
echo.
echo  ████████████████████████████████████████████
echo  █      Cribbage Board Collection          █
echo  █         Quick Install                   █  
echo  ████████████████████████████████████████████
echo.
echo  This will install the application properly
echo  to your Program Files and create shortcuts.
echo.
echo  Press any key to continue or close window to cancel...
pause >nul

:: Check if running as admin, if not request it
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo  Requesting administrator privileges...
    echo  (Required to install to Program Files)
    echo.
    powershell -Command "Start-Process cmd -ArgumentList '/c \"%~f0\"' -Verb RunAs"
    exit /b
)

:: Run the professional installer
call "%~dp0PROFESSIONAL_INSTALL.bat"
