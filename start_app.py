#!/usr/bin/env python3
"""
Start the Cribbage Board Collection Flask App
"""

import os
import sys

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

# Import and run the app
from app import app

if __name__ == "__main__":
    print("🎮 Starting Cribbage Board Collection App")
    print("🌐 Server will be available at: http://localhost:5001")
    
    # Run the app
    app.run(host="0.0.0.0", port=5001, debug=True)
