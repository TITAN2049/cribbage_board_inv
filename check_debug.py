#!/usr/bin/env python3
import requests

base_url = "http://localhost:5001"

def check_debug_info():
    print("🔍 Checking for Debug Information")
    print("=" * 40)
    
    try:
        response = requests.get(f"{base_url}/stats")
        if response.status_code == 200:
            # Look for debug comment
            if "DEBUG:" in response.text:
                print("✅ Found DEBUG comment")
                # Extract debug line
                lines = response.text.split('\n')
                for line in lines:
                    if "DEBUG:" in line:
                        print(f"   {line.strip()}")
            else:
                print("❌ No DEBUG comment found")
                
            # Also look for "Player Rivalries" text literally
            if "Player Rivalries" in response.text:
                print("✅ Found 'Player Rivalries' text")
            else:
                print("❌ 'Player Rivalries' text not found")
                
            # Look for "Nemesis" 
            if "Nemesis" in response.text:
                print("✅ Found 'Nemesis' text")
            else:
                print("❌ 'Nemesis' text not found")
                
        else:
            print(f"❌ Stats page returned {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_debug_info()
