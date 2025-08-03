#!/usr/bin/env python3
"""
Railway Production startup script with PostgreSQL support
"""

import os
import sqlite3
import psycopg2
from pathlib import Path

def init_database():
    """Initialize database - PostgreSQL on Railway, SQLite locally"""
    database_url = os.environ.get('DATABASE_URL')
    
    if database_url:
        # PostgreSQL on Railway
        print("� Initializing PostgreSQL database on Railway...")
        try:
            conn = psycopg2.connect(database_url)
            cursor = conn.cursor()
            
            # Check if tables exist
            cursor.execute("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_name = 'boards'
            """)
            
            if not cursor.fetchone():
                print("Creating PostgreSQL tables...")
                
                # Create tables for PostgreSQL
                cursor.execute("""
                    CREATE TABLE boards (
                        id SERIAL PRIMARY KEY,
                        roman_number VARCHAR(10),
                        description TEXT,
                        wood_type VARCHAR(100),
                        stain VARCHAR(100),
                        finish VARCHAR(100),
                        pegs_included VARCHAR(10),
                        price DECIMAL(10,2),
                        front_view VARCHAR(255),
                        back_view VARCHAR(255),
                        date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                cursor.execute("""
                    CREATE TABLE players (
                        id SERIAL PRIMARY KEY,
                        first_name VARCHAR(100) NOT NULL,
                        last_name VARCHAR(100) NOT NULL,
                        photo VARCHAR(255),
                        date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                cursor.execute("""
                    CREATE TABLE games (
                        id SERIAL PRIMARY KEY,
                        board_id INTEGER REFERENCES boards(id),
                        winner_id INTEGER REFERENCES players(id),
                        loser_id INTEGER REFERENCES players(id),
                        date_played DATE,
                        is_skunk BOOLEAN DEFAULT FALSE,
                        is_double_skunk BOOLEAN DEFAULT FALSE,
                        date_recorded TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                conn.commit()
                print("✅ PostgreSQL tables created successfully!")
            else:
                print("✅ PostgreSQL database already initialized")
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            print(f"❌ PostgreSQL initialization failed: {e}")
    
    else:
        # SQLite for local development
        print("🗃️  Initializing SQLite database for local development...")
        base_dir = Path(__file__).parent
        data_dir = base_dir / "data"
        db_path = data_dir / "database.db"
        schema_path = base_dir / "schema.sql"
        
        data_dir.mkdir(exist_ok=True)
        (data_dir / "uploads").mkdir(exist_ok=True)
        
        if not db_path.exists():
            try:
                with open(schema_path, 'r') as f:
                    schema = f.read()
                
                conn = sqlite3.connect(str(db_path))
                conn.executescript(schema)
                conn.close()
                print("✅ SQLite database initialized!")
            except Exception as e:
                print(f"❌ SQLite initialization failed: {e}")
        else:
            print("✅ SQLite database already exists")

def main():
    """Main entry point for Railway production"""
    print("🚀 Starting Cribbage Board Collection (Railway Production)")
    
    # Initialize database
    init_database()
    
    # Import the hybrid app
    from app.app import app
    
    # Get port from environment
    port = int(os.environ.get('PORT', 5000))
    
    # Configure for production
    app.config.update(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'cribbage_board_collection_secret_key_2024_production'),
        ENV='production',
        DEBUG=False,
        TESTING=False
    )
    
    print(f"🌐 Starting server on port {port}")
    print("📱 App accessible from any device with internet!")
    
    # Start with Gunicorn for better performance
    import subprocess
    import sys
    
    try:
        cmd = [
            sys.executable, "-m", "gunicorn",
            "--bind", f"0.0.0.0:{port}",
            "--workers", "2",
            "--timeout", "120",
            "app.app:app"
        ]
        subprocess.run(cmd, check=True)
    except (ImportError, FileNotFoundError):
        print("⚠️  Using Flask dev server")
        app.run(host='0.0.0.0', port=port, debug=False)

if __name__ == '__main__':
    main()
