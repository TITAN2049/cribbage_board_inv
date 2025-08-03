@echo off
title Cribbage Board Collection - Network Access

cls
echo.
echo  ████████████████████████████████████████████████████████████████████████████
echo  █                                                                          █
echo  █          Cribbage Board Collection - Network Access Mode                █  
echo  █                                                                          █
echo  ████████████████████████████████████████████████████████████████████████████
echo.
echo  This will start the app accessible from other devices on your network
echo.

:: Get local IP address
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4 Address"') do (
    set "LOCAL_IP=%%a"
    set "LOCAL_IP=!LOCAL_IP: =!"
    goto :found_ip
)
:found_ip

if not defined LOCAL_IP (
    set "LOCAL_IP=192.168.1.100"
    echo  ⚠️  Could not detect IP automatically. Using example: %LOCAL_IP%
) else (
    echo  🌐 Detected your local IP: %LOCAL_IP%
)

echo.
echo  📱 DEVICE ACCESS INSTRUCTIONS:
echo     • On same WiFi network, devices can access:
echo     • http://%LOCAL_IP%:5000
echo.
echo  🔥 FIREWALL NOTE:
echo     • Windows may ask to allow Python through firewall
echo     • Click "Allow" to enable network access
echo.
echo  Starting server... Press Ctrl+C to stop
echo.
echo  ════════════════════════════════════════════════════════════════════════════
echo.

:: Change to app directory and start with network access
cd /d "%~dp0"
python -c "
import os
import sys
sys.path.insert(0, 'app')
from app import app

print('🚀 Starting Cribbage Board Collection with network access...')
print(f'📱 Access from other devices: http://%LOCAL_IP%:5000')
print('💻 Local access: http://localhost:5000')
print()
print('Press Ctrl+C to stop the server')
print('=' * 60)

app.run(host='0.0.0.0', port=5000, debug=False)
"

echo.
echo Server stopped.
pause
