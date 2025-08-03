#!/usr/bin/env python3
import requests
import time

base_url = "http://localhost:5001"

def run_comprehensive_test():
    print("🚀 COMPREHENSIVE APPLICATION TEST")
    print("=" * 50)
    
    results = {
        'page_loads': 0,
        'form_submissions': 0,
        'detail_pages': 0,
        'total_tests': 0
    }
    
    # Test 1: Basic page loading
    print("\n📄 Testing Basic Page Loading")
    pages = [
        ('Home', '/'),
        ('Players', '/players'),
        ('Games', '/games'),
        ('Stats', '/stats'),
        ('Add Player', '/add_player'),
        ('Add Board', '/add_board'),
        ('Add Game', '/add_game')
    ]
    
    for name, path in pages:
        try:
            response = requests.get(f"{base_url}{path}")
            status = "✅ OK" if response.status_code == 200 else f"❌ {response.status_code}"
            print(f"{name:15} {status}")
            if response.status_code == 200:
                results['page_loads'] += 1
            results['total_tests'] += 1
        except Exception as e:
            print(f"{name:15} ❌ Error: {e}")
            results['total_tests'] += 1
    
    # Test 2: Form submissions (should work and create data)
    print("\n📝 Testing Form Submissions")
    
    # Add a player
    player_data = {
        'first_name': 'Test',
        'last_name': 'Player'
    }
    try:
        response = requests.post(f"{base_url}/add_player", data=player_data, allow_redirects=False)
        status = "✅ OK" if response.status_code in [200, 302] else f"❌ {response.status_code}"
        print(f"Add Player:     {status}")
        if response.status_code in [200, 302]:
            results['form_submissions'] += 1
        results['total_tests'] += 1
    except Exception as e:
        print(f"Add Player:     ❌ Error: {e}")
        results['total_tests'] += 1
    
    # Add a board
    board_data = {
        'roman_number': 'TEST',
        'description': 'Test Board Description',
        'date': '2024-01-01',
        'material_type': 'Wood',
        'wood_type': 'Pine'
    }
    try:
        response = requests.post(f"{base_url}/add_board", data=board_data, allow_redirects=False)
        status = "✅ OK" if response.status_code in [200, 302] else f"❌ {response.status_code}"
        print(f"Add Board:      {status}")
        if response.status_code in [200, 302]:
            results['form_submissions'] += 1
        results['total_tests'] += 1
    except Exception as e:
        print(f"Add Board:      ❌ Error: {e}")
        results['total_tests'] += 1
    
    # Wait for data to be saved
    time.sleep(1)
    
    # Test 3: Detail pages (should work with existing data)
    print("\n🔍 Testing Detail Pages")
    
    # Test board details
    for board_id in [1, 5, 7]:  # We know we have at least 7 boards
        try:
            response = requests.get(f"{base_url}/board/{board_id}")
            status = "✅ OK" if response.status_code == 200 else f"❌ {response.status_code}"
            print(f"Board {board_id}:        {status}")
            if response.status_code == 200:
                results['detail_pages'] += 1
            results['total_tests'] += 1
        except Exception as e:
            print(f"Board {board_id}:        ❌ Error: {e}")
            results['total_tests'] += 1
    
    # Test player details
    for player_id in [1, 10, 17]:  # We know we have at least 17 players
        try:
            response = requests.get(f"{base_url}/player/{player_id}")
            status = "✅ OK" if response.status_code == 200 else f"❌ {response.status_code}"
            print(f"Player {player_id}:      {status}")
            if response.status_code == 200:
                results['detail_pages'] += 1
            results['total_tests'] += 1
        except Exception as e:
            print(f"Player {player_id}:      ❌ Error: {e}")
            results['total_tests'] += 1
    
    # Test 4: Advanced functionality
    print("\n⚙️  Testing Advanced Features")
    
    # Test stats page has nemesis data
    try:
        response = requests.get(f"{base_url}/stats")
        has_nemesis = "Nemesis" in response.text or "nemesis" in response.text
        status = "✅ OK" if response.status_code == 200 and has_nemesis else f"❌ Missing nemesis"
        print(f"Nemesis Stats:  {status}")
        if response.status_code == 200:
            results['detail_pages'] += 1
        results['total_tests'] += 1
    except Exception as e:
        print(f"Nemesis Stats:  ❌ Error: {e}")
        results['total_tests'] += 1
    
    # Summary
    print("\n📊 TEST SUMMARY")
    print("=" * 50)
    print(f"Page Loads:       {results['page_loads']:2d} / {len(pages)}")
    print(f"Form Submissions: {results['form_submissions']:2d} / 2")
    print(f"Detail Pages:     {results['detail_pages']:2d} / 7")
    print(f"Total:            {results['page_loads'] + results['form_submissions'] + results['detail_pages']:2d} / {results['total_tests']}")
    
    success_rate = ((results['page_loads'] + results['form_submissions'] + results['detail_pages']) / results['total_tests']) * 100
    print(f"\nSuccess Rate: {success_rate:.1f}%")
    
    if success_rate >= 90:
        print("🎉 EXCELLENT! Application is working great!")
    elif success_rate >= 75:
        print("✅ GOOD! Most functionality is working.")
    elif success_rate >= 50:
        print("⚠️  FAIR. Some issues remain.")
    else:
        print("❌ POOR. Significant issues need fixing.")

if __name__ == "__main__":
    run_comprehensive_test()
