#!/usr/bin/env python3
"""
Cribbage Board Collection - Optimized Application Starter
Lightweight, efficient script to start the Flask application
"""

import os
import sys
import subprocess
import platform
import socket
import webbrowser
import time
import signal
import atexit

# Global variable to track server process
server_process = None

def cleanup():
    """Clean up resources on exit"""
    global server_process
    if server_process:
        try:
            server_process.terminate()
            server_process.wait(timeout=5)
        except:
            try:
                server_process.kill()
            except:
                pass

def signal_handler(signum, frame):
    """Handle Ctrl+C gracefully"""
    print("\n👋 Shutting down...")
    cleanup()
    sys.exit(0)

def check_port(port):
    """Check if a port is available"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', port))
            return result != 0
    except:
        return False

def find_available_port():
    """Find an available port starting from 5000"""
    for port in range(5000, 5010):
        if check_port(port):
            return port
    return None

def setup_database():
    """Setup database if it doesn't exist"""
    db_path = os.path.join("app", "database.db")
    if not os.path.exists(db_path):
        schema_path = "schema.sql"
        if os.path.exists(schema_path):
            try:
                with open(schema_path, 'r') as f:
                    schema = f.read()
                subprocess.run(["sqlite3", db_path], input=schema, 
                             text=True, check=True, timeout=10)
                return True
            except:
                pass
    return os.path.exists(db_path)

def start_app():
    """Start the Flask application efficiently"""
    global server_process
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    atexit.register(cleanup)
    
    # Minimal output - no fancy banners for efficiency
    print("Starting Cribbage Board Collection...")
    
    # Check virtual environment
    os_name = platform.system()
    venv_python = os.path.join("venv", "Scripts", "python.exe") if os_name == "Windows" else os.path.join("venv", "bin", "python")
    
    if not os.path.exists(venv_python):
        print("Error: Application not properly installed")
        print("Please run the installer")
        return False
    
    # Setup database
    if not setup_database():
        print("Warning: Database setup may have failed")
    
    # Find available port
    port = find_available_port()
    if not port:
        print("Error: No available ports")
        return False
    
    # Set minimal environment
    env = os.environ.copy()
    env['FLASK_APP'] = os.path.join('app', 'app.py')
    env['FLASK_ENV'] = 'production'  # Production mode for efficiency
    env['PYTHONOPTIMIZE'] = '1'  # Enable Python optimizations
    
    try:
        # Start Flask with minimal logging for better performance
        cmd = [
            venv_python, "-m", "flask", "run", 
            "--port", str(port), 
            "--host", "127.0.0.1",  # Only localhost for security
            "--no-reload",  # Disable auto-reload for efficiency
            "--no-debugger"  # Disable debugger for efficiency
        ]
        
        # Start server process
        server_process = subprocess.Popen(
            cmd, env=env, 
            stdout=subprocess.DEVNULL if '--silent' in sys.argv else None,
            stderr=subprocess.PIPE
        )
        
        # Wait a moment for server to start
        time.sleep(1.5)
        
        # Check if server started successfully
        if server_process.poll() is not None:
            stderr_output = server_process.stderr.read().decode()
            print(f"Error starting server: {stderr_output}")
            return False
        
        # Open browser only if server started successfully
        if check_port(port):
            print("Server failed to start")
            return False
            
        print(f"Server started on http://localhost:{port}")
        
        # Open browser
        try:
            webbrowser.open(f'http://localhost:{port}')
        except:
            print("Could not open browser automatically")
            print(f"Please open: http://localhost:{port}")
        
        # Wait for server process
        server_process.wait()
        
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        cleanup()
    
    return True

def main():
    """Main entry point"""
    # Change to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Start the application
    success = start_app()
    
    if not success:
        print("Failed to start application")
        if '--no-pause' not in sys.argv:
            input("Press Enter to exit...")
        sys.exit(1)

if __name__ == "__main__":
    main()
