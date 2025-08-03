#!/usr/bin/env python3
"""
Hybrid Flask App for Cribbage Board Collection
Works with both PostgreSQL (Railway) and SQLite (local)
"""

import os
import sqlite3
import time
import uuid
from flask import Flask, request, redirect, url_for, render_template, flash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-key-change-in-production")

# Configuration
app.config["UPLOAD_FOLDER"] = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "uploads")
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB limit

# Ensure upload directory exists
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

def is_production():
    """Check if running in production (Railway deployment)"""
    return "RAILWAY_ENVIRONMENT" in os.environ

def execute_query(query, params=None, fetch=False):
    """Execute database query with automatic database selection"""
    params = params or []
    
    if is_production():
        # Production: Use PostgreSQL
        try:
            import psycopg2
            from psycopg2.extras import RealDictCursor
            
            DATABASE_URL = os.environ.get("DATABASE_URL")
            if not DATABASE_URL:
                raise Exception("DATABASE_URL not found in environment")
            
            conn = psycopg2.connect(DATABASE_URL)
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(query, params)
            
            if fetch:
                result = cursor.fetchall()
            else:
                result = None
                conn.commit()
            
            cursor.close()
            conn.close()
            return result
            
        except Exception as e:
            print(f"PostgreSQL Error: {e}")
            raise
    else:
        # Development: Use SQLite
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database.db")
        
        try:
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, params)
            
            if fetch:
                result = cursor.fetchall()
            else:
                result = None
                conn.commit()
            
            cursor.close()
            conn.close()
            return result
            
        except Exception as e:
            print(f"SQLite Error: {e}")
            raise

def generate_unique_filename(original_filename, prefix="board"):
    """Generate a unique filename for uploaded files"""
    if not original_filename:
        return None
    
    # Get file extension
    extension = os.path.splitext(secure_filename(original_filename))[1].lower() or ".jpg"
    
    # Generate unique filename with timestamp and random component
    return f"{prefix}_{int(time.time())}_{uuid.uuid4().hex[:8]}{extension}"

def safe_delete_file(filename):
    """Safely delete a file from uploads directory"""
    if not filename:
        return
    
    timestamp = int(time.time())
    unique_id = uuid.uuid4().hex[:8]
    
    try:
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        pass  # Silently handle file deletion errors

@app.route("/uploads/<filename>")
def uploaded_file(filename):
    """Serve uploaded files"""
    try:
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        if os.path.exists(file_path):
            from flask import send_file
            return send_file(file_path)
        else:
            return "File not found", 404
    except Exception as e:
        return f"Error serving file: {e}", 500

# ================================
# PLAYER STATISTICS FUNCTIONS
# ================================

def calculate_player_stats(player_id):
    """Calculate comprehensive statistics for a player"""
    try:
        # Basic win/loss stats
        wins = execute_query("SELECT COUNT(*) as count FROM games WHERE winner_id = ?", [player_id], fetch=True)[0]['count']
        losses = execute_query("SELECT COUNT(*) as count FROM games WHERE loser_id = ?", [player_id], fetch=True)[0]['count']
        
        # Skunk stats (games won/lost by >30 points)
        skunks_given = execute_query("""
            SELECT COUNT(*) as count FROM games 
            WHERE winner_id = ? AND (winner_score - loser_score) >= 30
        """, [player_id], fetch=True)[0]['count']
        
        skunks_received = execute_query("""
            SELECT COUNT(*) as count FROM games 
            WHERE loser_id = ? AND (winner_score - loser_score) >= 30
        """, [player_id], fetch=True)[0]['count']
        
        # Double skunks (won/lost by >60 points)
        double_skunks_given = execute_query("""
            SELECT COUNT(*) as count FROM games 
            WHERE winner_id = ? AND (winner_score - loser_score) >= 60
        """, [player_id], fetch=True)[0]['count']
        
        double_skunks_received = execute_query("""
            SELECT COUNT(*) as count FROM games 
            WHERE loser_id = ? AND (winner_score - loser_score) >= 60
        """, [player_id], fetch=True)[0]['count']
        
        # Average scores
        avg_winning_score = execute_query("""
            SELECT AVG(winner_score) as avg FROM games WHERE winner_id = ?
        """, [player_id], fetch=True)[0]['avg'] or 0
        
        avg_losing_score = execute_query("""
            SELECT AVG(loser_score) as avg FROM games WHERE loser_id = ?
        """, [player_id], fetch=True)[0]['avg'] or 0
        
        # Recent form (last 10 games)
        recent_games = execute_query("""
            SELECT CASE WHEN winner_id = ? THEN 'W' ELSE 'L' END as result
            FROM games 
            WHERE winner_id = ? OR loser_id = ?
            ORDER BY date_played DESC 
            LIMIT 10
        """, [player_id, player_id, player_id], fetch=True)
        
        recent_wins = sum(1 for game in recent_games if game['result'] == 'W')
        recent_form = f"{recent_wins}/{len(recent_games)}" if recent_games else "0/0"
        
        # Current streak calculation
        current_streak = 0
        if recent_games:
            streak_type = recent_games[0]['result'] if recent_games else None
            for game in recent_games:
                if game['result'] == streak_type:
                    current_streak += 1
                else:
                    break
            current_streak = f"{current_streak}{'W' if streak_type == 'W' else 'L'}"
        else:
            current_streak = "0"
        
        # Find favorite opponent (who they beat the most)
        favorite_opponent = None
        try:
            opponent_stats = execute_query("""
                SELECT p.id, p.first_name || ' ' || p.last_name as name,
                       COUNT(CASE WHEN g.winner_id = ? THEN 1 END) as wins_against_them,
                       COUNT(CASE WHEN g.loser_id = ? THEN 1 END) as losses_to_them,
                       COUNT(*) as total_games
                FROM games g
                JOIN players p ON (g.winner_id = p.id OR g.loser_id = p.id)
                WHERE (g.winner_id = ? OR g.loser_id = ?) AND p.id != ?
                GROUP BY p.id, p.first_name, p.last_name
                HAVING COUNT(CASE WHEN g.winner_id = ? THEN 1 END) > 0
                ORDER BY wins_against_them DESC, total_games DESC
                LIMIT 1
            """, [player_id, player_id, player_id, player_id, player_id, player_id], fetch=True)
            
            if opponent_stats:
                opp = opponent_stats[0]
                favorite_opponent = {
                    'id': opp['id'],
                    'name': opp['name'],
                    'wins_against_them': opp['wins_against_them'],
                    'losses_to_them': opp['losses_to_them'],
                    'total_games': opp['total_games'],
                    'win_rate_against': round((opp['wins_against_them'] / opp['total_games'] * 100), 1) if opp['total_games'] > 0 else 0
                }
        except Exception as e:
            print(f"Error finding favorite opponent: {e}")
        
        return {
            'wins': wins,
            'losses': losses,
            'total_games': wins + losses,
            'win_percentage': round((wins / (wins + losses) * 100), 1) if (wins + losses) > 0 else 0,
            'skunks_given': skunks_given,
            'skunks_received': skunks_received,
            'double_skunks_given': double_skunks_given,
            'double_skunks_received': double_skunks_received,
            'avg_winning_score': round(avg_winning_score, 1),
            'avg_losing_score': round(avg_losing_score, 1),
            'recent_form': recent_form,
            'recent_wins': recent_wins,
            'recent_games_count': len(recent_games),
            'current_streak': current_streak,
            'favorite_opponent': favorite_opponent
        }
        
    except Exception as e:
        print(f"Error calculating player stats: {e}")
        return {
            'wins': 0, 'losses': 0, 'total_games': 0, 'win_percentage': 0,
            'skunks_given': 0, 'skunks_received': 0,
            'double_skunks_given': 0, 'double_skunks_received': 0,
            'avg_winning_score': 0, 'avg_losing_score': 0,
            'recent_form': '0/0', 'recent_wins': 0, 'recent_games_count': 0,
            'current_streak': '0', 'favorite_opponent': None
        }

def get_player_nemesis(player_id):
    """Find the player's nemesis (opponent they've lost to most)"""
    try:
        nemesis_data = execute_query("""
            SELECT p.id, p.first_name || ' ' || p.last_name as name, 
                   COUNT(*) as losses_to_them,
                   (SELECT COUNT(*) FROM games g2 WHERE g2.winner_id = ? AND g2.loser_id = p.id) as wins_against_them
            FROM games g
            JOIN players p ON g.winner_id = p.id
            WHERE g.loser_id = ?
            GROUP BY p.id, p.first_name, p.last_name
            ORDER BY losses_to_them DESC, wins_against_them ASC
            LIMIT 1
        """, [player_id, player_id], fetch=True)
        
        if nemesis_data:
            nemesis = nemesis_data[0]
            total_games = nemesis['losses_to_them'] + nemesis['wins_against_them']
            return {
                'id': nemesis['id'],
                'name': nemesis['name'],
                'losses_to_them': nemesis['losses_to_them'],
                'wins_against_them': nemesis['wins_against_them'],
                'total_games': total_games,
                'win_rate_against': round((nemesis['wins_against_them'] / total_games * 100), 1) if total_games > 0 else 0
            }
        return None
        
    except Exception as e:
        print(f"Error finding nemesis: {e}")
        return None

def get_player_leaderboard_position(player_id):
    """Get player's position in various leaderboards"""
    try:
        # Overall win rate leaderboard
        leaderboard = execute_query("""
            SELECT p.id,
                   p.first_name || ' ' || p.last_name as name,
                   COUNT(CASE WHEN g.winner_id = p.id THEN 1 END) as wins,
                   COUNT(CASE WHEN g.loser_id = p.id THEN 1 END) as losses,
                   (COUNT(CASE WHEN g.winner_id = p.id THEN 1 END) * 100.0 / 
                    (COUNT(CASE WHEN g.winner_id = p.id THEN 1 END) + COUNT(CASE WHEN g.loser_id = p.id THEN 1 END))) as win_rate
            FROM players p
            LEFT JOIN games g ON (g.winner_id = p.id OR g.loser_id = p.id)
            GROUP BY p.id, p.first_name, p.last_name
            HAVING (COUNT(CASE WHEN g.winner_id = p.id THEN 1 END) + COUNT(CASE WHEN g.loser_id = p.id THEN 1 END)) > 0
            ORDER BY win_rate DESC, wins DESC
        """, fetch=True)
        
        # Find player's position
        for i, player in enumerate(leaderboard):
            if player['id'] == player_id:
                return {
                    'position': i + 1,
                    'total_players': len(leaderboard),
                    'win_rate': round(player['win_rate'], 1) if player['win_rate'] else 0,
                    'wins': player['wins'],
                    'losses': player['losses']
                }
        
        return None
        
    except Exception as e:
        print(f"Error getting leaderboard position: {e}")
        return None

# ================================
# ROUTES
# ================================

@app.route("/")
def index():
    try:
        # Get filter parameters
        filter_collection = request.args.get('filter_collection')
        filter_gift = request.args.get('filter_gift')
        filter_wood = request.args.get('filter_wood')
        filter_material = request.args.get('filter_material')
        search = request.args.get('search')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        # Base query
        query = "SELECT * FROM boards WHERE 1=1"
        params = []
        
        # Apply filters
        if filter_collection:
            query += " AND in_collection = ?"
            params.append(int(filter_collection))
        
        if filter_gift:
            query += " AND is_gift = ?"
            params.append(int(filter_gift))
        
        if filter_wood:
            query += " AND LOWER(wood_type) LIKE ?"
            params.append(f"%{filter_wood.lower()}%")
        
        if filter_material:
            query += " AND LOWER(material_type) LIKE ?"
            params.append(f"%{filter_material.lower()}%")
        
        if search:
            query += " AND (LOWER(description) LIKE ? OR LOWER(gifted_to) LIKE ? OR LOWER(gifted_from) LIKE ? OR LOWER(roman_number) LIKE ?)"
            search_param = f"%{search.lower()}%"
            params.extend([search_param, search_param, search_param, search_param])
        
        if date_from:
            query += " AND date >= ?"
            params.append(date_from)
        
        if date_to:
            query += " AND date <= ?"
            params.append(date_to)
        
        # Add ordering
        query += " ORDER BY id DESC"
        
        boards = execute_query(query, params, fetch=True)
        return render_template("index.html", boards=boards)
        
    except Exception as e:
        flash(f"Database error: {e}", "error")
        return render_template("index.html", boards=[])

@app.route("/board/<int:board_id>")
def board_detail(board_id):
    try:
        board = execute_query("SELECT * FROM boards WHERE id = ?", [board_id], fetch=True)
        if not board:
            flash("Board not found!", "error")
            return redirect(url_for("index"))
        return render_template("board_detail.html", board=board[0])
    except Exception as e:
        flash(f"Database error: {e}", "error")
        return redirect(url_for("index"))

@app.route("/add_board", methods=["GET", "POST"])
def add_board():
    if request.method == "POST":
        try:
            # Get form data
            date = request.form.get("date", "")
            roman_number = request.form.get("roman_number", "")
            description = request.form.get("description", "")
            
            # Handle material type (check for custom input)
            material_type = request.form.get("material_type", "")
            custom_material = request.form.get("custom_material_type", "")
            if material_type == "Other" and custom_material:
                material_type = custom_material
                # Add to material_types table for future reference
                try:
                    execute_query("INSERT OR IGNORE INTO material_types (name) VALUES (?)", [custom_material])
                except:
                    pass  # Ignore if table doesn't exist or other errors
            
            # Handle wood type (check for custom input)
            wood_type = request.form.get("wood_type", "")
            custom_wood = request.form.get("custom_wood_type", "")
            if wood_type == "Other" and custom_wood:
                wood_type = custom_wood
                # Add to wood_types table for future reference
                try:
                    execute_query("INSERT OR IGNORE INTO wood_types (name) VALUES (?)", [custom_wood])
                except:
                    pass  # Ignore if table doesn't exist or other errors
            
            # Validate required field
            if not roman_number:
                flash("Roman Number is required!", "error")
                return render_template("add_board.html")
            
            # Handle collection and gift status
            in_collection = 1 if request.form.get("in_collection") else 0
            is_gift = 1 if request.form.get("is_gift") else 0
            gifted_to = request.form.get("gifted_to", "") if is_gift else ""
            gifted_from = request.form.get("gifted_from", "") if is_gift else ""
            
            # Handle file uploads
            front_view = request.files.get("front_view")
            back_view = request.files.get("back_view")
            
            front_filename = None
            back_filename = None
            
            if front_view and front_view.filename:
                front_filename = generate_unique_filename(front_view.filename, "front")
                front_view.save(os.path.join(app.config["UPLOAD_FOLDER"], front_filename))
            
            if back_view and back_view.filename:
                back_filename = generate_unique_filename(back_view.filename, "back")
                back_view.save(os.path.join(app.config["UPLOAD_FOLDER"], back_filename))
            
            # Insert into database
            insert_params = [date, roman_number, description, wood_type, material_type,
                           front_filename, back_filename,
                           in_collection, is_gift, gifted_to, gifted_from]
            
            execute_query("""
                INSERT INTO boards (date, roman_number, description, wood_type, material_type,
                                  image_front, image_back, 
                                  in_collection, is_gift, gifted_to, gifted_from)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, insert_params)
            
            flash("Board added successfully!", "success")
            return redirect(url_for("index"))
            
        except Exception as e:
            print(f"Exception in add_board: {e}")
            flash(f"Error adding board: {e}", "error")
    
    return render_template("add_board.html")

@app.route("/edit_board/<int:board_id>", methods=["GET", "POST"])
def edit_board(board_id):
    if request.method == "POST":
        try:
            # Get form data
            date = request.form.get("date", "")
            roman_number = request.form.get("roman_number", "")
            description = request.form.get("description", "")
            
            # Handle material type (check for custom input)
            material_type = request.form.get("material_type", "")
            custom_material = request.form.get("custom_material_type", "")
            if material_type == "Other" and custom_material:
                material_type = custom_material
                # Add to material_types table for future reference
                try:
                    execute_query("INSERT OR IGNORE INTO material_types (name) VALUES (?)", [custom_material])
                except:
                    pass  # Ignore if table doesn't exist or other errors
            
            # Handle wood type (check for custom input)
            wood_type = request.form.get("wood_type", "")
            custom_wood = request.form.get("custom_wood_type", "")
            if wood_type == "Other" and custom_wood:
                wood_type = custom_wood
                # Add to wood_types table for future reference
                try:
                    execute_query("INSERT OR IGNORE INTO wood_types (name) VALUES (?)", [custom_wood])
                except:
                    pass  # Ignore if table doesn't exist or other errors
            
            # Handle collection and gift status
            in_collection = 1 if request.form.get("in_collection") else 0
            is_gift = 1 if request.form.get("is_gift") else 0
            gifted_to = request.form.get("gifted_to", "") if is_gift else ""
            gifted_from = request.form.get("gifted_from", "") if is_gift else ""
            
            # Debug: Print form data
            print(f"DEBUG - Form data received:")
            print(f"  Date: '{date}'")
            print(f"  Roman Number: '{roman_number}'")
            print(f"  Description: '{description}'")
            print(f"  Wood Type: '{wood_type}'")
            print(f"  Material Type: '{material_type}'")
            print(f"  In Collection: {in_collection}")
            print(f"  Is Gift: {is_gift}")
            print(f"  Gifted To: '{gifted_to}'")
            print(f"  Gifted From: '{gifted_from}'")
            
            # Get current board to check for existing images
            current_board = execute_query("SELECT * FROM boards WHERE id = ?", [board_id], fetch=True)
            if not current_board:
                flash("Board not found!", "error")
                return redirect(url_for("index"))
            
            current_board = current_board[0]
            
            # Handle file uploads
            front_view = request.files.get("front_view")
            back_view = request.files.get("back_view")
            
            front_filename = current_board['image_front']
            back_filename = current_board['image_back']
            
            # Upload new front image if provided
            if front_view and front_view.filename:
                # Delete old image if it exists
                if front_filename:
                    safe_delete_file(front_filename)
                front_filename = generate_unique_filename(front_view.filename, "front")
                front_view.save(os.path.join(app.config["UPLOAD_FOLDER"], front_filename))
            
            # Upload new back image if provided
            if back_view and back_view.filename:
                # Delete old image if it exists
                if back_filename:
                    safe_delete_file(back_filename)
                back_filename = generate_unique_filename(back_view.filename, "back")
                back_view.save(os.path.join(app.config["UPLOAD_FOLDER"], back_filename))
            
            # Update database
            update_params = [date, roman_number, description, wood_type, material_type,
                           front_filename, back_filename,
                           in_collection, is_gift, gifted_to, gifted_from, board_id]
            
            print(f"DEBUG - Update parameters: {update_params}")
            
            execute_query("""
                UPDATE boards SET date = ?, roman_number = ?, description = ?, wood_type = ?, material_type = ?,
                                image_front = ?, image_back = ?, 
                                in_collection = ?, is_gift = ?, gifted_to = ?, gifted_from = ?
                WHERE id = ?
            """, update_params)
            
            flash("Board updated successfully!", "success")
            return redirect(url_for("board_detail", board_id=board_id))
            
        except Exception as e:
            flash(f"Error updating board: {e}", "error")
    
    # GET request - show the edit form
    try:
        board = execute_query("SELECT * FROM boards WHERE id = ?", [board_id], fetch=True)
        if not board:
            flash("Board not found!", "error")
            return redirect(url_for("index"))
        return render_template("edit_board.html", board=board[0])
    except Exception as e:
        flash(f"Database error: {e}", "error")
        return redirect(url_for("index"))

@app.route("/delete_board/<int:board_id>", methods=["POST"])
def delete_board(board_id):
    try:
        # Get board info to delete associated images
        board = execute_query("SELECT * FROM boards WHERE id = ?", [board_id], fetch=True)
        if not board:
            flash("Board not found!", "error")
            return redirect(url_for("index"))
        
        board = board[0]
        
        # Delete associated images
        if board['image_front']:
            safe_delete_file(board['image_front'])
        if board['image_back']:
            safe_delete_file(board['image_back'])
        
        # Delete board from database
        execute_query("DELETE FROM boards WHERE id = ?", [board_id])
        
        flash("Board deleted successfully!", "success")
        return redirect(url_for("index"))
        
    except Exception as e:
        flash(f"Error deleting board: {e}", "error")
        return redirect(url_for("index"))

@app.route("/players")
def players():
    try:
        # Get all players with their game statistics
        players = execute_query("""
            SELECT p.*,
                   COUNT(CASE WHEN g.winner_id = p.id THEN 1 END) as wins,
                   COUNT(CASE WHEN g.loser_id = p.id THEN 1 END) as losses
            FROM players p
            LEFT JOIN games g ON (g.winner_id = p.id OR g.loser_id = p.id)
            GROUP BY p.id, p.first_name, p.last_name, p.photo, p.date_added
            ORDER BY p.first_name, p.last_name
        """, fetch=True)
        
        # Calculate additional stats
        active_players = len([p for p in players if (p['wins'] or 0) + (p['losses'] or 0) > 0])
        total_games = execute_query("SELECT COUNT(*) as count FROM games", fetch=True)[0]['count']
        
        return render_template("players.html", 
                             players=players, 
                             active_players=active_players, 
                             total_games=total_games)
        
    except Exception as e:
        flash(f"Database error: {e}", "error")
        return render_template("players.html", players=[], active_players=0, total_games=0)

@app.route("/add_player", methods=["POST"])
def add_player():
    try:
        # Debug: Print all form data
        print(f"DEBUG - Add Player Form data received:")
        print(f"  Form keys: {list(request.form.keys())}")
        print(f"  Files keys: {list(request.files.keys())}")
        
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        
        print(f"  First Name: '{first_name}'")
        print(f"  Last Name: '{last_name}'")
        
        # Handle photo upload
        photo = request.files.get("photo")
        photo_filename = None
        
        if photo and photo.filename:
            photo_filename = generate_unique_filename(photo.filename, "player")
            photo.save(os.path.join(app.config["UPLOAD_FOLDER"], photo_filename))
            print(f"  Photo saved: {photo_filename}")
        else:
            print(f"  No photo uploaded")
        
        print(f"  Insert parameters: {[first_name, last_name, photo_filename]}")
        
        execute_query("""
            INSERT INTO players (first_name, last_name, photo) 
            VALUES (?, ?, ?)
        """, [first_name, last_name, photo_filename])
        
        flash("Player added successfully!", "success")
        
    except Exception as e:
        print(f"Exception in add_player: {e}")
        flash(f"Error adding player: {e}", "error")
    
    return redirect(url_for("players"))

@app.route("/edit_player/<int:player_id>", methods=["GET", "POST"])
def edit_player(player_id):
    if request.method == "POST":
        try:
            first_name = request.form["first_name"]
            last_name = request.form["last_name"]
            
            # Get current player to check for existing photo
            current_player = execute_query("SELECT * FROM players WHERE id = ?", [player_id], fetch=True)
            if not current_player:
                flash("Player not found!", "error")
                return redirect(url_for("players"))
            
            current_player = current_player[0]
            
            # Handle photo upload
            photo = request.files.get("photo")
            photo_filename = current_player['photo']
            
            if photo and photo.filename:
                # Delete old photo if it exists
                if photo_filename:
                    safe_delete_file(photo_filename)
                photo_filename = generate_unique_filename(photo.filename, "player")
                photo.save(os.path.join(app.config["UPLOAD_FOLDER"], photo_filename))
            
            execute_query("""
                UPDATE players SET first_name = ?, last_name = ?, photo = ?
                WHERE id = ?
            """, [first_name, last_name, photo_filename, player_id])
            
            flash("Player updated successfully!", "success")
            return redirect(url_for("player_detail", player_id=player_id))
            
        except Exception as e:
            flash(f"Error updating player: {e}", "error")
    
    # GET request - show the edit form
    try:
        player = execute_query("SELECT * FROM players WHERE id = ?", [player_id], fetch=True)
        if not player:
            flash("Player not found!", "error")
            return redirect(url_for("players"))
        return render_template("edit_player.html", player=player[0])
    except Exception as e:
        flash(f"Database error: {e}", "error")
        return redirect(url_for("players"))

@app.route("/delete_player/<int:player_id>", methods=["POST"])
def delete_player(player_id):
    try:
        # Get player info to delete associated images
        player = execute_query("SELECT * FROM players WHERE id = ?", [player_id], fetch=True)
        if not player:
            flash("Player not found!", "error")
            return redirect(url_for("players"))
        
        player = player[0]
        
        # Delete associated photo
        if player['photo']:
            safe_delete_file(player['photo'])
        
        # Delete player from database
        execute_query("DELETE FROM players WHERE id = ?", [player_id])
        
        flash("Player deleted successfully!", "success")
        return redirect(url_for("players"))
        
    except Exception as e:
        flash(f"Error deleting player: {e}", "error")
        return redirect(url_for("players"))

@app.route("/player/<int:player_id>")
def player_detail(player_id):
    try:
        player = execute_query("SELECT * FROM players WHERE id = ?", [player_id], fetch=True)
        if not player:
            flash("Player not found!", "error")
            return redirect(url_for("players"))
        
        # Get all games for this player
        games = execute_query("""
            SELECT g.*, 
                   pw.first_name || ' ' || pw.last_name as winner,
                   pl.first_name || ' ' || pl.last_name as loser,
                   CASE 
                       WHEN g.winner_id = ? THEN 'W'
                       ELSE 'L'
                   END as result
            FROM games g
            LEFT JOIN players pw ON g.winner_id = pw.id
            LEFT JOIN players pl ON g.loser_id = pl.id
            WHERE g.winner_id = ? OR g.loser_id = ?
            ORDER BY g.date_played DESC
        """, [player_id, player_id, player_id], fetch=True)
        
        # Calculate comprehensive statistics
        stats = calculate_player_stats(player_id)
        
        # Get nemesis (most frequent opponent they've lost to)
        nemesis = get_player_nemesis(player_id)
        
        # Get recent games (limit 10)
        recent_games = games[:10] if games else []
        
        # Get leaderboard position
        leaderboard_position = get_player_leaderboard_position(player_id)
        
        return render_template("player_detail.html", 
                             player=player[0], 
                             games=games,
                             recent_games=recent_games,
                             stats=stats,
                             nemesis=nemesis,
                             leaderboard_position=leaderboard_position)
        
    except Exception as e:
        flash(f"Database error: {e}", "error")
        return redirect(url_for("players"))

@app.route("/games")
def games():
    try:
        games = execute_query("""
            SELECT g.*, 
                   pw.first_name || ' ' || pw.last_name as winner,
                   pl.first_name || ' ' || pl.last_name as loser,
                   b.roman_number
            FROM games g
            LEFT JOIN players pw ON g.winner_id = pw.id
            LEFT JOIN players pl ON g.loser_id = pl.id
            LEFT JOIN boards b ON g.board_id = b.id
            ORDER BY g.date_played DESC
        """, fetch=True)
        
        players = execute_query("SELECT * FROM players ORDER BY first_name, last_name", fetch=True)
        boards = execute_query("SELECT * FROM boards ORDER BY roman_number", fetch=True)
        
        return render_template("games.html", games=games, players=players, boards=boards)
        
    except Exception as e:
        flash(f"Database error: {e}", "error")
        return render_template("games.html", games=[], players=[], boards=[])

@app.route("/add_game", methods=["POST"])
def add_game():
    try:
        winner_id = request.form["winner_id"]
        loser_id = request.form["loser_id"]
        board_id = request.form.get("board_id") or None  # Optional field
        date_played = request.form["date_played"]
        winner_score = request.form.get("winner_score") or 121
        loser_score = request.form.get("loser_score") or 0
        notes = request.form.get("notes", "")
        
        # Determine skunk status based on scores
        loser_score_int = int(loser_score)
        is_double_skunk = 1 if loser_score_int < 61 else 0
        is_skunk = 1 if loser_score_int < 91 and not is_double_skunk else 0
        
        insert_params = [winner_id, loser_id, board_id, winner_score, loser_score, date_played, is_skunk, is_double_skunk, notes]
        
        execute_query("""
            INSERT INTO games (winner_id, loser_id, board_id, winner_score, loser_score, date_played, is_skunk, is_double_skunk, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, insert_params)
        
        flash("Game recorded successfully!", "success")
        
    except Exception as e:
        flash(f"Error recording game: {e}", "error")
    
    return redirect(url_for("games"))

@app.route("/game/<int:game_id>/edit", methods=["GET", "POST"])
def edit_game(game_id):
    try:
        if request.method == "GET":
            # Get game data for editing
            game = execute_query("""
                SELECT g.*, 
                       pw.first_name || ' ' || pw.last_name as winner_name,
                       pl.first_name || ' ' || pl.last_name as loser_name,
                       b.roman_number
                FROM games g
                LEFT JOIN players pw ON g.winner_id = pw.id
                LEFT JOIN players pl ON g.loser_id = pl.id
                LEFT JOIN boards b ON g.board_id = b.id
                WHERE g.id = ?
            """, [game_id], fetch=True)
            
            if not game:
                flash("Game not found", "error")
                return redirect(url_for("games"))
            
            players = execute_query("SELECT * FROM players ORDER BY first_name, last_name", fetch=True)
            boards = execute_query("SELECT * FROM boards ORDER BY roman_number", fetch=True)
            
            return render_template("edit_game.html", game=game[0], players=players, boards=boards)
        
        else:  # POST - update game
            winner_id = request.form["winner_id"]
            loser_id = request.form["loser_id"]
            board_id = request.form.get("board_id") or None
            date_played = request.form["date_played"]
            winner_score = request.form.get("winner_score", 121)
            loser_score = request.form.get("loser_score", 0)
            notes = request.form.get("notes", "")
            
            # Determine skunk status based on scores
            loser_score_int = int(loser_score)
            is_double_skunk = 1 if loser_score_int < 61 else 0
            is_skunk = 1 if loser_score_int < 91 and not is_double_skunk else 0
            
            execute_query("""
                UPDATE games 
                SET winner_id = ?, loser_id = ?, board_id = ?, winner_score = ?, 
                    loser_score = ?, date_played = ?, is_skunk = ?, is_double_skunk = ?, notes = ?
                WHERE id = ?
            """, [winner_id, loser_id, board_id, winner_score, loser_score, date_played, is_skunk, is_double_skunk, notes, game_id])
            
            flash("Game updated successfully!", "success")
            return redirect(url_for("games"))
            
    except Exception as e:
        flash(f"Error editing game: {e}", "error")
        if request.method == "GET":
            return redirect(url_for("games"))
        else:
            return redirect(url_for("edit_game", game_id=game_id))

@app.route("/game/<int:game_id>/delete", methods=["POST"])
def delete_game(game_id):
    try:
        # Check if game exists
        game = execute_query("SELECT * FROM games WHERE id = ?", [game_id], fetch=True)
        if not game:
            flash("Game not found", "error")
            return redirect(url_for("games"))
        
        # Delete the game
        execute_query("DELETE FROM games WHERE id = ?", [game_id])
        flash("Game deleted successfully!", "success")
        
    except Exception as e:
        print(f"Exception in delete_game: {e}")
        flash(f"Error deleting game: {e}", "error")
    
    return redirect(url_for("games"))

@app.route("/stats")
def stats():
    try:
        # Get all data for the template
        boards = execute_query("SELECT * FROM boards", fetch=True)
        players = execute_query("SELECT * FROM players", fetch=True)
        games = execute_query("SELECT * FROM games", fetch=True)
        
        # Calculate comprehensive leaderboard data
        leaderboard = []
        if players and games:
            for player in players:
                player_stats = calculate_player_stats(player['id'])
                if player_stats['total_games'] > 0:  # Only include players with games
                    leaderboard_entry = {
                        'id': player['id'],
                        'first_name': player['first_name'],
                        'last_name': player['last_name'],
                        'photo': player['photo'] if 'photo' in player.keys() else None,
                        'wins': player_stats['wins'],
                        'losses': player_stats['losses'],
                        'total_games': player_stats['total_games'],
                        'win_percentage': player_stats['win_percentage'],
                        'skunks_given': player_stats['skunks_given'],
                        'skunks_received': player_stats['skunks_received'],
                        'double_skunks_given': player_stats['double_skunks_given'],
                        'double_skunks_received': player_stats['double_skunks_received'],
                        'avg_winning_score': player_stats['avg_winning_score'],
                        'current_streak': player_stats['current_streak'],
                        'recent_form': player_stats['recent_form']
                    }
                    leaderboard.append(leaderboard_entry)
            
            # Sort leaderboard by win percentage (desc), then by total wins (desc), then by total games (desc)
            leaderboard.sort(key=lambda x: (x['win_percentage'], x['wins'], x['total_games']), reverse=True)
        
        # Calculate nemesis data for each player
        player_nemesis = {}
        if players and games:
            for player in players:
                # Find who beat this player the most
                opponents = {}
                for game in games:
                    if game['loser_id'] == player['id']:
                        # Find winner name
                        winner = next((p for p in players if p['id'] == game['winner_id']), None)
                        if winner:
                            winner_name = f"{winner['first_name']} {winner['last_name']}"
                            opponents[winner_name] = opponents.get(winner_name, 0) + 1
                
                if opponents:
                    # Find the opponent who beat this player the most
                    nemesis = max(opponents.items(), key=lambda x: x[1])
                    player_nemesis[player['id']] = {
                        'name': nemesis[0],
                        'losses_to_them': nemesis[1]
                    }
        
        return render_template("stats.html", 
                             boards=boards, 
                             players=players, 
                             games=games, 
                             leaderboard=leaderboard,
                             player_nemesis=player_nemesis)
        
    except Exception as e:
        print(f"ERROR in stats route: {e}")
        flash(f"Database error: {e}", "error")
        return render_template("stats.html", boards=[], players=[], games=[], leaderboard=[], player_nemesis={})

@app.route("/leaderboard")
def leaderboard():
    """Display player leaderboard with various rankings"""
    try:
        # Get all players with their stats
        players_data = execute_query("""
            SELECT p.id,
                   p.first_name || ' ' || p.last_name as name,
                   p.first_name, p.last_name, p.photo,
                   COUNT(CASE WHEN g.winner_id = p.id THEN 1 END) as wins,
                   COUNT(CASE WHEN g.loser_id = p.id THEN 1 END) as losses,
                   (COUNT(CASE WHEN g.winner_id = p.id THEN 1 END) * 100.0 / 
                    NULLIF(COUNT(CASE WHEN g.winner_id = p.id THEN 1 END) + COUNT(CASE WHEN g.loser_id = p.id THEN 1 END), 0)) as win_rate,
                   COUNT(CASE WHEN g.winner_id = p.id AND (g.winner_score - g.loser_score) >= 30 THEN 1 END) as skunks_given,
                   COUNT(CASE WHEN g.loser_id = p.id AND (g.winner_score - g.loser_score) >= 30 THEN 1 END) as skunks_received
            FROM players p
            LEFT JOIN games g ON (g.winner_id = p.id OR g.loser_id = p.id)
            GROUP BY p.id, p.first_name, p.last_name, p.photo
            HAVING (COUNT(CASE WHEN g.winner_id = p.id THEN 1 END) + COUNT(CASE WHEN g.loser_id = p.id THEN 1 END)) > 0
            ORDER BY win_rate DESC, wins DESC
        """, fetch=True)
        
        # Calculate rankings
        win_rate_leaders = sorted(players_data, key=lambda x: (x['win_rate'] or 0, x['wins']), reverse=True)
        most_wins = sorted(players_data, key=lambda x: x['wins'], reverse=True)
        most_games = sorted(players_data, key=lambda x: x['wins'] + x['losses'], reverse=True)
        skunk_masters = sorted(players_data, key=lambda x: x['skunks_given'], reverse=True)
        
        return render_template("leaderboard.html", 
                             win_rate_leaders=win_rate_leaders,
                             most_wins=most_wins,
                             most_games=most_games,
                             skunk_masters=skunk_masters)
        
    except Exception as e:
        flash(f"Database error: {e}", "error")
        return render_template("leaderboard.html", 
                             win_rate_leaders=[], most_wins=[], most_games=[], skunk_masters=[])

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = not is_production()
    app.run(host="0.0.0.0", port=port, debug=debug)
