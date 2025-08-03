#!/usr/bin/env python3
import requests
import time

base_url = "http://localhost:5001"

def test_data_retrieval():
    print("🔍 Testing Data Retrieval After Creation")
    print("=" * 50)
    
    # First, let's add some data
    print("📝 Adding test data...")
    
    # Add a player
    player_data = {
        'first_name': 'John',
        'last_name': 'Doe'
    }
    player_response = requests.post(f"{base_url}/add_player", data=player_data)
    print(f"Add player response: {player_response.status_code}")
    
    # Add a board
    board_data = {
        'roman_number': 'I',
        'description': 'Test Board',
        'date': '2024-01-01',
        'material_type': 'Wood',
        'wood_type': 'Oak'
    }
    board_response = requests.post(f"{base_url}/add_board", data=board_data)
    print(f"Add board response: {board_response.status_code}")
    
    # Wait a moment for data to be saved
    time.sleep(1)
    
    # Now try to access detail pages with different IDs
    print("\n🔍 Testing Detail Pages")
    
    # Try board details with various IDs
    for board_id in [1, 2, 3]:
        try:
            board_detail = requests.get(f"{base_url}/board/{board_id}")
            print(f"Board {board_id} detail: {board_detail.status_code}")
        except Exception as e:
            print(f"Board {board_id} error: {e}")
    
    # Try player details with various IDs
    for player_id in [1, 2, 3]:
        try:
            player_detail = requests.get(f"{base_url}/player/{player_id}")
            print(f"Player {player_id} detail: {player_detail.status_code}")
        except Exception as e:
            print(f"Player {player_id} error: {e}")
    
    # Check what's on the home page
    print("\n🏠 Home Page Content")
    home = requests.get(base_url)
    if "John Doe" in home.text:
        print("✅ Home page shows John Doe")
    else:
        print("❌ Home page doesn't show John Doe")
    
    if "Test Board" in home.text:
        print("✅ Home page shows Test Board")
    else:
        print("❌ Home page doesn't show Test Board")
    
    # Check players page
    print("\n👥 Players Page Content")
    players = requests.get(f"{base_url}/players")
    if "John Doe" in players.text:
        print("✅ Players page shows John Doe")
    else:
        print("❌ Players page doesn't show John Doe")

if __name__ == "__main__":
    test_data_retrieval()
