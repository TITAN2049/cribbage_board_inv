#!/usr/bin/env python3
"""
Data Backup System for Cribbage Board Collection
Creates backups of database and uploaded images before code updates
"""

import os
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path

def create_backup():
    """Create a complete backup of all user data"""
    print("🔄 Creating backup of your cribbage board data...")
    
    # Get current directory
    base_dir = Path(__file__).parent
    
    # Create backup directory with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = base_dir / "data_backups" / f"backup_{timestamp}"
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    success = True
    
    # Backup database
    db_paths_to_check = [
        base_dir / "app" / "database.db",  # Current location
        base_dir / "data" / "database.db",  # New location
        base_dir / "database.db"  # Alternative location
    ]
    
    database_backed_up = False
    for db_path in db_paths_to_check:
        if db_path.exists():
            try:
                backup_db_path = backup_dir / "database.db"
                shutil.copy2(str(db_path), str(backup_db_path))
                print(f"✅ Database backed up from: {db_path}")
                database_backed_up = True
                break
            except Exception as e:
                print(f"❌ Failed to backup database from {db_path}: {e}")
                success = False
    
    if not database_backed_up:
        print("⚠️  No database found to backup")
    
    # Backup uploaded images
    upload_paths_to_check = [
        base_dir / "app" / "static" / "uploads",  # Current location
        base_dir / "data" / "uploads",  # New location
    ]
    
    images_backed_up = False
    for upload_path in upload_paths_to_check:
        if upload_path.exists():
            try:
                backup_uploads_path = backup_dir / "uploads"
                shutil.copytree(str(upload_path), str(backup_uploads_path), dirs_exist_ok=True)
                image_count = len(list(backup_uploads_path.glob("*")))
                print(f"✅ {image_count} images backed up from: {upload_path}")
                images_backed_up = True
                break
            except Exception as e:
                print(f"❌ Failed to backup images from {upload_path}: {e}")
                success = False
    
    if not images_backed_up:
        print("⚠️  No images found to backup")
    
    # Create backup info file
    info_file = backup_dir / "backup_info.txt"
    with open(info_file, 'w') as f:
        f.write(f"Cribbage Board Collection Data Backup\n")
        f.write(f"Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Backup Location: {backup_dir}\n")
        f.write(f"Database Backed Up: {database_backed_up}\n")
        f.write(f"Images Backed Up: {images_backed_up}\n")
        f.write(f"Includes: Board images, Player photos, Game records, Player data\n")
    
    if success:
        print(f"✅ Backup completed successfully!")
        print(f"📁 Backup saved to: {backup_dir}")
        return str(backup_dir)
    else:
        print("❌ Backup completed with some errors")
        return None

def list_backups():
    """List all available backups"""
    base_dir = Path(__file__).parent
    backup_root = base_dir / "data_backups"
    
    if not backup_root.exists():
        print("No backups found.")
        return []
    
    backups = []
    for backup_dir in sorted(backup_root.glob("backup_*"), reverse=True):
        if backup_dir.is_dir():
            info_file = backup_dir / "backup_info.txt"
            if info_file.exists():
                with open(info_file, 'r') as f:
                    info = f.read()
                backups.append((str(backup_dir), info))
            else:
                backups.append((str(backup_dir), "No info available"))
    
    print(f"📋 Found {len(backups)} backup(s):")
    for i, (path, info) in enumerate(backups, 1):
        print(f"\n{i}. {Path(path).name}")
        print(f"   {info.split('Created: ')[1].split('Backup Location:')[0].strip() if 'Created: ' in info else 'Unknown date'}")
    
    return backups

def restore_backup(backup_path):
    """Restore data from a backup"""
    backup_dir = Path(backup_path)
    if not backup_dir.exists():
        print(f"❌ Backup directory not found: {backup_path}")
        return False
    
    print(f"🔄 Restoring backup from: {backup_dir.name}")
    
    base_dir = Path(__file__).parent
    success = True
    
    # Ensure data directory exists
    data_dir = base_dir / "data"
    data_dir.mkdir(exist_ok=True)
    (data_dir / "uploads").mkdir(exist_ok=True)
    
    # Restore database
    backup_db = backup_dir / "database.db"
    if backup_db.exists():
        try:
            target_db = data_dir / "database.db"
            shutil.copy2(str(backup_db), str(target_db))
            print("✅ Database restored")
        except Exception as e:
            print(f"❌ Failed to restore database: {e}")
            success = False
    
    # Restore images
    backup_uploads = backup_dir / "uploads"
    if backup_uploads.exists():
        try:
            target_uploads = data_dir / "uploads"
            if target_uploads.exists():
                shutil.rmtree(str(target_uploads))
            shutil.copytree(str(backup_uploads), str(target_uploads))
            image_count = len(list(target_uploads.glob("*")))
            print(f"✅ {image_count} images restored")
        except Exception as e:
            print(f"❌ Failed to restore images: {e}")
            success = False
    
    if success:
        print("✅ Backup restored successfully!")
        return True
    else:
        print("❌ Backup restoration completed with errors")
        return False

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "list":
        list_backups()
    elif len(sys.argv) > 1 and sys.argv[1] == "restore":
        if len(sys.argv) > 2:
            restore_backup(sys.argv[2])
        else:
            backups = list_backups()
            if backups:
                try:
                    choice = int(input("\nEnter backup number to restore: ")) - 1
                    if 0 <= choice < len(backups):
                        restore_backup(backups[choice][0])
                    else:
                        print("Invalid selection")
                except ValueError:
                    print("Invalid input")
    else:
        create_backup()
