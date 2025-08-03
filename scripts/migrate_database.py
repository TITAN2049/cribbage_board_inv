#!/usr/bin/env python3
"""
Database migration script to add missing columns to existing databases
"""

import os
import sqlite3
from pathlib import Path

try:
    import psycopg2
    HAS_PSYCOPG2 = True
except ImportError:
    HAS_PSYCOPG2 = False

def migrate_sqlite():
    """Migrate SQLite database"""
    db_path = os.path.join(os.path.dirname(__file__), "..", "app", "database.db")
    
    if not os.path.exists(db_path):
        print("❌ No SQLite database found, skipping migration")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Add missing columns to boards table if they don't exist
        columns_to_add = [
            ("stain", "TEXT"),
            ("finish", "TEXT"),
            ("pegs_included", "TEXT"),
            ("price", "DECIMAL(10,2)")
        ]
        
        for column_name, column_type in columns_to_add:
            try:
                cursor.execute(f"ALTER TABLE boards ADD COLUMN {column_name} {column_type}")
                print(f"✅ Added column '{column_name}' to boards table")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e).lower():
                    print(f"⚠️  Column '{column_name}' already exists")
                else:
                    print(f"❌ Error adding column '{column_name}': {e}")
        
        conn.commit()
        conn.close()
        print("✅ SQLite database migration completed")
        
    except Exception as e:
        print(f"❌ Error migrating SQLite database: {e}")

def migrate_postgresql():
    """Migrate PostgreSQL database (Railway)"""
    if not HAS_PSYCOPG2:
        print("❌ psycopg2 not available, skipping PostgreSQL migration")
        return
        
    database_url = os.environ.get('DATABASE_URL')
    
    if not database_url:
        print("❌ No DATABASE_URL found, skipping PostgreSQL migration")
        return
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Add missing columns to boards table if they don't exist
        columns_to_add = [
            ("stain", "TEXT"),
            ("finish", "TEXT"),
            ("pegs_included", "TEXT"),
            ("price", "DECIMAL(10,2)")
        ]
        
        for column_name, column_type in columns_to_add:
            try:
                cursor.execute(f"ALTER TABLE boards ADD COLUMN {column_name} {column_type}")
                print(f"✅ Added column '{column_name}' to boards table")
            except Exception as e:
                if "already exists" in str(e).lower():
                    print(f"⚠️  Column '{column_name}' already exists")
                else:
                    print(f"❌ Error adding column '{column_name}': {e}")
        
        conn.commit()
        conn.close()
        print("✅ PostgreSQL database migration completed")
        
    except Exception as e:
        print(f"❌ Error migrating PostgreSQL database: {e}")

if __name__ == "__main__":
    print("🔄 Starting database migration...")
    
    # Check if we're on Railway (PostgreSQL)
    if os.environ.get('DATABASE_URL'):
        print("🚂 Detected Railway environment, migrating PostgreSQL...")
        migrate_postgresql()
    else:
        print("💻 Detected local environment, migrating SQLite...")
        migrate_sqlite()
    
    print("✅ Database migration process completed!")
