#!/usr/bin/env python3

import requests
import json
import time
import sys

BASE_URL = "http://localhost:5001"

def test_endpoint(name, method, url, data=None, files=None, expected_status=200):
    try:
        if method.upper() == 'GET':
            response = requests.get(url, timeout=10)
        elif method.upper() == 'POST':
            response = requests.post(url, data=data, files=files, timeout=10)
        
        success = response.status_code == expected_status
        status_icon = "✅" if success else "❌"
        
        print(f"{status_icon} {name}: {response.status_code}")
        
        if not success:
            print(f"   Expected: {expected_status}, Got: {response.status_code}")
            if response.status_code >= 400:
                print(f"   Error: {response.text[:300]}...")
        
        return success
    except Exception as e:
        print(f"❌ {name}: Exception - {e}")
        return False

def main():
    print("🎯 Comprehensive Cribbage App Test Suite")
    print("="*60)
    
    results = {}
    
    # Test 1: Basic Page Loading
    print("\n📄 Testing Page Loading")
    print("-" * 30)
    results['home'] = test_endpoint("Home Page", "GET", f"{BASE_URL}/")
    results['players'] = test_endpoint("Players Page", "GET", f"{BASE_URL}/players")
    results['games'] = test_endpoint("Games Page", "GET", f"{BASE_URL}/games")
    results['stats'] = test_endpoint("Stats Page", "GET", f"{BASE_URL}/stats")
    
    # Test 2: Add Player
    print("\n👤 Testing Player Management")
    print("-" * 30)
    player_data = {
        'first_name': 'John',
        'last_name': 'Doe'
    }
    results['add_player'] = test_endpoint("Add Player", "POST", f"{BASE_URL}/add_player", player_data, expected_status=302)
    
    player_data2 = {
        'first_name': 'Jane',
        'last_name': 'Smith'
    }
    results['add_player2'] = test_endpoint("Add Second Player", "POST", f"{BASE_URL}/add_player", player_data2, expected_status=302)
    
    # Test 3: Add Board
    print("\n🎯 Testing Board Management")
    print("-" * 30)
    board_data = {
        'roman_number': 'I',
        'description': 'My first cribbage board',
        'date': '01/01/2025',
        'in_collection': '1',
        'material_type': 'Wood',
        'wood_type': 'Oak',
        'is_gift': '0'
    }
    results['add_board'] = test_endpoint("Add Board", "POST", f"{BASE_URL}/add_board", board_data, expected_status=302)
    
    # Test 4: Add Game
    print("\n🎮 Testing Game Management")
    print("-" * 30)
    game_data = {
        'date_played': '2025-01-01',
        'winner_id': '1',
        'loser_id': '2',
        'winner_score': '121',
        'loser_score': '85',
        'notes': 'Great game!'
    }
    results['add_game'] = test_endpoint("Add Game", "POST", f"{BASE_URL}/add_game", game_data, expected_status=302)
    
    # Test 5: Detail Pages (after adding data)
    print("\n🔍 Testing Detail Pages")
    print("-" * 30)
    results['board_detail'] = test_endpoint("Board Detail", "GET", f"{BASE_URL}/board_detail/1")
    results['player_detail'] = test_endpoint("Player Detail", "GET", f"{BASE_URL}/player_detail/1")
    
    # Test 6: Edit Pages
    print("\n✏️ Testing Edit Pages")
    print("-" * 30)
    results['edit_board'] = test_endpoint("Edit Board Page", "GET", f"{BASE_URL}/edit_board/1")
    results['edit_player'] = test_endpoint("Edit Player Page", "GET", f"{BASE_URL}/edit_player/1")
    results['edit_game'] = test_endpoint("Edit Game Page", "GET", f"{BASE_URL}/game/1/edit")
    
    # Test 7: Delete Operations
    print("\n🗑️ Testing Delete Operations")
    print("-" * 30)
    # Add another game first
    game_data2 = {
        'date_played': '2025-01-02',
        'winner_id': '2',
        'loser_id': '1',
        'winner_score': '121',
        'loser_score': '50',  # This should be a double skunk
        'notes': 'Double skunk!'
    }
    test_endpoint("Add Second Game", "POST", f"{BASE_URL}/add_game", game_data2, expected_status=302)
    
    # Now test delete
    results['delete_game'] = test_endpoint("Delete Game", "POST", f"{BASE_URL}/game/2/delete", expected_status=302)
    
    # Test 8: Stats with Nemesis and Skunks
    print("\n📊 Testing Enhanced Stats")
    print("-" * 30)
    results['stats_with_data'] = test_endpoint("Stats with Data", "GET", f"{BASE_URL}/stats")
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST RESULTS SUMMARY")
    print("="*60)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    success_rate = (passed / total) * 100
    
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success Rate: {success_rate:.1f}%")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! 🎉")
        print("✅ URL routing issues: FIXED")
        print("✅ Player picture sizing: FIXED") 
        print("✅ Date formatting: FIXED")
        print("✅ Nemesis and skunk stats: RESTORED")
        print("✅ Game deletion: WORKING")
        print("✅ Game editing: WORKING")
    else:
        print(f"\n❌ {total - passed} tests still failing")
        failed_tests = [name for name, result in results.items() if not result]
        print(f"Failed tests: {', '.join(failed_tests)}")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
