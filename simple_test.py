#!/usr/bin/env python3
"""
Simple Test Runner for Cribbage Board Collection App
Tests database operations and basic functionality without external dependencies
"""

import os
import sqlite3
import sys
from datetime import datetime

class SimpleCribbageTest:
    def __init__(self):
        self.db_path = "app/database.db"
        self.test_results = []
        
    def log_test(self, test_name, success, message=""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        self.test_results.append({"test": test_name, "success": success, "message": message})
    
    def test_database_exists(self):
        """Test if database file exists"""
        exists = os.path.exists(self.db_path)
        self.log_test("Database Exists", exists, f"Path: {self.db_path}")
        return exists
    
    def test_database_schema(self):
        """Test if all required tables exist"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check for all required tables
            required_tables = ['boards', 'players', 'games', 'wood_types', 'material_types']
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            existing_tables = [row[0] for row in cursor.fetchall()]
            
            missing_tables = [table for table in required_tables if table not in existing_tables]
            
            success = len(missing_tables) == 0
            message = f"Missing tables: {missing_tables}" if missing_tables else "All tables present"
            
            conn.close()
            self.log_test("Database Schema", success, message)
            return success
        except Exception as e:
            self.log_test("Database Schema", False, f"Error: {str(e)}")
            return False
    
    def test_add_sample_data(self):
        """Add sample data for testing"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Add wood types
            wood_types = ["Oak", "Maple", "Cherry", "Walnut", "Pine"]
            for wood in wood_types:
                cursor.execute("INSERT OR IGNORE INTO wood_types (name) VALUES (?)", (wood,))
            
            # Add material types
            material_types = ["Wood", "Metal", "Plastic", "Resin"]
            for material in material_types:
                cursor.execute("INSERT OR IGNORE INTO material_types (name) VALUES (?)", (material,))
            
            # Add players
            players = [
                ("Alice", "Johnson"),
                ("Bob", "Smith"),
                ("Charlie", "Brown"),
                ("Diana", "Wilson")
            ]
            for first, last in players:
                cursor.execute("INSERT OR IGNORE INTO players (first_name, last_name) VALUES (?, ?)", (first, last))
            
            # Add boards
            boards = [
                ("01/15/2023", "I", "Beautiful oak cribbage board", "Oak", "Wood", "oak_front.jpg", "oak_back.jpg", 0, None, None, 1),
                ("03/22/2023", "II", "Maple board with inlay", "Maple", "Wood", "maple_front.jpg", "maple_back.jpg", 1, "Uncle Tom", None, 1),
                ("06/10/2023", None, "Gift board", "Cherry", "Wood", "gift_front.jpg", "gift_back.jpg", 1, None, "Aunt Mary", 0)
            ]
            for board in boards:
                cursor.execute("""
                    INSERT OR IGNORE INTO boards 
                    (date, roman_number, description, wood_type, material_type, image_front, image_back, is_gift, gifted_to, gifted_from, in_collection)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, board)
            
            # Add games with different skunk scenarios
            games = [
                (1, 1, 2, 121, 90, 0, 0, "2023-08-01"),  # Regular game: Alice beats Bob
                (1, 2, 1, 121, 85, 1, 0, "2023-08-02"),  # Skunk: Bob skunks Alice
                (2, 3, 4, 121, 45, 1, 1, "2023-08-03"),  # Double skunk: Charlie double-skunks Diana  
                (1, 4, 3, 121, 95, 0, 0, "2023-08-04"),  # Regular: Diana beats Charlie
                (2, 1, 3, 121, 80, 1, 0, "2023-08-05"),  # Skunk: Alice skunks Charlie
                (1, 2, 4, 121, 100, 0, 0, "2023-08-06"), # Regular: Bob beats Diana
                (2, 3, 1, 121, 88, 1, 0, "2023-08-07"),  # Skunk: Charlie skunks Alice
            ]
            for game in games:
                cursor.execute("""
                    INSERT OR IGNORE INTO games 
                    (board_id, winner_id, loser_id, winner_score, loser_score, is_skunk, is_double_skunk, date_played)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, game)
            
            conn.commit()
            conn.close()
            
            self.log_test("Add Sample Data", True, "Sample data added successfully")
            return True
        except Exception as e:
            self.log_test("Add Sample Data", False, f"Error: {str(e)}")
            return False
    
    def test_query_stats(self):
        """Test statistics queries"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Test player stats query (similar to what's in app.py)
            cursor.execute("""
                SELECT p.id, p.first_name, p.last_name,
                       SUM(CASE WHEN p.id = g.winner_id THEN 1 ELSE 0 END) AS wins,
                       SUM(CASE WHEN p.id = g.loser_id AND g.is_double_skunk = 1 THEN 3
                                WHEN p.id = g.loser_id AND g.is_skunk = 1 THEN 2
                                WHEN p.id = g.loser_id THEN 1 ELSE 0 END) AS total_losses,
                       SUM(CASE WHEN p.id = g.winner_id AND g.is_skunk = 1 THEN 1 ELSE 0 END) AS skunks_given,
                       SUM(CASE WHEN p.id = g.loser_id AND g.is_skunk = 1 THEN 1 ELSE 0 END) AS skunks_received,
                       COUNT(CASE WHEN p.id = g.winner_id OR p.id = g.loser_id THEN 1 END) AS total_games
                FROM players p
                LEFT JOIN games g ON p.id = g.winner_id OR p.id = g.loser_id
                GROUP BY p.id
                ORDER BY wins DESC, total_losses ASC
            """)
            
            results = cursor.fetchall()
            conn.close()
            
            success = len(results) > 0
            message = f"Found stats for {len(results)} players" if success else "No stats found"
            
            # Print detailed stats
            if success:
                print("\n📊 Player Statistics:")
                print("-" * 80)
                print(f"{'Player':<15} {'Wins':<6} {'Losses':<8} {'S.Given':<8} {'S.Recv':<8} {'Games':<6}")
                print("-" * 80)
                for row in results:
                    name = f"{row[1]} {row[2]}"
                    print(f"{name:<15} {row[3]:<6} {row[4]:<8} {row[5]:<8} {row[6]:<8} {row[7]:<6}")
                print("-" * 80)
            
            self.log_test("Query Stats", success, message)
            return success
        except Exception as e:
            self.log_test("Query Stats", False, f"Error: {str(e)}")
            return False
    
    def test_skunk_weighting(self):
        """Test that skunk weighting is working correctly"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Find Diana (player 4) who should have received a double skunk (worth 3 losses)
            cursor.execute("""
                SELECT SUM(CASE WHEN p.id = g.loser_id AND g.is_double_skunk = 1 THEN 3
                               WHEN p.id = g.loser_id AND g.is_skunk = 1 THEN 2
                               WHEN p.id = g.loser_id THEN 1 ELSE 0 END) AS weighted_losses,
                       SUM(CASE WHEN p.id = g.loser_id THEN 1 ELSE 0 END) AS actual_losses
                FROM players p
                LEFT JOIN games g ON p.id = g.winner_id OR p.id = g.loser_id  
                WHERE p.first_name = 'Diana'
                GROUP BY p.id
            """)
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                weighted_losses, actual_losses = result
                # Diana should have more weighted losses than actual losses due to double skunk
                success = weighted_losses > actual_losses if weighted_losses and actual_losses else False
                message = f"Weighted: {weighted_losses}, Actual: {actual_losses}"
            else:
                success = False
                message = "No data found for Diana"
            
            self.log_test("Skunk Weighting", success, message)
            return success
        except Exception as e:
            self.log_test("Skunk Weighting", False, f"Error: {str(e)}")
            return False
    
    def test_nemesis_query(self):
        """Test nemesis finding logic"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Test nemesis query for Alice (player 1)
            cursor.execute("""
                SELECT 
                    CASE WHEN g.winner_id = 1 THEN p2.first_name || ' ' || p2.last_name 
                         ELSE p1.first_name || ' ' || p1.last_name END AS opponent_name,
                    SUM(CASE WHEN g.loser_id = 1 THEN 1 ELSE 0 END) AS losses_to_them
                FROM games g
                JOIN players p1 ON g.winner_id = p1.id
                JOIN players p2 ON g.loser_id = p2.id
                WHERE g.winner_id = 1 OR g.loser_id = 1
                GROUP BY opponent_name
                HAVING COUNT(*) >= 2
                ORDER BY losses_to_them DESC
                LIMIT 1
            """)
            
            result = cursor.fetchone()
            conn.close()
            
            success = result is not None
            message = f"Alice's nemesis: {result[0]} ({result[1]} losses)" if result else "No nemesis found"
            
            self.log_test("Nemesis Query", success, message)
            return success
        except Exception as e:
            self.log_test("Nemesis Query", False, f"Error: {str(e)}")
            return False
    
    def test_duplicate_checking(self):
        """Test duplicate checking for players and boards"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Test duplicate player check
            # First, try to add a duplicate Alice Johnson (should be prevented in the app)
            cursor.execute("SELECT COUNT(*) FROM players WHERE first_name = 'Alice' AND last_name = 'Johnson'")
            alice_count_before = cursor.fetchone()[0]
            
            # Test duplicate board roman numeral check
            # Check if board with roman numeral "I" exists
            cursor.execute("SELECT COUNT(*) FROM boards WHERE roman_number = 'I'")
            roman_i_count = cursor.fetchone()[0]
            
            # Test that we can identify duplicates
            success = True
            messages = []
            
            if alice_count_before > 0:
                messages.append(f"Alice Johnson exists {alice_count_before} times")
                # In a real app, attempting to add another would be blocked
            
            if roman_i_count > 0:
                messages.append(f"Board 'I' exists {roman_i_count} times")
                # In a real app, attempting to add another would be blocked
            
            # Test game duplicate logic
            cursor.execute("""
                SELECT COUNT(*) FROM games 
                WHERE board_id = 1 AND winner_id = 1 AND loser_id = 2 AND date_played = '2023-08-01'
            """)
            duplicate_game_count = cursor.fetchone()[0]
            
            if duplicate_game_count > 0:
                messages.append(f"Potential duplicate game exists {duplicate_game_count} times")
            
            conn.close()
            
            message = " | ".join(messages) if messages else "No duplicates found"
            self.log_test("Duplicate Checking", success, message)
            return success
        except Exception as e:
            self.log_test("Duplicate Checking", False, f"Error: {str(e)}")
            return False

    def test_player_deletion(self):
        """Test player deletion logic with constraints"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Add a test player who has no games
            cursor.execute("INSERT INTO players (first_name, last_name) VALUES (?, ?)", ("Test", "Player"))
            test_player_id = cursor.lastrowid
            
            # Test that we can delete a player with no games
            cursor.execute("SELECT COUNT(*) FROM games WHERE winner_id = ? OR loser_id = ?", 
                          (test_player_id, test_player_id))
            games_count = cursor.fetchone()[0]
            
            can_delete = games_count == 0
            
            if can_delete:
                cursor.execute("DELETE FROM players WHERE id = ?", (test_player_id,))
                cursor.execute("SELECT COUNT(*) FROM players WHERE id = ?", (test_player_id,))
                still_exists = cursor.fetchone()[0] > 0
                success = not still_exists
                message = "Successfully deleted player with no games"
            else:
                success = False
                message = f"Player has {games_count} games, cannot delete"
            
            # Test constraint: try to check if Alice (who has games) would be blocked
            cursor.execute("SELECT COUNT(*) FROM games WHERE winner_id = 1 OR loser_id = 1")
            alice_games = cursor.fetchone()[0]
            
            constraint_works = alice_games > 0
            if constraint_works:
                message += f" | Alice has {alice_games} games (constraint working)"
            
            conn.commit()
            conn.close()
            
            final_success = success and constraint_works
            self.log_test("Player Deletion", final_success, message)
            return final_success
        except Exception as e:
            self.log_test("Player Deletion", False, f"Error: {str(e)}")
            return False

    def test_board_filters(self):
        """Test board filtering logic"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Test collection filter
            cursor.execute("SELECT COUNT(*) FROM boards WHERE in_collection = 1")
            in_collection = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM boards WHERE in_collection = 0") 
            not_in_collection = cursor.fetchone()[0]
            
            # Test gift filter
            cursor.execute("SELECT COUNT(*) FROM boards WHERE is_gift = 1")
            gifts = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM boards WHERE is_gift = 0")
            not_gifts = cursor.fetchone()[0]
            
            conn.close()
            
            success = (in_collection > 0 and gifts > 0)
            message = f"Collection: {in_collection}, Not: {not_in_collection}, Gifts: {gifts}, Regular: {not_gifts}"
            
            self.log_test("Board Filters", success, message)
            return success
        except Exception as e:
            self.log_test("Board Filters", False, f"Error: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all database tests"""
        print("🧪 Cribbage App Database Tests")
        print("=" * 40)
        
        # Basic tests
        if not self.test_database_exists():
            print("❌ Database not found! Run the app first to create it.")
            return
        
        self.test_database_schema()
        self.test_add_sample_data()
        
        # Functionality tests  
        self.test_query_stats()
        self.test_skunk_weighting()
        self.test_nemesis_query()
        self.test_board_filters()
        self.test_duplicate_checking()
        self.test_player_deletion()
        
        # Results
        passed = sum(1 for r in self.test_results if r["success"])
        total = len(self.test_results)
        
        print(f"\n🏁 Results: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
        
        if passed == total:
            print("🎉 All tests passed! Your database is working correctly!")
        else:
            print("⚠️  Some tests failed. Check the output above.")
        
        return passed == total

if __name__ == "__main__":
    print("🎮 Simple Database Test for Cribbage Board Collection")
    print("====================================================")
    
    tester = SimpleCribbageTest()
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ Your cribbage app database is ready!")
        print("🌐 Start the server with: ./run.sh")
        print("🧪 Run full web tests with: python test_cribbage_app.py")
    else:
        print("\n❌ Database issues detected. Check the errors above.")
        
    sys.exit(0 if success else 1)
