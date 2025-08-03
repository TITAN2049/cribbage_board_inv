#!/usr/bin/env python3
"""
Route Verification Script
Tests that all required routes exist in the Flask app
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from app.app_hybrid import app
    print("✅ Successfully imported hybrid app")
    
    # Check available routes
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append({
            'endpoint': rule.endpoint,
            'methods': list(rule.methods),
            'path': rule.rule
        })
    
    print(f"\n📋 Found {len(routes)} routes:")
    for route in sorted(routes, key=lambda x: x['endpoint']):
        print(f"  {route['endpoint']:<20} {route['methods']:<30} {route['path']}")
    
    # Check specifically for player routes
    player_routes = [r for r in routes if 'player' in r['endpoint']]
    print(f"\n👥 Player routes ({len(player_routes)}):")
    for route in player_routes:
        print(f"  ✅ {route['endpoint']:<20} {route['path']}")
        
    # Check for missing routes
    required_routes = ['players', 'player_detail', 'edit_player', 'add_player', 'delete_player']
    missing_routes = []
    
    for required in required_routes:
        if not any(r['endpoint'] == required for r in routes):
            missing_routes.append(required)
    
    if missing_routes:
        print(f"\n❌ Missing routes:")
        for missing in missing_routes:
            print(f"  - {missing}")
    else:
        print(f"\n✅ All required player routes are present!")
        
except ImportError as e:
    print(f"❌ Failed to import hybrid app: {e}")
    print("Trying to import old app...")
    try:
        from app.app import app
        print("⚠️  Using old app.py - this might be the problem!")
    except ImportError as e2:
        print(f"❌ Failed to import old app too: {e2}")
except Exception as e:
    print(f"❌ Error checking routes: {e}")
    import traceback
    traceback.print_exc()
