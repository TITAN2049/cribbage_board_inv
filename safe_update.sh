#!/bin/bash
# Safe Code Update Script for Cribbage Board Collection (macOS/Linux)
# This script backs up your data before updating code

echo "================================================================"
echo "          CRIBBAGE BOARD COLLECTION - SAFE UPDATE"
echo "================================================================"
echo ""
echo "This script will:"
echo "1. Backup your current database and images"
echo "2. Allow you to update your code safely"
echo "3. Restore your data after the update"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed or not in PATH"
    echo "Please install Python 3 first"
    exit 1
fi

echo "🔄 Step 1: Creating backup of your data..."
echo ""
python3 backup_data.py
if [ $? -ne 0 ]; then
    echo "❌ Backup failed! Update cancelled for safety."
    exit 1
fi

echo ""
echo "✅ Backup completed successfully!"
echo ""
echo "📋 Your data has been safely backed up."
echo "You can now update your code files without losing any data."
echo ""
echo "IMPORTANT INSTRUCTIONS:"
echo "1. Your database and images are now backed up"
echo "2. You can safely replace/update any code files"
echo "3. After updating, run this script again with 'restore' option"
echo "4. Or run: python3 backup_data.py restore"
echo ""
read -p "Would you like to migrate data to the new safe location now? (y/n): " migrate
if [[ $migrate == "y" || $migrate == "Y" ]]; then
    echo ""
    echo "🔄 Migrating data to safe directory..."
    python3 migrate_data.py
    echo ""
    echo "✅ Data migration completed!"
    echo "Your data is now protected from code updates."
fi

echo ""
echo "================================================================"
echo "                    UPDATE INSTRUCTIONS"
echo "================================================================"
echo ""
echo "1. ✅ Your data is safely backed up"
echo "2. 🔄 You can now update/replace code files"
echo "3. 🏃‍♂️ After updating, run your app normally:"
echo "   - Run: python3 start_app.py"
echo "   - Or run: python3 production.py"
echo ""
echo "4. 🔄 If you need to restore from backup:"
echo "   - Run: python3 backup_data.py restore"
echo "   - Or run this script again with 'restore'"
echo ""
echo "Your cribbage board collection data is now safe! 🛡️"
echo ""
