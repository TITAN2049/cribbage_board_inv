#!/usr/bin/env python3
"""
Cribbage Board Collection - Application Starter
Cross-platform script to start the Flask application
"""

import os
import sys
import subprocess
import platform
import socket
import webbrowser
import time

def check_port(port):
    """Check if a port is available"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', port))
    sock.close()
    return result != 0  # Returns True if port is available

def find_available_port():
    """Find an available port starting from 5000"""
    for port in range(5000, 5010):
        if check_port(port):
            return port
    return None

def start_app():
    """Start the Flask application"""
    print("=" * 50)
    print("🚀 Starting Cribbage Board Collection")
    print("=" * 50)
    print()
    
    # Check if virtual environment exists
    os_name = platform.system()
    if os_name == "Windows":
        venv_python = os.path.join("venv", "Scripts", "python.exe")
        if not os.path.exists(venv_python):
            print("❌ Virtual environment not found!")
            print("Please run the installer first:")
            print("  • Double-click 'install.py'")
            print("  • Or run 'windows_setup.bat'")
            input("Press Enter to exit...")
            return
    else:
        venv_python = os.path.join("venv", "bin", "python")
        if not os.path.exists(venv_python):
            print("❌ Virtual environment not found!")
            print("Please run the installer first:")
            print("  • Run: python3 install.py")
            print("  • Or run: ./setup.sh")
            input("Press Enter to exit...")
            return
    
    # Check if database exists
    db_path = os.path.join("app", "database.db")
    if not os.path.exists(db_path):
        print("🗄️ Creating database...")
        try:
            subprocess.run(["sqlite3", db_path], input=open("schema.sql").read(), 
                         text=True, check=True)
            print("✅ Database created")
        except:
            print("⚠️  Could not create database automatically")
    
    # Find available port
    port = find_available_port()
    if not port:
        print("❌ No available ports found (5000-5009)")
        input("Press Enter to exit...")
        return
    
    if port != 5000:
        print(f"⚠️  Port 5000 is busy, using port {port}")
    
    # Set environment variables
    env = os.environ.copy()
    env['FLASK_APP'] = os.path.join('app', 'app.py')
    
    print(f"🌐 Starting server on port {port}...")
    print(f"📱 URL: http://localhost:{port}")
    print()
    print("=" * 50)
    print("🎯 Application is starting...")
    print("Your browser should open automatically")
    print("Press Ctrl+C to stop the server")
    print("=" * 50)
    print()
    
    # Start Flask app
    try:
        # Open browser after a short delay
        def open_browser():
            time.sleep(2)
            webbrowser.open(f'http://localhost:{port}')
        
        import threading
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        # Start Flask
        cmd = [venv_python, "-m", "flask", "run", "--port", str(port), "--host", "0.0.0.0"]
        subprocess.run(cmd, env=env)
        
    except KeyboardInterrupt:
        print("\n👋 Application stopped")
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    start_app()
