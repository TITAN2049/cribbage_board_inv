#!/usr/bin/env python3
import requests

base_url = "http://localhost:5001"

def debug_stats_page():
    print("🔍 Debugging Stats Page Template")
    print("=" * 40)
    
    try:
        response = requests.get(f"{base_url}/stats")
        if response.status_code == 200:
            lines = response.text.split('\n')
            
            # Look for debug comments
            debug_lines = [line for line in lines if 'DEBUG' in line]
            print(f"Found {len(debug_lines)} debug lines:")
            for line in debug_lines:
                print(f"  {line.strip()}")
            
            # Look for any rivalries section
            rivalry_lines = []
            in_rivalries = False
            for i, line in enumerate(lines):
                if 'Player Rivalries' in line:
                    in_rivalries = True
                    print(f"\n📍 Found 'Player Rivalries' at line {i+1}")
                    # Show context around this line
                    start = max(0, i-3)
                    end = min(len(lines), i+10)
                    for j in range(start, end):
                        marker = ">>>" if j == i else "   "
                        print(f"{marker} {j+1:3d}: {lines[j].rstrip()}")
                    break
            
            if not in_rivalries:
                print("❌ 'Player Rivalries' section not found at all")
                
        else:
            print(f"❌ Stats page returned {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_stats_page()
