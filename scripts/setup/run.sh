#!/bin/bash

echo "🚀 Starting Cribbage Board Collection app..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run ./setup.sh first."
    exit 1
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Check if database exists
if [ ! -f app/database.db ]; then
    echo "🗄️ Database not found. Creating from schema..."
    sqlite3 app/database.db < schema.sql
    echo "✅ Database created"
fi

# Set Flask app
export FLASK_APP=app/app.py

# Function to try different ports
try_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
        return 1  # Port is in use
    else
        return 0  # Port is available
    fi
}

# Try to find an available port
PORT=5000
if ! try_port $PORT; then
    echo "⚠️ Port $PORT is in use (likely by AirPlay Receiver)"
    PORT=5001
    if ! try_port $PORT; then
        echo "⚠️ Port $PORT is also in use, trying 5002..."
        PORT=5002
        if ! try_port $PORT; then
            echo "❌ Ports 5000-5002 are all in use. Please free up a port or specify one manually."
            echo "💡 On macOS, you can disable AirPlay Receiver in System Preferences > General > AirDrop & Handoff"
            exit 1
        fi
    fi
fi

echo "🌐 Starting server on port $PORT..."
echo "📱 Open your browser to: http://localhost:$PORT"
echo "⏹️  Press Ctrl+C to stop the server"
echo ""

# Start Flask app
python -m flask run --port=$PORT
