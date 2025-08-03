#!/usr/bin/env python3

import requests
import json

BASE_URL = "http://localhost:5001"

def test_form_detailed(name, url, data):
    try:
        response = requests.post(url, data=data, allow_redirects=False)
        print(f"\n🔍 {name}")
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        if response.text:
            print(f"Response text (first 500 chars): {response.text[:500]}")
        return response
    except Exception as e:
        print(f"❌ {name}: Error - {e}")
        return None

def main():
    print("🔍 Detailed Form Testing")
    print("="*50)
    
    # Test player form
    player_data = {
        'first_name': 'Test',
        'last_name': 'User'
    }
    test_form_detailed("Add Player", f"{BASE_URL}/add_player", player_data)
    
    # Test board form
    board_data = {
        'roman_number': 'TEST',
        'description': 'Test board',
        'in_collection': '1',
        'material_type': 'Wood',
        'wood_type': 'Oak',
        'is_gift': '0'
    }
    test_form_detailed("Add Board", f"{BASE_URL}/add_board", board_data)
    
    # Check if data was created
    print(f"\n🔍 Checking Home Page After Data Creation")
    response = requests.get(f"{BASE_URL}/")
    print(f"Home page contains 'TEST': {'TEST' in response.text}")
    print(f"Home page length: {len(response.text)} chars")
    
    # Check players page
    response = requests.get(f"{BASE_URL}/players")
    print(f"Players page contains 'Test User': {'Test User' in response.text}")
    print(f"Players page length: {len(response.text)} chars")

if __name__ == "__main__":
    main()
