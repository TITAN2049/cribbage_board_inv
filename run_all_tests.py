#!/usr/bin/env python3
"""
Run All Tests for Cribbage Board Collection App
"""

import os
import sys
import subprocess
import time
import requests
import signal

def check_flask_app():
    """Check if Flask app is running"""
    try:
        response = requests.get("http://localhost:5000/", timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def start_flask_app():
    """Start the Flask app in background"""
    print("🚀 Starting Flask app...")
    
    # Start the app
    process = subprocess.Popen(
        [sys.executable, "start_app.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=os.getcwd()
    )
    
    # Wait for app to start
    for i in range(10):  # Wait up to 10 seconds
        time.sleep(1)
        if check_flask_app():
            print("✅ Flask app started successfully")
            return process
        print(f"   Waiting for app to start... ({i+1}/10)")
    
    print("❌ Failed to start Flask app")
    process.terminate()
    return None

def run_unit_tests():
    """Run unit tests"""
    print("\n" + "="*60)
    print("🧪 RUNNING UNIT TESTS")
    print("="*60)
    
    try:
        result = subprocess.run([sys.executable, "test_unit.py"], 
                              capture_output=True, text=True)
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running unit tests: {e}")
        return False

def run_comprehensive_tests():
    """Run comprehensive integration tests"""
    print("\n" + "="*60)
    print("🎯 RUNNING COMPREHENSIVE TESTS")
    print("="*60)
    
    try:
        result = subprocess.run([sys.executable, "test_comprehensive.py"], 
                              capture_output=True, text=True)
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running comprehensive tests: {e}")
        return False

def install_requirements():
    """Install required packages for testing"""
    print("📦 Installing test requirements...")
    
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "requests"], 
                      check=True, capture_output=True)
        print("✅ Test requirements installed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        return False

def main():
    """Main test runner"""
    print("🎮 CRIBBAGE BOARD COLLECTION - TEST SUITE")
    print("="*60)
    
    # Install requirements
    if not install_requirements():
        return False
    
    # Check if app is already running
    app_process = None
    if check_flask_app():
        print("✅ Flask app is already running")
    else:
        app_process = start_flask_app()
        if not app_process:
            print("❌ Cannot proceed without Flask app")
            return False
    
    try:
        # Run unit tests first
        unit_success = run_unit_tests()
        
        # Run comprehensive tests
        comprehensive_success = run_comprehensive_tests()
        
        # Final summary
        print("\n" + "="*60)
        print("🏆 FINAL TEST SUMMARY")
        print("="*60)
        print(f"Unit Tests: {'✅ PASSED' if unit_success else '❌ FAILED'}")
        print(f"Comprehensive Tests: {'✅ PASSED' if comprehensive_success else '❌ FAILED'}")
        
        overall_success = unit_success and comprehensive_success
        print(f"\nOverall Result: {'🎉 ALL TESTS PASSED' if overall_success else '❌ SOME TESTS FAILED'}")
        
        return overall_success
        
    finally:
        # Clean up - stop the Flask app if we started it
        if app_process:
            print("\n🛑 Stopping Flask app...")
            app_process.terminate()
            app_process.wait()
            print("✅ Flask app stopped")

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
