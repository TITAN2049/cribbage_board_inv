# Cribbage Board Collection - Windows Installation Guide

## 🎯 Quick Start (Automatic Installation)

### Prerequisites
1. **Python 3.8 or later** must be installed
   - Download from: https://www.python.org/downloads/
   - ⚠️ **IMPORTANT**: During installation, check "Add Python to PATH"

### Installation Steps

1. **Download** this folder to your Windows computer
2. **Double-click** `windows_setup.bat` to install everything automatically
3. **Double-click** `windows_run.bat` to start the application
4. **Open your browser** to `http://localhost:5000`

That's it! The application should now be running.

---

## 📋 What the Installer Does

The `windows_setup.bat` script automatically:
- ✅ Checks if Python is installed
- ✅ Creates a virtual environment
- ✅ Installs all required packages
- ✅ Sets up the database
- ✅ Creates necessary directories

---

## 🚀 Running the Application

After setup, always use `windows_run.bat` to start the application:

1. Double-click `windows_run.bat`
2. Wait for "Server Information" message
3. Open your browser to `http://localhost:5000`
4. Press `Ctrl+C` in the command window to stop

---

## 🔧 Manual Installation (Advanced Users)

If the automatic installer doesn't work:

```cmd
# 1. Create virtual environment
python -m venv venv

# 2. Activate virtual environment
venv\Scripts\activate.bat

# 3. Install requirements
pip install -r requirements.txt

# 4. Create database
sqlite3 app\database.db < schema.sql

# 5. Run application
set FLASK_APP=app\app.py
python -m flask run --port=5000
```

---

## 📁 Application Features

### 🏠 **Board Collection Management**
- Add new cribbage boards with photos
- Track board details (wood type, date made, etc.)
- Mark boards as gifts with gift information
- Filter boards by collection status

### 👥 **Player Management**
- Add and manage players
- Advanced statistics with win/loss records
- Nemesis and favorite opponent tracking
- Player deletion with game constraints

### 🎮 **Game Tracking**
- Record games with skunk tracking
- View game history by board
- Delete individual games
- Comprehensive game statistics

### 🎨 **Modern Interface**
- Clean, responsive design
- Easy navigation with back buttons
- Flash messaging for user feedback
- Mobile-friendly layout

---

## 🛠️ Troubleshooting

### Python Not Found
- Reinstall Python from https://python.org
- Make sure to check "Add Python to PATH"
- Restart your computer after installation

### Database Errors
- Make sure SQLite3 is available (usually comes with Python)
- Try deleting `app\database.db` and running setup again

### Port Already in Use
- The app will try port 5000, then 5001, then 5002
- Close other applications using these ports

### Permission Errors
- Run Command Prompt as Administrator
- Make sure the folder isn't in a protected location

---

## 📞 Support

If you encounter issues:

1. **Check the Prerequisites** - Ensure Python is properly installed
2. **Run as Administrator** - Try running the batch files as administrator
3. **Check File Permissions** - Make sure the folder isn't read-only
4. **Antivirus Software** - Some antivirus programs block batch files

---

## 🔒 Security Notes

- This application runs locally on your computer
- No data is sent to external servers
- All board photos are stored locally in `app\static\uploads`
- Database is stored locally in `app\database.db`

---

## 📦 Files Included

- `windows_setup.bat` - Automatic installer
- `windows_run.bat` - Application launcher
- `requirements.txt` - Python package requirements
- `schema.sql` - Database structure
- `app/` - Application files
  - `app.py` - Main application
  - `templates/` - Web page templates
  - `static/` - CSS, images, uploads

---

## 🆕 Version Information

This version includes:
- ✅ Complete board collection management
- ✅ Advanced player statistics
- ✅ Game tracking with skunk detection
- ✅ Modern, responsive web interface
- ✅ Duplicate prevention
- ✅ Data export capabilities
- ✅ Comprehensive error handling

---

*Enjoy managing your cribbage board collection!* 🎯
