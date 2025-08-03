#!/usr/bin/env python3
"""
Silent launcher for Cribbage Board Collection
Runs the application completely in the background
"""

import os
import sys
import subprocess
import time
import webbrowser
from pathlib import Path

def run_silent():
    """Run the application silently in background"""
    try:
        # Get the directory where this script is located
        app_dir = Path(__file__).parent.absolute()
        os.chdir(app_dir)
        
        # Path to Python in virtual environment
        if os.name == 'nt':  # Windows
            python_exe = app_dir / "venv" / "Scripts" / "python.exe"
        else:
            python_exe = app_dir / "venv" / "bin" / "python"
        
        # Initialize database silently
        subprocess.run([str(python_exe), "init_db.py"], 
                      stdout=subprocess.DEVNULL, 
                      stderr=subprocess.DEVNULL, 
                      creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
        
        # Start the Flask app in background
        env = os.environ.copy()
        env['FLASK_APP'] = str(app_dir / 'app' / 'app.py')
        env['FLASK_ENV'] = 'production'
        
        # Start Flask with no console window
        flask_process = subprocess.Popen(
            [str(python_exe), "-m", "flask", "run", "--port", "5000", "--host", "127.0.0.1"],
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )
        
        # Wait a moment for server to start
        time.sleep(3)
        
        # Open browser
        webbrowser.open('http://localhost:5000')
        
        return True
        
    except Exception as e:
        # If anything fails, try the basic approach
        return False

if __name__ == "__main__":
    # Hide console window on Windows
    if os.name == 'nt':
        import ctypes
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
    
    run_silent()
