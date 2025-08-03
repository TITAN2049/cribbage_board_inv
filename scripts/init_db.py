#!/usr/bin/env python3
"""
Database initialization script for Cribbage Board Collection
Ensures database is created with proper schema
"""

import os
import sqlite3

def init_database():
    """Initialize the database with the schema"""
    # Get the directory where this script is located
    app_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(app_dir, "app", "database.db")
    schema_path = os.path.join(app_dir, "schema.sql")
    
    # Ensure app directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # If database doesn't exist or is empty, create it
    needs_init = not os.path.exists(db_path)
    
    if not needs_init:
        # Check if database has tables
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='players'")
            has_players_table = cursor.fetchone() is not None
            conn.close()
            needs_init = not has_players_table
        except:
            needs_init = True
    
    if needs_init:
        print("Initializing database...")
        try:
            with open(schema_path, 'r') as f:
                schema = f.read()
            
            conn = sqlite3.connect(db_path)
            conn.executescript(schema)
            conn.close()
            print("Database initialized successfully!")
            return True
        except Exception as e:
            print(f"Failed to initialize database: {e}")
            return False
    else:
        print("Database already exists and is properly initialized.")
        return True

if __name__ == "__main__":
    init_database()
