#!/usr/bin/env python3
"""
Unit Tests for Cribbage Board Collection App
Tests database functions and core functionality directly
"""

import os
import sys
import sqlite3
import unittest
import tempfile
import shutil
from unittest.mock import patch, MagicMock

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

# Import the app
from app import app, execute_query, generate_unique_filename, safe_delete_file

class TestCribbageApp(unittest.TestCase):
    
    def setUp(self):
        """Set up test environment"""
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()
        
        # Create a temporary database for testing
        self.test_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.test_db.close()
        
        # Setup test database schema
        self.setup_test_database()
        
        # Mock the database path
        self.original_db_path = None
        
    def tearDown(self):
        """Clean up after tests"""
        try:
            os.unlink(self.test_db.name)
        except:
            pass
    
    def setup_test_database(self):
        """Create test database with proper schema"""
        conn = sqlite3.connect(self.test_db.name)
        cursor = conn.cursor()
        
        # Create boards table
        cursor.execute("""
            CREATE TABLE boards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                roman_number TEXT,
                description TEXT,
                wood_type TEXT,
                material_type TEXT,
                image_front TEXT,
                image_back TEXT,
                in_collection INTEGER DEFAULT 1,
                is_gift INTEGER DEFAULT 0,
                gifted_to TEXT,
                gifted_from TEXT
            )
        """)
        
        # Create players table
        cursor.execute("""
            CREATE TABLE players (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                photo TEXT,
                date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create games table
        cursor.execute("""
            CREATE TABLE games (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                board_id INTEGER,
                winner_id INTEGER,
                loser_id INTEGER,
                winner_score INTEGER DEFAULT 121,
                loser_score INTEGER DEFAULT 0,
                is_skunk INTEGER DEFAULT 0,
                is_double_skunk INTEGER DEFAULT 0,
                date_played TEXT DEFAULT (DATE('now'))
            )
        """)
        
        conn.commit()
        conn.close()
        
    @patch('app.os.path.join')
    def test_database_connection(self, mock_join):
        """Test database connection works"""
        mock_join.return_value = self.test_db.name
        
        # Test basic query
        result = execute_query("SELECT 1 as test", fetch=True)
        self.assertIsNotNone(result)
        self.assertEqual(result[0]['test'], 1)
    
    @patch('app.os.path.join')
    def test_add_board(self, mock_join):
        """Test adding a board to database"""
        mock_join.return_value = self.test_db.name
        
        # Add a test board
        execute_query("""
            INSERT INTO boards (date, roman_number, description, wood_type, material_type,
                              image_front, image_back, in_collection, is_gift, gifted_to, gifted_from)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, ['2024-01-01', 'XCII', 'Test board', 'Walnut', 'Solid Wood', 
              None, None, 1, 0, '', ''])
        
        # Verify board was added
        result = execute_query("SELECT * FROM boards WHERE roman_number = 'XCII'", fetch=True)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['description'], 'Test board')
        self.assertEqual(result[0]['wood_type'], 'Walnut')
    
    @patch('app.os.path.join') 
    def test_add_player(self, mock_join):
        """Test adding a player to database"""
        mock_join.return_value = self.test_db.name
        
        # Add a test player
        execute_query("""
            INSERT INTO players (first_name, last_name, photo)
            VALUES (?, ?, ?)
        """, ['John', 'Doe', None])
        
        # Verify player was added
        result = execute_query("SELECT * FROM players WHERE first_name = 'John'", fetch=True)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['last_name'], 'Doe')
    
    @patch('app.os.path.join')
    def test_add_game(self, mock_join):
        """Test adding a game to database"""
        mock_join.return_value = self.test_db.name
        
        # First add test data
        execute_query("INSERT INTO players (first_name, last_name) VALUES ('Alice', 'Smith')")
        execute_query("INSERT INTO players (first_name, last_name) VALUES ('Bob', 'Jones')")
        execute_query("INSERT INTO boards (roman_number, description) VALUES ('I', 'Test Board')")
        
        # Add a test game
        execute_query("""
            INSERT INTO games (winner_id, loser_id, board_id, winner_score, loser_score, 
                             date_played, is_skunk, is_double_skunk)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, [1, 2, 1, 121, 90, '2024-01-01', 1, 0])
        
        # Verify game was added
        result = execute_query("SELECT * FROM games WHERE winner_id = 1", fetch=True)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['loser_id'], 2)
        self.assertEqual(result[0]['is_skunk'], 1)
    
    def test_filename_generation(self):
        """Test unique filename generation"""
        filename1 = generate_unique_filename("test.jpg", "board")
        filename2 = generate_unique_filename("test.jpg", "board")
        
        # Filenames should be different
        self.assertNotEqual(filename1, filename2)
        
        # Should contain prefix and extension
        self.assertTrue(filename1.startswith("board_"))
        self.assertTrue(filename1.endswith(".jpg"))
    
    def test_home_page(self):
        """Test home page renders"""
        with patch('app.execute_query') as mock_query:
            mock_query.return_value = []
            response = self.client.get('/')
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Cribbage Board Collection', response.data)
    
    def test_add_board_get(self):
        """Test add board form loads"""
        response = self.client.get('/add_board')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Add New Cribbage Board', response.data)
    
    def test_players_page(self):
        """Test players page renders"""
        with patch('app.execute_query') as mock_query:
            mock_query.return_value = []
            response = self.client.get('/players')
            self.assertEqual(response.status_code, 200)
    
    def test_games_page(self):
        """Test games page renders"""
        with patch('app.execute_query') as mock_query:
            mock_query.return_value = []
            response = self.client.get('/games')
            self.assertEqual(response.status_code, 200)
    
    def test_stats_page(self):
        """Test stats page renders"""
        with patch('app.execute_query') as mock_query:
            # Mock the stats queries
            mock_query.side_effect = [
                [{'count': 5}],  # board_count
                [{'count': 3}],  # player_count  
                [{'count': 10}], # game_count
                [{'count': 4}],  # in_collection
                [{'count': 1}],  # gifts_given
                []               # top_players
            ]
            response = self.client.get('/stats')
            self.assertEqual(response.status_code, 200)

class TestDataValidation(unittest.TestCase):
    """Test data validation and edge cases"""
    
    def test_empty_filename(self):
        """Test handling of empty filenames"""
        result = generate_unique_filename("", "test")
        self.assertIsNone(result)
        
        result = generate_unique_filename(None, "test")
        self.assertIsNone(result)
    
    def test_filename_without_extension(self):
        """Test filename generation without extension"""
        result = generate_unique_filename("testfile", "board")
        self.assertTrue(result.endswith(".jpg"))  # Should default to .jpg
    
    def test_safe_delete_empty_filename(self):
        """Test safe delete with empty filename"""
        # Should not raise an exception
        safe_delete_file("")
        safe_delete_file(None)

def run_unit_tests():
    """Run all unit tests"""
    print("🧪 Running Unit Tests for Cribbage App")
    print("=" * 40)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestCribbageApp))
    suite.addTests(loader.loadTestsFromTestCase(TestDataValidation))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 40)
    print("📊 UNIT TEST SUMMARY")
    print("=" * 40)
    print(f"Tests Run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ Failures:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
    
    if result.errors:
        print("\n⚠️ Errors:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    print(f"\n{'✅ All tests passed!' if success else '❌ Some tests failed'}")
    
    return success

if __name__ == "__main__":
    run_unit_tests()
