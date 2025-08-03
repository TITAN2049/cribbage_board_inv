#!/usr/bin/env python3
import requests

base_url = "http://localhost:5001"

def test_enhanced_leaderboard():
    print("🏆 ENHANCED LEADERBOARD TEST")
    print("=" * 50)
    
    try:
        response = requests.get(f"{base_url}/stats")
        if response.status_code == 200:
            content = response.text.lower()
            
            # Check for enhanced leaderboard features
            checks = [
                ("🏆 Trophy header", "🏆" in content),
                ("Rank styling", "crown" in content),
                ("Win/Loss record", "w</span>" in content and "l</span>" in content),
                ("Progress bars", "bg-gray-200 rounded-full" in content),
                ("Streak indicators", "streak" in content),
                ("Skunk statistics", "skunks given" in content),
                ("Average scores", "avg score" in content),
                ("Recent form", "recent form" in content or "last 10" in content),
                ("Player links", "player_detail" in content),
                ("Legend", "double skunks" in content),
                ("Proper sorting", "ranked by win percentage" in content)
            ]
            
            passed = 0
            total = len(checks)
            
            for check_name, result in checks:
                status = "✅" if result else "❌"
                print(f"{status} {check_name}")
                if result:
                    passed += 1
            
            print(f"\n📊 Leaderboard Enhancement Results:")
            print(f"Features Working: {passed}/{total}")
            print(f"Success Rate: {(passed/total)*100:.1f}%")
            
            if passed == total:
                print("🎉 PERFECT! Enhanced leaderboard is fully functional!")
            elif passed >= total * 0.8:
                print("✅ EXCELLENT! Most enhancements are working.")
            elif passed >= total * 0.6:
                print("⚠️  GOOD. Some features need attention.")
            else:
                print("❌ NEEDS WORK. Significant issues with enhancements.")
        else:
            print(f"❌ Stats page failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing leaderboard: {e}")

if __name__ == "__main__":
    test_enhanced_leaderboard()
