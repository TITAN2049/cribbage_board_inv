#!/usr/bin/env python3
"""
Database Migration Script - Add Photo Support to Players
This script safely adds the photo column to existing player tables
"""

import os
import sqlite3
from pathlib import Path

def migrate_sqlite_database():
    """Add photo column to SQLite database"""
    base_dir = Path(__file__).parent
    
    # Check data directory first
    data_dir = base_dir / "data"
    db_path = data_dir / "database.db"
    
    # Fallback to app directory
    if not db_path.exists():
        app_dir = base_dir / "app"
        db_path = app_dir / "database.db"
    
    if not db_path.exists():
        print("❌ No database found to migrate")
        return False
    
    print(f"🔄 Migrating database: {db_path}")
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Check if photo column already exists
        cursor.execute("PRAGMA table_info(players)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'photo' in columns:
            print("✅ Photo column already exists in players table")
        else:
            # Add photo column
            cursor.execute("ALTER TABLE players ADD COLUMN photo TEXT")
            print("✅ Added photo column to players table")
        
        # Check if date_added column exists
        if 'date_added' not in columns:
            cursor.execute("ALTER TABLE players ADD COLUMN date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
            print("✅ Added date_added column to players table")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✅ Database migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

def migrate_postgresql_database():
    """Add photo column to PostgreSQL database (Railway)"""
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("⚠️  No PostgreSQL DATABASE_URL found")
        return False
    
    try:
        import psycopg2
        print("🔄 Migrating PostgreSQL database...")
        
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Check if photo column exists
        cursor.execute("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'players' AND column_name = 'photo'
        """)
        
        if cursor.fetchone():
            print("✅ Photo column already exists in players table")
        else:
            # Add photo column
            cursor.execute("ALTER TABLE players ADD COLUMN photo VARCHAR(255)")
            conn.commit()
            print("✅ Added photo column to players table")
        
        cursor.close()
        conn.close()
        
        print("✅ PostgreSQL migration completed successfully!")
        return True
        
    except ImportError:
        print("⚠️  psycopg2 not available for PostgreSQL migration")
        return False
    except Exception as e:
        print(f"❌ PostgreSQL migration failed: {e}")
        return False

def main():
    """Run database migration"""
    print("🔄 Starting database migration for player photos...")
    print("")
    
    # Try PostgreSQL first (Railway)
    postgresql_success = migrate_postgresql_database()
    
    # Try SQLite (local)
    sqlite_success = migrate_sqlite_database()
    
    if postgresql_success or sqlite_success:
        print("")
        print("🎉 Migration completed!")
        print("Players can now have photos!")
    else:
        print("")
        print("❌ Migration failed - no databases were updated")

if __name__ == "__main__":
    main()
