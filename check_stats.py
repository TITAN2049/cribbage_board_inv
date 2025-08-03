#!/usr/bin/env python3
import requests

base_url = "http://localhost:5001"

def check_stats_content():
    print("🔍 Checking Stats Page Content")
    print("=" * 40)
    
    try:
        response = requests.get(f"{base_url}/stats")
        if response.status_code == 200:
            content = response.text.lower()
            
            # Check for nemesis content
            print("Nemesis-related content:")
            if "nemesis" in content:
                print("✅ 'nemesis' found in page")
                # Find nemesis section
                lines = response.text.split('\n')
                nemesis_lines = [line.strip() for line in lines if 'nemesis' in line.lower()]
                for line in nemesis_lines[:3]:  # Show first 3 matches
                    print(f"   - {line}")
            else:
                print("❌ 'nemesis' NOT found in page")
            
            # Check for rivalry content
            if "rivalries" in content:
                print("✅ 'rivalries' found in page")
            else:
                print("❌ 'rivalries' NOT found in page")
                
            # Check if we have player data
            if "player leaderboard" in content:
                print("✅ Player leaderboard section found")
            else:
                print("❌ Player leaderboard section NOT found")
                
            # Check overall content length
            print(f"📊 Total page length: {len(response.text)} characters")
            
        else:
            print(f"❌ Stats page returned {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_stats_content()
