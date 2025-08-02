#!/usr/bin/env python3
"""
Production startup script for Railway deployment
Optimized for cloud hosting with proper configuration
"""

import os
import sqlite3
from pathlib import Path
from app.app import app

def init_database():
    """Initialize database for production"""
    base_dir = Path(__file__).parent
    
    # Use data directory for persistent storage
    data_dir = base_dir / "data"
    app_dir = base_dir / "app"
    db_path = data_dir / "database.db"
    schema_path = base_dir / "schema.sql"
    
    # Ensure directories exist
    data_dir.mkdir(exist_ok=True)
    (data_dir / "uploads").mkdir(exist_ok=True)
    app_dir.mkdir(exist_ok=True)
    (app_dir / "static" / "uploads").mkdir(parents=True, exist_ok=True)
    
    # Initialize database if it doesn't exist or is empty
    if not db_path.exists():
        # Check if database exists in old location
        old_db_path = app_dir / "database.db"
        if old_db_path.exists():
            print("Moving database from app directory to data directory...")
            old_db_path.rename(db_path)
            print("✅ Database moved to data directory")
        else:
            print("Initializing new database for production...")
            try:
                with open(schema_path, 'r') as f:
                    schema = f.read()
                
                conn = sqlite3.connect(str(db_path))
                conn.executescript(schema)
                conn.close()
                print("✅ Database initialized successfully!")
            except Exception as e:
                print(f"❌ Database initialization failed: {e}")
    else:
        print("✅ Database already exists in data directory")

def main():
    """Main entry point for production"""
    print("🚀 Starting Cribbage Board Collection (Production Mode)")
    
    # Initialize database
    init_database()
    
    # Get port from environment (Railway sets this)
    port = int(os.environ.get('PORT', 5000))
    
    # Configure for production
    app.config.update(
        # Security
        SECRET_KEY=os.environ.get('SECRET_KEY', 'cribbage_board_collection_secret_key_2024_production'),
        
        # Performance
        SEND_FILE_MAX_AGE_DEFAULT=31536000,  # 1 year cache for static files
        
        # Railway specific
        ENV='production',
        DEBUG=False,
        TESTING=False
    )
    
    print(f"🌐 Starting server on port {port}")
    print("📱 App will be accessible from any device with internet!")
    
    # Start the production server with Gunicorn
    import subprocess
    import sys
    
    try:
        # Use Gunicorn for production (more robust than Flask dev server)
        cmd = [
            sys.executable, "-m", "gunicorn",
            "--bind", f"0.0.0.0:{port}",
            "--workers", "2",
            "--timeout", "120",
            "--keep-alive", "5",
            "--max-requests", "1000",
            "--max-requests-jitter", "100",
            "app.app:app"
        ]
        subprocess.run(cmd, check=True)
    except (ImportError, FileNotFoundError):
        # Fallback to Flask dev server if Gunicorn not available
        print("⚠️  Gunicorn not found, using Flask dev server")
        app.run(
            host='0.0.0.0',  # Listen on all interfaces (required for Railway)
            port=port,
            debug=False,
            threaded=True,  # Handle multiple requests
            use_reloader=False  # Disable in production
        )

if __name__ == '__main__':
    main()
