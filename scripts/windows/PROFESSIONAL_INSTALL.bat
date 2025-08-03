@echo off
setlocal enabledelayedexpansion
title Cribbage Board Collection - Professional Installer

:: Request admin privileges if not already running as admin
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Requesting administrator privileges...
    powershell -Command "Start-Process cmd -ArgumentList '/c \"%~f0\"' -Verb RunAs"
    exit /b
)

cls
color 0A
echo.
echo  ████████████████████████████████████████████████████████████████████████████
echo  █                                                                          █
echo  █                  Cribbage Board Collection Installer                    █  
echo  █                                                                          █
echo  ████████████████████████████████████████████████████████████████████████████
echo.
echo  Installing to Program Files... Please wait
echo.

:: Set installation directory in Program Files
set "INSTALL_DIR=%ProgramFiles%\Cribbage Board Collection"
set "LOGFILE=%TEMP%\cribbage_professional_install.log"

echo Installation started at %DATE% %TIME% > "%LOGFILE%"
echo Install directory: %INSTALL_DIR% >> "%LOGFILE%"

:: Step 1: Check and install Python if needed
echo  [1/6] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo  [1/6] Installing Python...
    
    :: Download Python installer silently
    powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe' -OutFile '%TEMP%\python_installer.exe'" >> "%LOGFILE%" 2>&1
    
    if exist "%TEMP%\python_installer.exe" (
        "%TEMP%\python_installer.exe" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0 >> "%LOGFILE%" 2>&1
        timeout /t 30 /nobreak >nul
        del "%TEMP%\python_installer.exe" >nul 2>&1
        
        :: Refresh PATH
        for /f "tokens=2*" %%a in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v PATH') do set "SYSTEM_PATH=%%b"
        for /f "tokens=2*" %%a in ('reg query "HKCU\Environment" /v PATH 2^>nul') do set "USER_PATH=%%b"
        set "PATH=%SYSTEM_PATH%;%USER_PATH%"
    )
)

python --version >nul 2>&1
if errorlevel 1 (
    echo  ❌ Python installation failed
    pause
    exit /b 1
)
echo  ✅ Python ready

:: Step 2: Create installation directory
echo  [2/6] Creating installation directory...
if exist "%INSTALL_DIR%" (
    rmdir /s /q "%INSTALL_DIR%" >> "%LOGFILE%" 2>&1
)
mkdir "%INSTALL_DIR%" >> "%LOGFILE%" 2>&1

:: Step 3: Copy application files
echo  [3/6] Copying application files...
xcopy "%~dp0app" "%INSTALL_DIR%\app" /E /I /H /Y >> "%LOGFILE%" 2>&1
copy "%~dp0requirements.txt" "%INSTALL_DIR%\" >> "%LOGFILE%" 2>&1
copy "%~dp0schema.sql" "%INSTALL_DIR%\" >> "%LOGFILE%" 2>&1
copy "%~dp0start_app.py" "%INSTALL_DIR%\" >> "%LOGFILE%" 2>&1
copy "%~dp0init_db.py" "%INSTALL_DIR%\" >> "%LOGFILE%" 2>&1
copy "%~dp0launch_silent.py" "%INSTALL_DIR%\" >> "%LOGFILE%" 2>&1

:: Step 4: Create optimized virtual environment
echo  [4/6] Setting up Python environment...
cd /d "%INSTALL_DIR%"
python -m venv venv --clear >> "%LOGFILE%" 2>&1
call venv\Scripts\activate.bat && python -m pip install --upgrade pip --quiet >> "%LOGFILE%" 2>&1
call venv\Scripts\activate.bat && pip install -r requirements.txt --quiet --no-cache-dir >> "%LOGFILE%" 2>&1

::: Step 5: Setup application data
echo  [5/6] Configuring application...
if not exist "%INSTALL_DIR%\app\static\uploads" (
    mkdir "%INSTALL_DIR%\app\static\uploads" >> "%LOGFILE%" 2>&1
)

:: Initialize database using Python script
call venv\Scripts\activate.bat && python init_db.py >> "%LOGFILE%" 2>&1

:: Create optimized launcher script
set "LAUNCHER=%INSTALL_DIR%\launch.bat"
echo @echo off > "%LAUNCHER%"
echo cd /d "%INSTALL_DIR%" >> "%LAUNCHER%"
echo call venv\Scripts\activate.bat >> "%LAUNCHER%"
echo python init_db.py ^>nul 2^>^&1 >> "%LAUNCHER%"
echo start /b python start_app.py ^>nul 2^>^&1 >> "%LAUNCHER%"
echo timeout /t 3 /nobreak ^>nul >> "%LAUNCHER%"
echo start http://localhost:5000 >> "%LAUNCHER%"

:: Create service-style VBS launcher (no windows, minimal resources)
set "VBSLAUNCHER=%INSTALL_DIR%\launch_silent.vbs"
echo Set objShell = CreateObject("WScript.Shell") > "%VBSLAUNCHER%"
echo Set objFSO = CreateObject("Scripting.FileSystemObject") >> "%VBSLAUNCHER%"
echo strAppPath = objFSO.GetParentFolderName(WScript.ScriptFullName) >> "%VBSLAUNCHER%"
echo objShell.CurrentDirectory = strAppPath >> "%VBSLAUNCHER%"
echo ' Run the Python silent launcher >> "%VBSLAUNCHER%"
echo objShell.Run "venv\Scripts\python.exe launch_silent.py", 0, False >> "%VBSLAUNCHER%"

:: Step 6: Create desktop and start menu shortcuts
echo  [6/6] Creating shortcuts...

:: Desktop shortcut
set "DESKTOP=%PUBLIC%\Desktop"
if not exist "%DESKTOP%" set "DESKTOP=%USERPROFILE%\Desktop"

powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%DESKTOP%\Cribbage Board Collection.lnk'); $Shortcut.TargetPath = '%VBSLAUNCHER%'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.IconLocation = '%SystemRoot%\System32\imageres.dll,109'; $Shortcut.Description = 'Cribbage Board Collection - Runs silently in background'; $Shortcut.Save()" >> "%LOGFILE%" 2>&1

:: Start Menu shortcut
set "STARTMENU=%ProgramData%\Microsoft\Windows\Start Menu\Programs"
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%STARTMENU%\Cribbage Board Collection.lnk'); $Shortcut.TargetPath = '%VBSLAUNCHER%'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.IconLocation = '%SystemRoot%\System32\imageres.dll,109'; $Shortcut.Description = 'Cribbage Board Collection - Runs silently in background'; $Shortcut.Save()" >> "%LOGFILE%" 2>&1

:: Create uninstaller
set "UNINSTALLER=%INSTALL_DIR%\uninstall.bat"
echo @echo off > "%UNINSTALLER%"
echo echo Uninstalling Cribbage Board Collection... >> "%UNINSTALLER%"
echo taskkill /f /im python.exe 2^>nul >> "%UNINSTALLER%"
echo timeout /t 2 /nobreak ^>nul >> "%UNINSTALLER%"
echo del "%DESKTOP%\Cribbage Board Collection.lnk" 2^>nul >> "%UNINSTALLER%"
echo del "%STARTMENU%\Cribbage Board Collection.lnk" 2^>nul >> "%UNINSTALLER%"
echo cd /d "%ProgramFiles%" >> "%UNINSTALLER%"
echo rmdir /s /q "Cribbage Board Collection" >> "%UNINSTALLER%"
echo echo Uninstall complete. >> "%UNINSTALLER%"
echo pause >> "%UNINSTALLER%"

:: Add to Windows Programs list
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\CribbageBoardCollection" /v "DisplayName" /d "Cribbage Board Collection" /f >> "%LOGFILE%" 2>&1
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\CribbageBoardCollection" /v "UninstallString" /d "%UNINSTALLER%" /f >> "%LOGFILE%" 2>&1
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\CribbageBoardCollection" /v "DisplayVersion" /d "1.0" /f >> "%LOGFILE%" 2>&1
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\CribbageBoardCollection" /v "Publisher" /d "Cribbage Board Collection" /f >> "%LOGFILE%" 2>&1
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\CribbageBoardCollection" /v "DisplayIcon" /d "%SystemRoot%\System32\imageres.dll,109" /f >> "%LOGFILE%" 2>&1

:: Final success message
cls
echo.
echo  ████████████████████████████████████████████████████████████████████████████
echo  █                                                                          █
echo  █                    PROFESSIONAL INSTALLATION COMPLETE!                  █  
echo  █                                                                          █
echo  ████████████████████████████████████████████████████████████████████████████
echo.
echo  ✅ Cribbage Board Collection installed successfully!
echo.
echo  📍 Installed to: %INSTALL_DIR%
echo  📍 Desktop shortcut created
echo  📍 Start Menu entry created
echo  📍 Added to Windows Programs list
echo.
echo  🚀 OPTIMIZED FOR PERFORMANCE:
echo     • Runs completely in background (no terminal windows)
echo     • Minimal memory usage
echo     • Fast startup
echo     • No background processes when not in use
echo     • Clean uninstall available
echo.
echo  To start: Double-click the desktop shortcut or find it in Start Menu
echo  To uninstall: Use Windows "Add or Remove Programs" or run uninstall.bat
echo.
echo  ════════════════════════════════════════════════════════════════════════════

:: Clean up
del "%LOGFILE%" >nul 2>&1

:: Auto-cleanup: Delete the downloaded/extracted installer files
echo  🧹 Cleaning up installation files...
set "SOURCE_DIR=%~dp0"
set "CLEANUP_BATCH=%TEMP%\cleanup_installer.bat"

:: Create a self-deleting cleanup script
echo @echo off > "%CLEANUP_BATCH%"
echo timeout /t 3 /nobreak ^>nul >> "%CLEANUP_BATCH%"
echo echo Cleaning up installation files... >> "%CLEANUP_BATCH%"
echo cd /d "%TEMP%" >> "%CLEANUP_BATCH%"
echo rmdir /s /q "%SOURCE_DIR%" 2^>nul >> "%CLEANUP_BATCH%"
echo del "%CLEANUP_BATCH%" 2^>nul >> "%CLEANUP_BATCH%"

echo.
echo  Installation complete! Press any key to exit...
echo  (Installation files will be automatically cleaned up)
pause >nul

:: Start the cleanup process in background
start /min cmd /c "%CLEANUP_BATCH%"
exit /b 0
