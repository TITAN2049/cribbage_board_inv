@echo off
title Cribbage Board Collection - Simple Install

:: Simple installer without cleanup (for testing)
cls
echo.
echo  ████████████████████████████████████████████
echo  █      Cribbage Board Collection          █
echo  █         Simple Install                  █  
echo  ████████████████████████████████████████████
echo.

:: Check if running as admin, if not request it
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo  Requesting administrator privileges...
    powershell -Command "Start-Process cmd -ArgumentList '/c \"%~f0\"' -Verb RunAs"
    exit /b
)

:: Set installation directory
set "INSTALL_DIR=%ProgramFiles%\Cribbage Board Collection"

echo  Installing to: %INSTALL_DIR%
echo.

:: Create installation directory
if exist "%INSTALL_DIR%" (
    rmdir /s /q "%INSTALL_DIR%" >nul 2>&1
)
mkdir "%INSTALL_DIR%" >nul 2>&1

:: Install Python if needed
python --version >nul 2>&1
if errorlevel 1 (
    echo  Installing Python...
    powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe' -OutFile '%TEMP%\python_installer.exe'" >nul 2>&1
    if exist "%TEMP%\python_installer.exe" (
        "%TEMP%\python_installer.exe" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0 >nul 2>&1
        timeout /t 20 /nobreak >nul
        del "%TEMP%\python_installer.exe" >nul 2>&1
    )
)

:: Copy files
echo  Copying application files...
xcopy "%~dp0app" "%INSTALL_DIR%\app" /E /I /H /Y >nul 2>&1
copy "%~dp0requirements.txt" "%INSTALL_DIR%\" >nul 2>&1
copy "%~dp0schema.sql" "%INSTALL_DIR%\" >nul 2>&1
copy "%~dp0start_app.py" "%INSTALL_DIR%\" >nul 2>&1
copy "%~dp0init_db.py" "%INSTALL_DIR%\" >nul 2>&1

:: Setup Python environment
echo  Setting up Python environment...
cd /d "%INSTALL_DIR%"
python -m venv venv >nul 2>&1
call venv\Scripts\activate.bat && python -m pip install --upgrade pip --quiet >nul 2>&1
call venv\Scripts\activate.bat && pip install -r requirements.txt --quiet >nul 2>&1

:: Initialize database
echo  Setting up database...
call venv\Scripts\activate.bat && python init_db.py >nul 2>&1

:: Create launcher
echo @echo off > launch.bat
echo cd /d "%INSTALL_DIR%" >> launch.bat
echo call venv\Scripts\activate.bat >> launch.bat
echo python init_db.py ^>nul 2^>^&1 >> launch.bat
echo start /b python start_app.py >> launch.bat
echo timeout /t 2 /nobreak ^>nul >> launch.bat
echo start http://localhost:5000 >> launch.bat

:: Create silent launcher
echo Set objShell = CreateObject("WScript.Shell") > launch_silent.vbs
echo objShell.CurrentDirectory = "%INSTALL_DIR%" >> launch_silent.vbs
echo objShell.Run "launch.bat", 0, False >> launch_silent.vbs

:: Create desktop shortcut
set "DESKTOP=%USERPROFILE%\Desktop"
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%DESKTOP%\Cribbage Board Collection.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\launch_silent.vbs'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.IconLocation = '%SystemRoot%\System32\imageres.dll,109'; $Shortcut.Description = 'Cribbage Board Collection Manager'; $Shortcut.Save()" >nul 2>&1

echo.
echo  ✅ Installation Complete!
echo.
echo  📍 Installed to: %INSTALL_DIR%
echo  📍 Desktop shortcut created
echo.
echo  Double-click the desktop shortcut to start the application!
echo.
pause
