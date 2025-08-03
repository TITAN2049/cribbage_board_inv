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
            print(f"Deleted file: {filename}")
    except Exception as e:
        print(f"Error deleting file {filename}: {e}")

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

@app.route("/")
def index():
    try:
        boards = execute_query("SELECT * FROM boards ORDER BY id DESC", fetch=True)
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
            roman_number = request.form["roman_number"]
            description = request.form.get("description", "")
            wood_type = request.form.get("wood_type", "")
            material_type = request.form.get("material_type", "")
            
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
            execute_query("""
                INSERT INTO boards (date, roman_number, description, wood_type, material_type,
                                  image_front, image_back, 
                                  in_collection, is_gift, gifted_to, gifted_from)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, [date, roman_number, description, wood_type, material_type,
                  front_filename, back_filename,
                  in_collection, is_gift, gifted_to, gifted_from])
            
            flash("Board added successfully!", "success")
            return redirect(url_for("index"))
            
        except Exception as e:
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
            wood_type = request.form.get("wood_type", "")
            material_type = request.form.get("material_type", "")
            
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
        players = execute_query("SELECT * FROM players ORDER BY first_name, last_name", fetch=True)
        return render_template("players.html", players=players)
    except Exception as e:
        flash(f"Database error: {e}", "error")
        return render_template("players.html", players=[])

@app.route("/add_player", methods=["POST"])
def add_player():
    try:
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        
        # Handle photo upload
        photo = request.files.get("photo")
        photo_filename = None
        
        if photo and photo.filename:
            photo_filename = generate_unique_filename(photo.filename, "player")
            photo.save(os.path.join(app.config["UPLOAD_FOLDER"], photo_filename))
        
        execute_query("""
            INSERT INTO players (first_name, last_name, photo) 
            VALUES (?, ?, ?)
        """, [first_name, last_name, photo_filename])
        
        flash("Player added successfully!", "success")
        
    except Exception as e:
        flash(f"Error adding player: {e}", "error")
    
    return redirect(url_for("players"))

@app.route("/player/<int:player_id>")
def player_detail(player_id):
    try:
        player = execute_query("SELECT * FROM players WHERE id = ?", [player_id], fetch=True)
        if not player:
            flash("Player not found!", "error")
            return redirect(url_for("players"))
        
        games = execute_query("""
            SELECT g.*, 
                   p1.first_name || ' ' || p1.last_name as player1_name,
                   p2.first_name || ' ' || p2.last_name as player2_name
            FROM games g
            LEFT JOIN players p1 ON g.player1_id = p1.id
            LEFT JOIN players p2 ON g.player2_id = p2.id
            WHERE g.player1_id = ? OR g.player2_id = ?
            ORDER BY g.date_played DESC
        """, [player_id, player_id], fetch=True)
        
        return render_template("player_detail.html", player=player[0], games=games)
        
    except Exception as e:
        flash(f"Database error: {e}", "error")
        return redirect(url_for("players"))

@app.route("/games")
def games():
    try:
        games = execute_query("""
            SELECT g.*, 
                   p1.first_name || ' ' || p1.last_name as player1_name,
                   p2.first_name || ' ' || p2.last_name as player2_name,
                   b.roman_number as board_number
            FROM games g
            LEFT JOIN players p1 ON g.player1_id = p1.id
            LEFT JOIN players p2 ON g.player2_id = p2.id
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
        player1_id = request.form["player1_id"]
        player2_id = request.form["player2_id"]
        board_id = request.form["board_id"]
        player1_score = int(request.form["player1_score"])
        player2_score = int(request.form["player2_score"])
        date_played = request.form["date_played"]
        notes = request.form.get("notes", "")
        
        execute_query("""
            INSERT INTO games (player1_id, player2_id, board_id, player1_score, player2_score, date_played, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, [player1_id, player2_id, board_id, player1_score, player2_score, date_played, notes])
        
        flash("Game recorded successfully!", "success")
        
    except Exception as e:
        flash(f"Error recording game: {e}", "error")
    
    return redirect(url_for("games"))

@app.route("/stats")
def stats():
    try:
        # Basic stats
        board_count = execute_query("SELECT COUNT(*) as count FROM boards", fetch=True)[0]['count']
        player_count = execute_query("SELECT COUNT(*) as count FROM players", fetch=True)[0]['count']
        game_count = execute_query("SELECT COUNT(*) as count FROM games", fetch=True)[0]['count']
        
        # Collection stats
        in_collection = execute_query("SELECT COUNT(*) as count FROM boards WHERE in_collection = 1", fetch=True)[0]['count']
        gifts_given = execute_query("SELECT COUNT(*) as count FROM boards WHERE is_gift = 1", fetch=True)[0]['count']
        
        # Top players
        top_players = execute_query("""
            SELECT p.first_name || ' ' || p.last_name as name, COUNT(*) as games_played
            FROM games g
            JOIN players p ON (g.player1_id = p.id OR g.player2_id = p.id)
            GROUP BY p.id, p.first_name, p.last_name
            ORDER BY games_played DESC
            LIMIT 5
        """, fetch=True)
        
        stats = {
            'board_count': board_count,
            'player_count': player_count,
            'game_count': game_count,
            'in_collection': in_collection,
            'gifts_given': gifts_given,
            'top_players': top_players
        }
        
        return render_template("stats.html", stats=stats)
        
    except Exception as e:
        flash(f"Database error: {e}", "error")
        return render_template("stats.html", stats={})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = not is_production()
    app.run(host="0.0.0.0", port=port, debug=debug)
