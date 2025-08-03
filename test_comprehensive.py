#!/usr/bin/env python3
"""
Comprehensive Test Suite for Cribbage Board Collection App
Tests all major functionality including boards, players, games, and file uploads
"""

import os
import sys
import sqlite3
import requests
import json
import time
from datetime import datetime, timedelta

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

BASE_URL = "http://localhost:5001"
UPLOAD_DIR = "app/static/uploads"

class CribbageAppTester:
    def __init__(self):
        self.session = requests.Session()
        self.db_path = "app/database.db"
        self.test_results = []
        
    def log_test(self, test_name, success, message=""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            'test': test_name,
            'success': success,
            'message': message
        })
        print(f"{status}: {test_name}")
        if message:
            print(f"    {message}")
    
    def setup_database(self):
        """Ensure database is clean and has proper schema"""
        try:
            # Clear existing data
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Clear tables
            cursor.execute("DELETE FROM games")
            cursor.execute("DELETE FROM boards")
            cursor.execute("DELETE FROM players")
            
            conn.commit()
            conn.close()
            
            self.log_test("Database Setup", True, "Database cleared successfully")
            return True
        except Exception as e:
            self.log_test("Database Setup", False, str(e))
            return False
    
    def test_home_page(self):
        """Test the home page loads"""
        try:
            response = self.session.get(f"{BASE_URL}/")
            success = response.status_code == 200 and "Cribbage Board Collection" in response.text
            self.log_test("Home Page Load", success, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("Home Page Load", False, str(e))
            return False
    
    def test_add_board_form(self):
        """Test the add board form loads"""
        try:
            response = self.session.get(f"{BASE_URL}/add_board")
            success = response.status_code == 200 and "Add New Cribbage Board" in response.text
            self.log_test("Add Board Form Load", success, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("Add Board Form Load", False, str(e))
            return False
    
    def test_add_board_with_data(self):
        """Test adding a board with complete data"""
        try:
            # Get available photos
            photos = [f for f in os.listdir(UPLOAD_DIR) if f.endswith(('.jpg', '.jpeg', '.png'))]
            front_photo = None
            back_photo = None
            
            for photo in photos:
                if 'front' in photo:
                    front_photo = photo
                elif 'back' in photo:
                    back_photo = photo
            
            # Test data for multiple boards
            test_boards = [
                {
                    'date': '2024-01-15',
                    'roman_number': 'XCII',
                    'description': 'Beautiful walnut board with mother of pearl inlays',
                    'wood_type': 'Walnut',
                    'material_type': 'Solid Wood',
                    'in_collection': '1',
                    'is_gift': '',
                    'gifted_to': '',
                    'gifted_from': ''
                },
                {
                    'date': '2024-02-10',
                    'roman_number': '93',
                    'description': 'Cherry wood board with brass pegs',
                    'wood_type': 'Cherry',
                    'material_type': 'Solid Wood',
                    'in_collection': '1',
                    'is_gift': '1',
                    'gifted_to': 'John Smith',
                    'gifted_from': 'Mary Johnson'
                },
                {
                    'date': '2024-03-05',
                    'roman_number': 'XCV',
                    'description': 'Oak board with traditional design',
                    'wood_type': 'Oak',
                    'material_type': 'Solid Wood',
                    'in_collection': '',
                    'is_gift': '',
                    'gifted_to': '',
                    'gifted_from': ''
                }
            ]
            
            added_boards = 0
            for i, board_data in enumerate(test_boards):
                try:
                    files = {}
                    if front_photo and i == 0:  # Add photo to first board
                        with open(os.path.join(UPLOAD_DIR, front_photo), 'rb') as f:
                            files['front_view'] = (front_photo, f.read())
                    if back_photo and i == 0:
                        with open(os.path.join(UPLOAD_DIR, back_photo), 'rb') as f:
                            files['back_view'] = (back_photo, f.read())
                    
                    response = self.session.post(f"{BASE_URL}/add_board", data=board_data, files=files)
                    
                    if response.status_code == 200 and "Board added successfully" in response.text:
                        added_boards += 1
                    elif response.status_code == 302:  # Redirect on success
                        added_boards += 1
                
                except Exception as e:
                    print(f"Error adding board {i+1}: {e}")
            
            success = added_boards == len(test_boards)
            self.log_test("Add Boards with Data", success, f"Added {added_boards}/{len(test_boards)} boards")
            return success
            
        except Exception as e:
            self.log_test("Add Boards with Data", False, str(e))
            return False
    
    def test_players_page(self):
        """Test players page loads"""
        try:
            response = self.session.get(f"{BASE_URL}/players")
            success = response.status_code == 200
            self.log_test("Players Page Load", success, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("Players Page Load", False, str(e))
            return False
    
    def test_add_players(self):
        """Test adding players"""
        try:
            # Get available player photo
            photos = [f for f in os.listdir(UPLOAD_DIR) if f.endswith(('.jpg', '.jpeg', '.png'))]
            player_photo = None
            
            for photo in photos:
                if 'player' in photo:
                    player_photo = photo
                    break
            
            test_players = [
                {'first_name': 'Alice', 'last_name': 'Johnson'},
                {'first_name': 'Bob', 'last_name': 'Smith'},
                {'first_name': 'Charlie', 'last_name': 'Brown'},
                {'first_name': 'Diana', 'last_name': 'Wilson'}
            ]
            
            added_players = 0
            for i, player_data in enumerate(test_players):
                try:
                    files = {}
                    if player_photo and i == 0:  # Add photo to first player
                        with open(os.path.join(UPLOAD_DIR, player_photo), 'rb') as f:
                            files['photo'] = (player_photo, f.read())
                    
                    response = self.session.post(f"{BASE_URL}/add_player", data=player_data, files=files)
                    
                    if response.status_code == 302:  # Redirect on success
                        added_players += 1
                
                except Exception as e:
                    print(f"Error adding player {i+1}: {e}")
            
            success = added_players == len(test_players)
            self.log_test("Add Players", success, f"Added {added_players}/{len(test_players)} players")
            return success
            
        except Exception as e:
            self.log_test("Add Players", False, str(e))
            return False
    
    def test_games_page(self):
        """Test games page loads"""
        try:
            response = self.session.get(f"{BASE_URL}/games")
            success = response.status_code == 200
            self.log_test("Games Page Load", success, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("Games Page Load", False, str(e))
            return False
    
    def test_add_games(self):
        """Test adding games"""
        try:
            # First get available players and boards from database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT id FROM players LIMIT 4")
            player_ids = [row[0] for row in cursor.fetchall()]
            
            cursor.execute("SELECT id FROM boards LIMIT 3")
            board_ids = [row[0] for row in cursor.fetchall()]
            
            conn.close()
            
            if len(player_ids) < 2 or len(board_ids) < 1:
                self.log_test("Add Games", False, "Not enough players or boards to create games")
                return False
            
            # Create test games
            base_date = datetime.now() - timedelta(days=30)
            test_games = []
            
            for i in range(10):  # Create 10 games
                game_date = base_date + timedelta(days=i*3)
                test_games.append({
                    'winner_id': str(player_ids[i % len(player_ids)]),
                    'loser_id': str(player_ids[(i+1) % len(player_ids)]),
                    'board_id': str(board_ids[i % len(board_ids)]),
                    'date_played': game_date.strftime('%Y-%m-%d'),
                    'is_skunk': '1' if i % 4 == 0 else '',  # Every 4th game is a skunk
                    'is_double_skunk': '1' if i % 8 == 0 else ''  # Every 8th game is a double skunk
                })
            
            added_games = 0
            for i, game_data in enumerate(test_games):
                try:
                    response = self.session.post(f"{BASE_URL}/add_game", data=game_data)
                    
                    if response.status_code == 302:  # Redirect on success
                        added_games += 1
                
                except Exception as e:
                    print(f"Error adding game {i+1}: {e}")
            
            success = added_games == len(test_games)
            self.log_test("Add Games", success, f"Added {added_games}/{len(test_games)} games")
            return success
            
        except Exception as e:
            self.log_test("Add Games", False, str(e))
            return False
    
    def test_board_detail_pages(self):
        """Test individual board detail pages"""
        try:
            # Get board IDs from database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM boards LIMIT 3")
            board_ids = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            success_count = 0
            for board_id in board_ids:
                try:
                    response = self.session.get(f"{BASE_URL}/board/{board_id}")
                    if response.status_code == 200:
                        success_count += 1
                except Exception:
                    pass
            
            success = success_count == len(board_ids)
            self.log_test("Board Detail Pages", success, f"Loaded {success_count}/{len(board_ids)} board details")
            return success
            
        except Exception as e:
            self.log_test("Board Detail Pages", False, str(e))
            return False
    
    def test_player_detail_pages(self):
        """Test individual player detail pages"""
        try:
            # Get player IDs from database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM players LIMIT 4")
            player_ids = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            success_count = 0
            for player_id in player_ids:
                try:
                    response = self.session.get(f"{BASE_URL}/player/{player_id}")
                    if response.status_code == 200:
                        success_count += 1
                except Exception:
                    pass
            
            success = success_count == len(player_ids)
            self.log_test("Player Detail Pages", success, f"Loaded {success_count}/{len(player_ids)} player details")
            return success
            
        except Exception as e:
            self.log_test("Player Detail Pages", False, str(e))
            return False
    
    def test_edit_board(self):
        """Test editing a board"""
        try:
            # Get first board ID
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM boards LIMIT 1")
            result = cursor.fetchone()
            conn.close()
            
            if not result:
                self.log_test("Edit Board", False, "No boards available to edit")
                return False
            
            board_id = result[0]
            
            # Test GET edit form
            response = self.session.get(f"{BASE_URL}/edit_board/{board_id}")
            if response.status_code != 200:
                self.log_test("Edit Board", False, f"Edit form failed to load: {response.status_code}")
                return False
            
            # Test POST edit
            edit_data = {
                'date': '2024-06-15',
                'roman_number': 'XCIX',
                'description': 'Updated description - Beautiful edited board',
                'wood_type': 'Maple',
                'material_type': 'Solid Wood',
                'in_collection': '1',
                'is_gift': '1',
                'gifted_to': 'Updated Recipient',
                'gifted_from': 'Updated Giver'
            }
            
            response = self.session.post(f"{BASE_URL}/edit_board/{board_id}", data=edit_data)
            success = response.status_code in [200, 302]
            
            self.log_test("Edit Board", success, f"Edit response: {response.status_code}")
            return success
            
        except Exception as e:
            self.log_test("Edit Board", False, str(e))
            return False
    
    def test_edit_player(self):
        """Test editing a player"""
        try:
            # Get first player ID
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM players LIMIT 1")
            result = cursor.fetchone()
            conn.close()
            
            if not result:
                self.log_test("Edit Player", False, "No players available to edit")
                return False
            
            player_id = result[0]
            
            # Test GET edit form
            response = self.session.get(f"{BASE_URL}/edit_player/{player_id}")
            if response.status_code != 200:
                self.log_test("Edit Player", False, f"Edit form failed to load: {response.status_code}")
                return False
            
            # Test POST edit
            edit_data = {
                'first_name': 'Updated',
                'last_name': 'Player'
            }
            
            response = self.session.post(f"{BASE_URL}/edit_player/{player_id}", data=edit_data)
            success = response.status_code in [200, 302]
            
            self.log_test("Edit Player", success, f"Edit response: {response.status_code}")
            return success
            
        except Exception as e:
            self.log_test("Edit Player", False, str(e))
            return False
    
    def test_stats_page(self):
        """Test stats page loads and shows data"""
        try:
            response = self.session.get(f"{BASE_URL}/stats")
            success = (response.status_code == 200 and 
                      "board_count" in response.text.lower() and
                      "player_count" in response.text.lower())
            self.log_test("Stats Page", success, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("Stats Page", False, str(e))
            return False
    
    def test_database_integrity(self):
        """Test database has the expected data"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Count records
            cursor.execute("SELECT COUNT(*) FROM boards")
            board_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM players")
            player_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM games")
            game_count = cursor.fetchone()[0]
            
            conn.close()
            
            success = board_count >= 3 and player_count >= 4 and game_count >= 10
            message = f"Boards: {board_count}, Players: {player_count}, Games: {game_count}"
            
            self.log_test("Database Integrity", success, message)
            return success
            
        except Exception as e:
            self.log_test("Database Integrity", False, str(e))
            return False
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🎯 Starting Comprehensive Cribbage App Tests")
        print("=" * 50)
        
        # Database setup
        if not self.setup_database():
            print("❌ Database setup failed, stopping tests")
            return
        
        # Basic page tests
        self.test_home_page()
        self.test_add_board_form()
        self.test_players_page()
        self.test_games_page()
        
        # Data creation tests
        self.test_add_board_with_data()
        self.test_add_players()
        self.test_add_games()
        
        # Detail page tests
        self.test_board_detail_pages()
        self.test_player_detail_pages()
        
        # Edit functionality tests
        self.test_edit_board()
        self.test_edit_player()
        
        # Stats and integrity tests
        self.test_stats_page()
        self.test_database_integrity()
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)
        
        passed = sum(1 for result in self.test_results if result['success'])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        # Show failed tests
        failed_tests = [result for result in self.test_results if not result['success']]
        if failed_tests:
            print(f"\n❌ Failed Tests ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"  - {test['test']}: {test['message']}")
        
        print("\n🎉 Testing Complete!")
        return passed == total

def main():
    """Main function to run tests"""
    # Check if Flask app is running
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code != 200:
            print("❌ Flask app is not responding properly")
            print("Please start the app with: python3 start_app.py")
            return
    except requests.exceptions.RequestException:
        print("❌ Flask app is not running on http://localhost:5000")
        print("Please start the app with: python3 start_app.py")
        return
    
    # Run tests
    tester = CribbageAppTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()
