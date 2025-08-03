#!/usr/bin/env python3
"""
Cribbage Board Collection - Cross-platform Installer
This script sets up the application on Windows, Mac, or Linux
"""

import os
import sys
import subprocess
import platform

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, 
                              capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def check_python():
    """Check if Python is installed and version"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or later is required")
        print(f"Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} found")
    return True

def main():
    print("=" * 50)
    print("🎯 Cribbage Board Collection Installer")
    print("=" * 50)
    print()
    
    # Check Python version
    if not check_python():
        input("Press Enter to exit...")
        sys.exit(1)
    
    # Detect operating system
    os_name = platform.system()
    print(f"🖥️  Operating System: {os_name}")
    print()
    
    # Create virtual environment
    if not run_command("python -m venv venv", "Creating virtual environment"):
        input("Press Enter to exit...")
        sys.exit(1)
    
    # Activate virtual environment and install packages
    if os_name == "Windows":
        activate_cmd = "venv\\Scripts\\activate.bat &&"
        python_cmd = "python"
    else:
        activate_cmd = "source venv/bin/activate &&"
        python_cmd = "python3"
    
    # Install requirements
    install_cmd = f"{activate_cmd} {python_cmd} -m pip install --upgrade pip && {activate_cmd} pip install -r requirements.txt"
    if not run_command(install_cmd, "Installing Python packages"):
        input("Press Enter to exit...")
        sys.exit(1)
    
    # Create uploads directory
    uploads_dir = os.path.join("app", "static", "uploads")
    if not os.path.exists(uploads_dir):
        os.makedirs(uploads_dir)
        print("✅ Created uploads directory")
    
    # Create database if it doesn't exist
    db_path = os.path.join("app", "database.db")
    if not os.path.exists(db_path):
        if os_name == "Windows":
            db_cmd = "sqlite3 app\\database.db < schema.sql"
        else:
            db_cmd = "sqlite3 app/database.db < schema.sql"
        
        if run_command(db_cmd, "Creating database"):
            print("✅ Database created successfully")
        else:
            print("⚠️  Database creation failed, but app may still work")
    else:
        print("✅ Database already exists")
    
    print()
    print("=" * 50)
    print("🎉 Installation Complete!")
    print("=" * 50)
    print()
    
    if os_name == "Windows":
        print("To start the application:")
        print("  • Double-click 'windows_run.bat'")
        print("  • Or run: python start_app.py")
    else:
        print("To start the application:")
        print("  • Run: ./run.sh")
        print("  • Or run: python3 start_app.py")
    
    print()
    print("Then open your browser to: http://localhost:5000")
    print()
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()
