#!/usr/bin/env python3
"""
Database Configuration for Cribbage Board Collection
Supports both PostgreSQL (Railway) and SQLite (local development)
"""

import os
import sqlite3
import psycopg2
from contextlib import contextmanager

class DatabaseManager:
    def __init__(self):
        self.database_url = os.environ.get('DATABASE_URL')
        self.is_postgresql = bool(self.database_url)
        
    @contextmanager
    def get_db_connection(self):
        """Get database connection with proper context management"""
        if self.is_postgresql:
            conn = psycopg2.connect(self.database_url)
            try:
                yield conn
            finally:
                conn.close()
        else:
            # SQLite fallback for local development
            from pathlib import Path
            base_dir = Path(__file__).parent.parent
            data_dir = base_dir / "data"
            db_path = data_dir / "database.db"
            
            # Fallback to app directory if data directory doesn't exist
            if not db_path.exists():
                app_dir = base_dir / "app"
                db_path = app_dir / "database.db"
            
            conn = sqlite3.connect(str(db_path))
            conn.row_factory = sqlite3.Row
            try:
                yield conn
            finally:
                conn.close()
    
    def execute_query(self, query, params=None, fetch=False):
        """Execute a query with proper parameter handling for both databases"""
        if params is None:
            params = []
        
        # Convert SQLite-style parameters to PostgreSQL if needed
        if self.is_postgresql and '?' in query:
            # Convert ? placeholders to $1, $2, etc. for PostgreSQL
            count = query.count('?')
            for i in range(count, 0, -1):
                query = query.replace('?', f'${i}', 1)
        
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            
            if fetch:
                if self.is_postgresql:
                    # Convert PostgreSQL results to dict-like objects
                    columns = [desc[0] for desc in cursor.description] if cursor.description else []
                    rows = cursor.fetchall()
                    result = [dict(zip(columns, row)) for row in rows]
                else:
                    result = cursor.fetchall()
                cursor.close()
                return result
            else:
                conn.commit()
                cursor.close()
    
    def get_last_insert_id(self, cursor):
        """Get the last inserted row ID (database-specific)"""
        if self.is_postgresql:
            cursor.execute("SELECT LASTVAL()")
            return cursor.fetchone()[0]
        else:
            return cursor.lastrowid

# Global database manager instance
db_manager = DatabaseManager()
