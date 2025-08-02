@echo off
echo ====================================
echo   Creating Desktop Shortcut
echo ====================================
echo.

set "CURRENT_DIR=%~dp0"
set "SHORTCUT_NAME=Cribbage Board Collection"
set "DESKTOP=%USERPROFILE%\Desktop"

:: Create a PowerShell script to create the shortcut
echo Creating shortcut on desktop...

powershell -Command "& {$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%DESKTOP%\%SHORTCUT_NAME%.lnk'); $Shortcut.TargetPath = '%CURRENT_DIR%start_app.py'; $Shortcut.WorkingDirectory = '%CURRENT_DIR%'; $Shortcut.IconLocation = '%SystemRoot%\System32\imageres.dll,109'; $Shortcut.Description = 'Cribbage Board Collection Manager'; $Shortcut.Save()}"

if %errorlevel% equ 0 (
    echo ✅ Desktop shortcut created successfully!
    echo You can now double-click "%SHORTCUT_NAME%" on your desktop to start the app
) else (
    echo ❌ Failed to create shortcut
)

echo.
pause
