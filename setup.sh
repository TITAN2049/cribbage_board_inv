#!/bin/bash

echo "🔧 Setting up Cribbage Board Collection environment..."

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed. Please install Python 3."
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install required packages
echo "📥 Installing required packages..."
pip install --upgrade pip
pip install flask requests

# Update requirements.txt
echo "📝 Updating requirements.txt..."
pip freeze > requirements.txt

# Create uploads directory if it doesn't exist
echo "📁 Creating uploads directory..."
mkdir -p app/static/uploads

# Initialize database if it doesn't exist
if [ ! -f app/database.db ]; then
  echo "🗄️ Creating new database from schema..."
  sqlite3 app/database.db < schema.sql
  echo "✅ Database created successfully"
else
  echo "ℹ️ Database already exists"
fi

# Make scripts executable
echo "🔐 Making scripts executable..."
chmod +x run.sh
chmod +x simple_test.py
chmod +x test_cribbage_app.py

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Run the app: ./run.sh"
echo "  2. Open browser: http://localhost:5000"
echo "  3. Run tests: ./simple_test.py or ./test_cribbage_app.py"
echo ""
