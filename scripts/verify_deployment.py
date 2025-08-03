#!/usr/bin/env python3
"""
Deployment Verification and Fix Script
Ensures the correct app version is deployed
"""

import os
import subprocess
import sys
from pathlib import Path

def check_git_status():
    """Check if changes are committed"""
    try:
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True, check=True)
        if result.stdout.strip():
            print("⚠️ You have uncommitted changes:")
            print(result.stdout)
            return False
        else:
            print("✅ All changes are committed")
            return True
    except subprocess.CalledProcessError:
        print("❌ Git status check failed")
        return False

def check_files():
    """Check that required files exist and are correct"""
    files_to_check = {
        'app/app_hybrid.py': 'Hybrid Flask app with photo support',
        'app/templates/players.html': 'Updated players template',
        'app/templates/player_detail.html': 'Player detail template',
        'app/templates/edit_player.html': 'Edit player template',
        'railway_production.py': 'Railway production script',
        'Procfile': 'Railway deployment config',
        'requirements.txt': 'Python dependencies'
    }
    
    print("🔍 Checking required files...")
    all_good = True
    
    for file_path, description in files_to_check.items():
        if Path(file_path).exists():
            print(f"✅ {description}: {file_path}")
        else:
            print(f"❌ Missing {description}: {file_path}")
            all_good = False
    
    return all_good

def check_procfile():
    """Verify Procfile is correct"""
    procfile_path = Path('Procfile')
    if procfile_path.exists():
        content = procfile_path.read_text().strip()
        if 'railway_production.py' in content:
            print("✅ Procfile is correctly configured for Railway")
            return True
        else:
            print("❌ Procfile is not configured correctly")
            print(f"Current content: {content}")
            return False
    else:
        print("❌ Procfile is missing")
        return False

def check_hybrid_app():
    """Verify hybrid app has required routes"""
    try:
        sys.path.append(str(Path.cwd()))
        from app.app_hybrid import app
        
        routes = [rule.endpoint for rule in app.url_map.iter_rules()]
        required_routes = ['players', 'player_detail', 'edit_player', 'add_player', 'delete_player']
        
        missing = [route for route in required_routes if route not in routes]
        
        if missing:
            print(f"❌ Hybrid app is missing routes: {missing}")
            return False
        else:
            print("✅ Hybrid app has all required player routes")
            return True
            
    except Exception as e:
        print(f"❌ Error checking hybrid app: {e}")
        return False

def main():
    """Main verification process"""
    print("🔧 DEPLOYMENT VERIFICATION AND FIX")
    print("=" * 50)
    
    # Check current directory
    if not Path('app').exists():
        print("❌ Not in the correct directory - no 'app' folder found")
        return
    
    print("📁 Current directory looks correct")
    
    # Run checks
    checks = [
        ("Files", check_files),
        ("Procfile", check_procfile), 
        ("Hybrid App", check_hybrid_app),
        ("Git Status", check_git_status)
    ]
    
    all_passed = True
    for check_name, check_func in checks:
        print(f"\n🔍 Checking {check_name}...")
        if not check_func():
            all_passed = False
    
    print("\n" + "=" * 50)
    
    if all_passed:
        print("✅ ALL CHECKS PASSED!")
        print("\n🚀 Your code is ready for deployment!")
        print("\nNext steps:")
        print("1. If using Railway CLI: Run 'railway up'")
        print("2. If using GitHub: Push to your main branch")
        print("3. Railway will automatically deploy the updated code")
        print("\n🎉 After deployment, player photos will work!")
        
    else:
        print("❌ SOME CHECKS FAILED!")
        print("\n🛠️ Issues found - please fix them before deploying")
        print("\nCommon fixes:")
        print("1. Run: git add . && git commit -m 'Add player photo support'")
        print("2. Make sure all files exist as listed above")
        print("3. Check that app_hybrid.py is working correctly")

if __name__ == "__main__":
    main()
