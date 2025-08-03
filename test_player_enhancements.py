#!/usr/bin/env python3
import requests

base_url = "http://localhost:5001"

def comprehensive_player_test():
    print("🚀 COMPREHENSIVE PLAYER ENHANCEMENT TEST")
    print("=" * 60)
    
    results = {
        'enhanced_stats': 0,
        'nemesis_data': 0,
        'favorite_opponent': 0,
        'improved_games': 0,
        'total_tests': 0
    }
    
    # Test players with game history
    test_players = [9, 10, 11, 12]
    
    for player_id in test_players:
        print(f"\n👤 Testing Player {player_id}")
        print("-" * 30)
        
        try:
            response = requests.get(f"{base_url}/player/{player_id}")
            if response.status_code == 200:
                content = response.text.lower()
                
                # Test 1: Enhanced statistics display
                has_advanced_stats = all(stat in content for stat in [
                    'skunks given', 'current streak', 'avg win score', 'total games'
                ])
                if has_advanced_stats:
                    print("✅ Enhanced statistics displayed")
                    results['enhanced_stats'] += 1
                else:
                    print("❌ Enhanced statistics missing")
                results['total_tests'] += 1
                
                # Test 2: Nemesis section
                if 'nemesis' in content and 'lost' in content:
                    print("✅ Nemesis section working")
                    results['nemesis_data'] += 1
                else:
                    print("❌ Nemesis section missing")
                results['total_tests'] += 1
                
                # Test 3: Favorite opponent
                if 'favorite opponent' in content and 'won' in content:
                    print("✅ Favorite opponent section working")
                    results['favorite_opponent'] += 1
                else:
                    print("❌ Favorite opponent section missing")
                results['total_tests'] += 1
                
                # Test 4: Improved game history with opponents
                if 'vs ' in content and ('won' in content or 'lost' in content):
                    print("✅ Game history shows opponents")
                    results['improved_games'] += 1
                else:
                    print("❌ Game history doesn't show opponents properly")
                results['total_tests'] += 1
                
            else:
                print(f"❌ Player page failed: {response.status_code}")
                results['total_tests'] += 4  # Count all missed tests
                
        except Exception as e:
            print(f"❌ Error testing player {player_id}: {e}")
            results['total_tests'] += 4  # Count all missed tests
    
    # Summary
    print(f"\n📊 ENHANCEMENT TEST SUMMARY")
    print("=" * 60)
    print(f"Enhanced Statistics: {results['enhanced_stats']:2d} / {len(test_players)}")
    print(f"Nemesis Data:        {results['nemesis_data']:2d} / {len(test_players)}")
    print(f"Favorite Opponent:   {results['favorite_opponent']:2d} / {len(test_players)}")
    print(f"Improved Games:      {results['improved_games']:2d} / {len(test_players)}")
    print(f"Total Tests Passed:  {sum(results.values())-results['total_tests']:2d} / {results['total_tests']}")
    
    success_rate = ((sum(results.values())-results['total_tests']) / results['total_tests']) * 100
    print(f"\nSuccess Rate: {success_rate:.1f}%")
    
    if success_rate >= 90:
        print("🎉 EXCELLENT! Player enhancements are working perfectly!")
    elif success_rate >= 75:
        print("✅ GREAT! Most player enhancements are functional.")
    elif success_rate >= 50:
        print("⚠️  GOOD. Some player enhancements need work.")
    else:
        print("❌ NEEDS WORK. Significant issues with player enhancements.")

if __name__ == "__main__":
    comprehensive_player_test()
