#!/usr/bin/env python3
import requests

base_url = "http://localhost:5001"

def test_player_detail():
    print("🔍 Testing Enhanced Player Detail Page")
    print("=" * 50)
    
    # Test with a few different player IDs
    for player_id in [1, 10, 17]:
        try:
            response = requests.get(f"{base_url}/player/{player_id}")
            if response.status_code == 200:
                print(f"✅ Player {player_id}: Page loads successfully")
                
                # Check for key content
                content = response.text.lower()
                if "nemesis" in content:
                    print(f"   ✅ Nemesis section found")
                else:
                    print(f"   ❌ Nemesis section missing")
                
                if "favorite opponent" in content:
                    print(f"   ✅ Favorite opponent section found")
                else:
                    print(f"   ❌ Favorite opponent section missing")
                
                if "current streak" in content:
                    print(f"   ✅ Current streak found")
                else:
                    print(f"   ❌ Current streak missing")
                
                if "skunks given" in content:
                    print(f"   ✅ Skunk statistics found")
                else:
                    print(f"   ❌ Skunk statistics missing")
                    
            else:
                print(f"❌ Player {player_id}: Failed with status {response.status_code}")
                
        except Exception as e:
            print(f"❌ Player {player_id}: Error - {e}")
        
        print()

if __name__ == "__main__":
    test_player_detail()
