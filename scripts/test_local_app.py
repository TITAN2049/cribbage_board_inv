#!/usr/bin/env python3
"""
Local Test Script for Player Photos
Tests the hybrid app with all photo features
"""

import os
import sys

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("🧪 Testing Cribbage Board Collection with Player Photos")
print("=" * 60)

try:
    # Import the hybrid app
    from app.app_hybrid import app
    print("✅ Successfully imported hybrid app")
    
    # Set local development configuration
    app.config.update({
        'DEBUG': True,
        'TESTING': False,
        'ENV': 'development'
    })
    
    # Check routes
    routes = list(app.url_map.iter_rules())
    player_routes = [r for r in routes if 'player' in r.endpoint]
    
    print(f"✅ Found {len(routes)} total routes")
    print(f"✅ Found {len(player_routes)} player routes")
    
    # List player routes
    print("\n👥 Player routes:")
    for route in player_routes:
        print(f"  • {route.endpoint:<20} {route.rule}")
    
    print("\n🚀 Starting local development server...")
    print("📱 Open your browser to: http://127.0.0.1:5000")
    print("✨ Player photo features are enabled!")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 60)
    
    # Start the app
    app.run(host='127.0.0.1', port=5000, debug=True)
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("\nTrying to diagnose the issue...")
    
    # Check if files exist
    import os
    files_to_check = [
        'app/app_hybrid.py',
        'app/app.py',
        'app/__init__.py'
    ]
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"✅ Found: {file_path}")
        else:
            print(f"❌ Missing: {file_path}")
            
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
