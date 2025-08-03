@echo off
setlocal enabledelayedexpansion
title Cribbage Board Collection - One Click Installer

:: Hide cursor and clear screen
echo off
cls

:: Set window size and colors
mode con: cols=80 lines=25
color 0A

echo.
echo  ████████████████████████████████████████████████████████████████████████████
echo  █                                                                          █
echo  █             Cribbage Board Collection - One Click Install               █  
echo  █                                                                          █
echo  ████████████████████████████████████████████████████████████████████████████
echo.
echo  Installing... Please wait (this may take a few minutes)
echo.

:: Create a temporary log file
set "LOGFILE=%TEMP%\cribbage_install.log"
echo Installation started at %DATE% %TIME% > "%LOGFILE%"

:: Step 1: Check and install Python if needed
echo  [1/5] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo  [1/5] Python not found - downloading and installing...
    echo Downloading Python... >> "%LOGFILE%"
    
    :: Download Python installer
    powershell -Command "& {Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe' -OutFile '%TEMP%\python_installer.exe'}" >> "%LOGFILE%" 2>&1
    
    if exist "%TEMP%\python_installer.exe" (
        echo Installing Python silently... >> "%LOGFILE%"
        "%TEMP%\python_installer.exe" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0 >> "%LOGFILE%" 2>&1
        
        :: Wait for installation to complete
        timeout /t 30 /nobreak >nul
        
        :: Refresh environment variables
        call refreshenv >nul 2>&1
        
        :: Check again
        python --version >nul 2>&1
        if errorlevel 1 (
            echo  ❌ Python installation failed. Please install Python manually.
            pause
            exit /b 1
        )
        
        :: Clean up installer
        del "%TEMP%\python_installer.exe" >nul 2>&1
    ) else (
        echo  ❌ Failed to download Python installer.
        pause
        exit /b 1
    )
) else (
    echo  ✅ Python found
)

:: Step 2: Create virtual environment
echo  [2/5] Setting up environment...
echo Creating virtual environment... >> "%LOGFILE%"
python -m venv venv >> "%LOGFILE%" 2>&1
if errorlevel 1 (
    echo  ❌ Failed to create virtual environment
    pause
    exit /b 1
)

:: Step 3: Install dependencies
echo  [3/5] Installing dependencies...
echo Installing packages... >> "%LOGFILE%"
call venv\Scripts\activate.bat && python -m pip install --upgrade pip --quiet >> "%LOGFILE%" 2>&1
call venv\Scripts\activate.bat && pip install -r requirements.txt --quiet >> "%LOGFILE%" 2>&1
if errorlevel 1 (
    echo  ❌ Failed to install dependencies
    pause
    exit /b 1
)

:: Step 4: Setup application
echo  [4/5] Setting up application...
echo Setting up directories and database... >> "%LOGFILE%"

:: Create uploads directory
if not exist "app\static\uploads" (
    mkdir "app\static\uploads" >> "%LOGFILE%" 2>&1
)

:: Create database if it doesn't exist
if not exist "app\database.db" (
    sqlite3 app\database.db < schema.sql >> "%LOGFILE%" 2>&1 || (
        echo Warning: Database creation may have failed >> "%LOGFILE%"
    )
)

::: Step 5: Create desktop shortcut
echo  [5/5] Creating desktop shortcut...
echo Creating desktop shortcut... >> "%LOGFILE%"

:: Get the desktop path (try multiple methods)
set "DESKTOP="
for /f "tokens=3*" %%i in ('reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders" /v Desktop 2^>nul') do set "DESKTOP=%%j"
if not defined DESKTOP set "DESKTOP=%USERPROFILE%\Desktop"
if not exist "%DESKTOP%" (
    set "DESKTOP=%USERPROFILE%\OneDrive\Desktop"
)
if not exist "%DESKTOP%" (
    mkdir "%USERPROFILE%\Desktop" >nul 2>&1
    set "DESKTOP=%USERPROFILE%\Desktop"
)

echo Desktop path: %DESKTOP% >> "%LOGFILE%"

:: Create a batch file to run the application
set "RUNNER=%~dp0run_cribbage.bat"
echo @echo off > "%RUNNER%"
echo title Cribbage Board Collection >> "%RUNNER%"
echo cd /d "%~dp0" >> "%RUNNER%"
echo if not exist venv\Scripts\activate.bat ( >> "%RUNNER%"
echo     echo Error: Application not properly installed >> "%RUNNER%"
echo     pause >> "%RUNNER%"
echo     exit /b 1 >> "%RUNNER%"
echo ^) >> "%RUNNER%"
echo call venv\Scripts\activate.bat >> "%RUNNER%"
echo echo Starting Cribbage Board Collection... >> "%RUNNER%"
echo start /min cmd /c "python start_app.py" >> "%RUNNER%"
echo timeout /t 3 /nobreak ^>nul >> "%RUNNER%"
echo start http://localhost:5000 >> "%RUNNER%"
echo exit >> "%RUNNER%"

:: Create VBS script to run without console window
set "VBSFILE=%~dp0run_cribbage_silent.vbs"
echo Set objShell = CreateObject("WScript.Shell") > "%VBSFILE%"
echo objShell.Run "%RUNNER%", 0, False >> "%VBSFILE%"

:: Create the desktop shortcut using a simpler method
set "SHORTCUT=%DESKTOP%\Cribbage Board Collection.lnk"
echo Creating shortcut at: %SHORTCUT% >> "%LOGFILE%"

:: Create PowerShell script for shortcut creation
set "PSFILE=%TEMP%\create_shortcut.ps1"
echo $WshShell = New-Object -comObject WScript.Shell > "%PSFILE%"
echo $Shortcut = $WshShell.CreateShortcut('%SHORTCUT%') >> "%PSFILE%"
echo $Shortcut.TargetPath = '%VBSFILE%' >> "%PSFILE%"
echo $Shortcut.WorkingDirectory = '%~dp0' >> "%PSFILE%"
echo $Shortcut.IconLocation = '%%SystemRoot%%\System32\shell32.dll,21' >> "%PSFILE%"
echo $Shortcut.Description = 'Cribbage Board Collection Manager' >> "%PSFILE%"
echo $Shortcut.Save() >> "%PSFILE%"

:: Run the PowerShell script
powershell -ExecutionPolicy Bypass -File "%PSFILE%" >> "%LOGFILE%" 2>&1

:: Clean up the temporary PowerShell file
del "%PSFILE%" >nul 2>&1

:: Verify shortcut was created
if exist "%SHORTCUT%" (
    echo ✅ Desktop shortcut created successfully >> "%LOGFILE%"
) else (
    echo ❌ Failed to create desktop shortcut >> "%LOGFILE%"
)

:: Final success message
cls
echo.
echo  ████████████████████████████████████████████████████████████████████████████
echo  █                                                                          █
echo  █                         INSTALLATION COMPLETE!                         █  
echo  █                                                                          █
echo  ████████████████████████████████████████████████████████████████████████████
echo.
echo  ✅ Cribbage Board Collection has been installed successfully!
echo.
echo  📍 A shortcut has been created on your desktop
echo  📍 Double-click "Cribbage Board Collection" to start the application
echo.
echo  The application will open in your web browser at: http://localhost:5000
echo.
echo  ════════════════════════════════════════════════════════════════════════════
echo.

:: Clean up
del "%LOGFILE%" >nul 2>&1

echo  Press any key to exit...
pause >nul
exit /b 0
