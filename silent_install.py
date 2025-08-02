#!/usr/bin/env python3
"""
Cribbage Board Collection - Silent Installer
Handles everything automatically with minimal user interaction
"""

import os
import sys
import subprocess
import platform
import urllib.request
import tempfile
import shutil
from pathlib import Path

def run_command_silent(command, description=""):
    """Run a command silently"""
    try:
        result = subprocess.run(command, shell=True, check=True, 
                              capture_output=True, text=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def check_python():
    """Check if Python is installed and version"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        return False, f"{version.major}.{version.minor}.{version.micro}"
    return True, f"{version.major}.{version.minor}.{version.micro}"

def install_python_windows():
    """Install Python on Windows silently"""
    print("Downloading Python installer...")
    
    # Download Python
    python_url = "https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe"
    installer_path = os.path.join(tempfile.gettempdir(), "python_installer.exe")
    
    try:
        urllib.request.urlretrieve(python_url, installer_path)
        print("Installing Python...")
        
        # Install silently
        cmd = f'"{installer_path}" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0'
        success, output = run_command_silent(cmd)
        
        # Clean up
        if os.path.exists(installer_path):
            os.remove(installer_path)
            
        return success
    except Exception as e:
        print(f"Failed to install Python: {e}")
        return False

def create_desktop_shortcut_windows():
    """Create desktop shortcut on Windows"""
    try:
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        if not os.path.exists(desktop):
            # Try alternative desktop location
            desktop = os.path.join(os.path.expanduser("~"), "OneDrive", "Desktop")
        
        app_dir = os.getcwd()
        
        # Create runner batch file
        runner_path = os.path.join(app_dir, "run_cribbage.bat")
        with open(runner_path, 'w') as f:
            f.write('@echo off\n')
            f.write(f'cd /d "{app_dir}"\n')
            f.write('call venv\\Scripts\\activate.bat\n')
            f.write('start /min cmd /c "python start_app.py"\n')
            f.write('timeout /t 3 /nobreak >nul\n')
            f.write('start http://localhost:5000\n')
        
        # Create VBS file for silent execution
        vbs_path = os.path.join(app_dir, "run_cribbage_silent.vbs")
        with open(vbs_path, 'w') as f:
            f.write('Set objShell = CreateObject("WScript.Shell")\n')
            f.write(f'objShell.Run """"{runner_path}"""", 0, False\n')
        
        # Create shortcut using PowerShell
        shortcut_path = os.path.join(desktop, "Cribbage Board Collection.lnk")
        ps_cmd = f'''
$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut('{shortcut_path}')
$Shortcut.TargetPath = '{vbs_path}'
$Shortcut.WorkingDirectory = '{app_dir}'
$Shortcut.IconLocation = '%SystemRoot%\\System32\\shell32.dll,21'
$Shortcut.Description = 'Cribbage Board Collection Manager'
$Shortcut.Save()
'''
        success, _ = run_command_silent(f'powershell -Command "& {{{ps_cmd}}}"')
        return success
        
    except Exception as e:
        print(f"Failed to create desktop shortcut: {e}")
        return False

def main():
    print("Cribbage Board Collection - Automated Installer")
    print("=" * 50)
    
    # Check if we're on Windows
    if platform.system() != "Windows":
        print("This installer is for Windows only.")
        print("Please use the regular install.py for other systems.")
        input("Press Enter to exit...")
        return
    
    # Step 1: Check/Install Python
    print("Checking Python installation...")
    python_ok, version = check_python()
    
    if not python_ok:
        print(f"Python version {version} is too old or not found.")
        print("Installing Python automatically...")
        
        if not install_python_windows():
            print("❌ Failed to install Python automatically.")
            print("Please install Python 3.8+ manually from python.org")
            input("Press Enter to exit...")
            return
        
        print("✅ Python installed successfully!")
    else:
        print(f"✅ Python {version} found")
    
    # Step 2: Create virtual environment
    print("Creating virtual environment...")
    success, _ = run_command_silent("python -m venv venv")
    if not success:
        print("❌ Failed to create virtual environment")
        input("Press Enter to exit...")
        return
    
    # Step 3: Install packages
    print("Installing required packages...")
    success, _ = run_command_silent("venv\\Scripts\\activate.bat && python -m pip install --upgrade pip --quiet")
    if success:
        success, _ = run_command_silent("venv\\Scripts\\activate.bat && pip install -r requirements.txt --quiet")
    
    if not success:
        print("❌ Failed to install packages")
        input("Press Enter to exit...")
        return
    
    # Step 4: Setup application
    print("Setting up application...")
    
    # Create uploads directory
    uploads_dir = Path("app/static/uploads")
    uploads_dir.mkdir(parents=True, exist_ok=True)
    
    # Create database
    if not os.path.exists("app/database.db"):
        run_command_silent("sqlite3 app\\database.db < schema.sql")
    
    # Step 5: Create desktop shortcut
    print("Creating desktop shortcut...")
    if create_desktop_shortcut_windows():
        print("✅ Desktop shortcut created")
    else:
        print("⚠️ Desktop shortcut creation failed")
    
    print("\n" + "=" * 50)
    print("🎉 INSTALLATION COMPLETE!")
    print("=" * 50)
    print("\n✅ Cribbage Board Collection has been installed successfully!")
    print("📍 Look for 'Cribbage Board Collection' shortcut on your desktop")
    print("📍 Double-click it to start the application")
    print("\nThe application will open at: http://localhost:5000")
    print("\nPress Enter to exit...")
    input()

if __name__ == "__main__":
    main()
