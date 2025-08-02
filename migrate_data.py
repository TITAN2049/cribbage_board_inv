#!/usr/bin/env python3
"""
Data Migration Script - Moves database and images to separate data directory
This ensures your data survives code updates
"""

import os
import shutil
import sqlite3
from pathlib import Path

def migrate_data():
    """Move database and images to data directory"""
    print("🔄 Migrating your data to a safe location...")
    
    base_dir = Path(__file__).parent
    
    # Create data directory structure
    data_dir = base_dir / "data"
    data_dir.mkdir(exist_ok=True)
    (data_dir / "uploads").mkdir(exist_ok=True)
    
    success = True
    
    # Move database
    old_db_path = base_dir / "app" / "database.db"
    new_db_path = data_dir / "database.db"
    
    if old_db_path.exists() and not new_db_path.exists():
        try:
            shutil.move(str(old_db_path), str(new_db_path))
            print("✅ Database moved to data directory")
        except Exception as e:
            print(f"❌ Failed to move database: {e}")
            success = False
    elif new_db_path.exists():
        print("✅ Database already in data directory")
    else:
        print("⚠️  No database found to migrate")
    
    # Move uploaded images
    old_uploads_path = base_dir / "app" / "static" / "uploads"
    new_uploads_path = data_dir / "uploads"
    
    if old_uploads_path.exists():
        try:
            # Copy all files from old to new location
            for file_path in old_uploads_path.glob("*"):
                if file_path.is_file():
                    target_path = new_uploads_path / file_path.name
                    if not target_path.exists():
                        shutil.copy2(str(file_path), str(target_path))
            
            # Count migrated files
            image_count = len(list(new_uploads_path.glob("*")))
            print(f"✅ {image_count} images migrated to data directory")
            
            # Clean up old uploads (but keep directory for app compatibility)
            for file_path in old_uploads_path.glob("*"):
                if file_path.is_file():
                    file_path.unlink()
            
        except Exception as e:
            print(f"❌ Failed to migrate images: {e}")
            success = False
    else:
        print("⚠️  No images found to migrate")
    
    # Create symlink or copy for app compatibility
    try:
        # Ensure the app's upload directory exists but is empty
        old_uploads_path.mkdir(exist_ok=True)
        print("✅ Maintained app directory structure")
    except Exception as e:
        print(f"⚠️  Could not maintain app directory: {e}")
    
    if success:
        print("✅ Data migration completed successfully!")
        print(f"📁 Your data is now safely stored in: {data_dir}")
        print("🔒 This directory will not be affected by code updates")
    else:
        print("❌ Data migration completed with some issues")
    
    return success

if __name__ == "__main__":
    migrate_data()
