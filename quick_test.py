#!/usr/bin/env python3

import requests
import json
import sys

BASE_URL = "http://localhost:5001"

def test_page(name, url):
    try:
        response = requests.get(url)
        print(f"✅ {name}: Status {response.status_code}")
        if response.status_code != 200:
            print(f"   Error: {response.text[:200]}...")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ {name}: Error - {e}")
        return False

def test_post(name, url, data, files=None):
    try:
        response = requests.post(url, data=data, files=files)
        print(f"✅ {name}: Status {response.status_code}")
        if response.status_code >= 400:
            print(f"   Error: {response.text[:200]}...")
        return response.status_code < 400
    except Exception as e:
        print(f"❌ {name}: Error - {e}")
        return False

def main():
    print("🔍 Testing Cribbage App Functionality")
    print("=" * 50)
    
    # Test basic pages
    test_page("Home Page", f"{BASE_URL}/")
    test_page("Players Page", f"{BASE_URL}/players")
    test_page("Games Page", f"{BASE_URL}/games")
    test_page("Stats Page", f"{BASE_URL}/stats")
    
    print("\n🧪 Testing Form Submissions")
    print("=" * 50)
    
    # Test adding a player
    player_data = {
        'first_name': 'Test',
        'last_name': 'Player'
    }
    test_post("Add Player", f"{BASE_URL}/add_player", player_data)
    
    # Test adding a board
    board_data = {
        'roman_number': 'TEST',
        'description': 'Test board',
        'in_collection': '1',
        'material_type': 'Wood',
        'wood_type': 'Oak',
        'is_gift': '0'
    }
    test_post("Add Board", f"{BASE_URL}/add_board", board_data)
    
    # Test adding a game
    game_data = {
        'date_played': '2025-01-01',
        'winner_id': '1',
        'loser_id': '2',
        'winner_score': '121',
        'loser_score': '100'
    }
    test_post("Add Game", f"{BASE_URL}/add_game", game_data)

if __name__ == "__main__":
    main()
