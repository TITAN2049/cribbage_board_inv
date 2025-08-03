# Cribbage Board Collection Manager

A comprehensive Flask web application for managing cribbage board collections, player records, and game statistics with photo support.

## Features

- 📋 **Board Management**: Track cribbage boards with detailed information, photos, and collection status
- 👥 **Player Management**: Maintain player profiles with photos and statistics
- 🎮 **Game Tracking**: Record game results, scores, and statistics
- 📊 **Statistics**: View win/loss records, skunk statistics, and performance metrics
- 🖼️ **Photo Support**: Upload and manage photos for players and boards
- ☁️ **Cloud Deployment**: Ready for Railway deployment with PostgreSQL support

## Quick Start

### Option 1: Automated Installation (Windows)
1. Download and run any of the installation scripts in `scripts/windows/`:
   - `ONE_CLICK_INSTALL.bat` - Complete automated setup
   - `PROFESSIONAL_INSTALL.bat` - Professional installation with logging
   - `SIMPLE_INSTALL.bat` - Basic installation

### Option 2: Manual Installation

1. **Clone or download** this repository
2. **Install Python 3.8+** if not already installed
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Initialize the database**:
   ```bash
   python scripts/init_db.py
   ```
5. **Run the application**:
   ```bash
   python scripts/start_app.py
   ```

### Option 3: Direct Flask Run
```bash
cd app
python app.py
```

## Project Structure

```
├── app/                    # Main application
│   ├── app.py             # Flask application (main)
│   ├── static/            # Static files (CSS, JS, uploads)
│   └── templates/         # HTML templates
├── docs/                  # Documentation
├── scripts/               # Utility scripts
│   ├── deployment/        # Deployment scripts
│   ├── setup/            # Setup and installation scripts
│   └── windows/          # Windows batch files
├── requirements.txt       # Python dependencies
├── schema.sql            # Database schema
└── Procfile              # Railway deployment configuration
```

## Key Files

- **`app/app.py`** - Main Flask application with hybrid SQLite/PostgreSQL support
- **`requirements.txt`** - Python package dependencies
- **`schema.sql`** - Database schema for tables and initial data
- **`Procfile`** - Railway deployment configuration

## Deployment

### Railway Deployment
1. Connect your repository to Railway
2. The app will automatically deploy using the configuration in `Procfile`
3. PostgreSQL database will be automatically provisioned and configured

### Local Development
- Uses SQLite database (`app/database.db`)
- Supports hot reloading for development
- Photo uploads stored in `app/static/uploads/`

## Database Schema

- **boards** - Cribbage board information with photos
- **players** - Player profiles with photos and join dates
- **games** - Game records with scores and statistics
- **wood_types** - Board wood type categories
- **material_types** - Board material categories

## Photo Management

- **Player Photos**: Upload and display player profile pictures
- **Board Photos**: Front and back view photos for each board
- **File Handling**: Secure file uploads with unique naming
- **Fallback Support**: Default avatars when no photos are uploaded

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Documentation

See the `docs/` directory for detailed documentation:
- Installation guides
- Deployment instructions
- Windows-specific setup
- Railway deployment guide

## License

This project is open source and available under the MIT License.

## Support

For issues or questions:
1. Check the documentation in the `docs/` folder
2. Run the test scripts in `scripts/` to verify setup
3. Check the installation logs for error details
