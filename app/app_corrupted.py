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
            
            # Handle collection and gift status
            in_collection = 1 if request.form.get("in_collection") else 0
            is_gift = 1 if request.form.get("is_gift") else 0
            gifted_to = request.form.get("gifted_to", "") if is_gift else ""
            gifted_from = request.form.get("gifted_from", "") if is_gift else ""ime
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, url_for, flash

# Check if we're on Railway (has DATABASE_URL)
DATABASE_URL = os.environ.get('DATABASE_URL')
IS_RAILWAY = bool(DATABASE_URL)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'cribbage_board_collection_secret_key_2024')

# Configure file uploads (Railway uses temp storage, local uses data directory)
if IS_RAILWAY:
    # On Railway, use temp storage (files will be lost on redeploy)
    app.config["UPLOAD_FOLDER"] = "/tmp/uploads"
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
else:
    # Local development - use data directory
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, "data")
    uploads_dir = os.path.join(data_dir, "uploads")
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(uploads_dir, exist_ok=True)
    app.config["UPLOAD_FOLDER"] = uploads_dir

def get_db():
    """Get database connection - PostgreSQL on Railway, SQLite locally"""
    if IS_RAILWAY:
        # Import here to avoid errors when psycopg2 is not installed locally
        import psycopg2
        from psycopg2.extras import RealDictCursor
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        return conn
    else:
        # SQLite for local development
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Try data directory first
        data_dir = os.path.join(base_dir, "data")
        db_path = os.path.join(data_dir, "database.db")
        
        # Fallback to app directory
        if not os.path.exists(db_path):
            app_dir = os.path.dirname(os.path.abspath(__file__))
            db_path = os.path.join(app_dir, "database.db")
        
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn

def execute_query(query, params=None, fetch=False):
    """Execute query with database-agnostic parameter handling"""
    if params is None:
        params = []
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        if IS_RAILWAY:
            # PostgreSQL uses $1, $2, etc. - convert from ?
            pg_query = query
            param_count = query.count('?')
            for i in range(param_count):
                pg_query = pg_query.replace('?', f'${i+1}', 1)
            cursor.execute(pg_query, params)
        else:
            # SQLite uses ?
            cursor.execute(query, params)
        
        if fetch:
            result = cursor.fetchall()
            cursor.close()
            conn.close()
            return result
        else:
            conn.commit()
            if IS_RAILWAY:
                # Get last inserted ID for PostgreSQL
                if query.strip().upper().startswith('INSERT'):
                    cursor.execute("SELECT LASTVAL()")
                    last_id = cursor.fetchone()[0]
                    cursor.close()
                    conn.close()
                    return last_id
            else:
                # Get last inserted ID for SQLite
                last_id = cursor.lastrowid
                cursor.close()
                conn.close()
                return last_id
            
            cursor.close()
            conn.close()
            
    except Exception as e:
        cursor.close()
        conn.close()
        raise e

def generate_unique_filename(original_filename, prefix=""):
    """Generate a unique filename to prevent overwrites"""
    if not original_filename:
        return f"{prefix}_{int(time.time())}_{uuid.uuid4().hex[:8]}.jpg"
    
    filename = secure_filename(original_filename)
    name, ext = os.path.splitext(filename)
    if not ext:
        ext = '.jpg'
    
    timestamp = int(time.time())
    unique_id = uuid.uuid4().hex[:8]
    return f"{prefix}_{timestamp}_{unique_id}_{name}{ext}"

def safe_delete_file(filename):
    """Safely delete a file if it exists"""
    if filename:
        try:
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Warning: Could not delete file {filename}: {e}")

@app.route("/uploads/<filename>")
def uploaded_file(filename):
    """Serve uploaded files (images)"""
    try:
        from flask import send_from_directory
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename)
    except Exception as e:
        print(f"Error serving file {filename}: {e}")
        # Return a placeholder image or 404
        from flask import abort
        abort(404)

@app.route("/")
def index():
    try:
        boards = execute_query("SELECT * FROM boards ORDER BY date DESC", fetch=True)
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
            # Get form data with safe defaults
            roman_number = request.form.get("roman_number", "")
            description = request.form.get("description", "")
            wood_type = request.form.get("wood_type", "")
            
            # Handle collection and gift status
            in_collection = 1 if request.form.get("in_collection") else 0
            is_gift = 1 if request.form.get("is_gift") else 0
            gifted_to = request.form.get("gifted_to", "") if is_gift else None
            gifted_from = request.form.get("gifted_from", "") if is_gift else None
            
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
                INSERT INTO boards (roman_number, description, wood_type, 
                                  image_front, image_back, 
                                  in_collection, is_gift, gifted_to, gifted_from)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, [roman_number, description, wood_type, 
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
            print(f"  Files: front_view={request.files.get('front_view', 'None')}, back_view={request.files.get('back_view', 'None')}")
            
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
        
        execute_query("INSERT INTO players (first_name, last_name, photo) VALUES (?, ?, ?)", 
                     [first_name, last_name, photo_filename])
        
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
        
        # Get player's game statistics
        stats = execute_query("""
            SELECT 
                COUNT(CASE WHEN winner_id = ? THEN 1 END) as wins,
                COUNT(CASE WHEN loser_id = ? THEN 1 END) as losses,
                COUNT(CASE WHEN winner_id = ? AND is_skunk = 1 THEN 1 END) as skunks_given,
                COUNT(CASE WHEN loser_id = ? AND is_skunk = 1 THEN 1 END) as skunks_received
            FROM games 
            WHERE winner_id = ? OR loser_id = ?
        """, [player_id, player_id, player_id, player_id, player_id, player_id], fetch=True)
        
        return render_template("player_detail.html", player=player[0], stats=stats[0] if stats else None)
    except Exception as e:
        flash(f"Database error: {e}", "error")
        return redirect(url_for("players"))

@app.route("/edit_player/<int:player_id>", methods=["GET", "POST"])
def edit_player(player_id):
    try:
        if request.method == "POST":
            first_name = request.form["first_name"]
            last_name = request.form["last_name"]
            
            # Get current player data
            current_player = execute_query("SELECT * FROM players WHERE id = ?", [player_id], fetch=True)
            if not current_player:
                flash("Player not found!", "error")
                return redirect(url_for("players"))
            
            current_photo = current_player[0]['photo'] if current_player[0]['photo'] else None
            
            # Handle photo upload
            photo = request.files.get("photo")
            photo_filename = current_photo  # Keep existing photo by default
            
            if photo and photo.filename:
                # Delete old photo if it exists
                if current_photo:
                    safe_delete_file(current_photo)
                
                # Save new photo
                photo_filename = generate_unique_filename(photo.filename, "player")
                photo.save(os.path.join(app.config["UPLOAD_FOLDER"], photo_filename))
            
            execute_query("""
                UPDATE players 
                SET first_name = ?, last_name = ?, photo = ?
                WHERE id = ?
            """, [first_name, last_name, photo_filename, player_id])
            
            flash("Player updated successfully!", "success")
            return redirect(url_for("player_detail", player_id=player_id))
        
        # GET request - show edit form
        player = execute_query("SELECT * FROM players WHERE id = ?", [player_id], fetch=True)
        if not player:
            flash("Player not found!", "error")
            return redirect(url_for("players"))
        
        return render_template("edit_player.html", player=player[0])
        
    except Exception as e:
        flash(f"Error updating player: {e}", "error")
        return redirect(url_for("players"))

@app.route("/delete_player/<int:player_id>", methods=["POST"])
def delete_player(player_id):
    try:
        # Get player data first to delete photo
        player = execute_query("SELECT * FROM players WHERE id = ?", [player_id], fetch=True)
        if player and player[0]['photo']:
            safe_delete_file(player[0]['photo'])
        
        # Check if player has any games
        games = execute_query("SELECT COUNT(*) as count FROM games WHERE winner_id = ? OR loser_id = ?", 
                             [player_id, player_id], fetch=True)
        
        if games and games[0]['count'] > 0:
            flash("Cannot delete player - they have game records!", "error")
        else:
            execute_query("DELETE FROM players WHERE id = ?", [player_id])
            flash("Player deleted successfully!", "success")
            
    except Exception as e:
        flash(f"Error deleting player: {e}", "error")
    
    return redirect(url_for("players"))

@app.route("/games")
def games():
    try:
        # Get games with player and board information
        games_query = """
            SELECT g.*, 
                   w.first_name || ' ' || w.last_name as winner,
                   l.first_name || ' ' || l.last_name as loser,
                   b.roman_number
            FROM games g
            JOIN players w ON g.winner_id = w.id
            JOIN players l ON g.loser_id = l.id
            JOIN boards b ON g.board_id = b.id
            ORDER BY g.date_played DESC, g.id DESC
        """
        
        if IS_RAILWAY:
            # PostgreSQL uses || for concatenation
            games = execute_query(games_query, fetch=True)
        else:
            # SQLite also supports ||
            games = execute_query(games_query, fetch=True)
        
        players = execute_query("SELECT * FROM players ORDER BY first_name, last_name", fetch=True)
        boards = execute_query("SELECT * FROM boards ORDER BY roman_number", fetch=True)
        
        return render_template("games.html", games=games, players=players, boards=boards)
        
    except Exception as e:
        flash(f"Database error: {e}", "error")
        return render_template("games.html", games=[], players=[], boards=[])

@app.route("/add_game", methods=["POST"])
def add_game():
    try:
        board_id = request.form["board_id"]
        winner_id = request.form["winner_id"]
        loser_id = request.form["loser_id"]
        date_played = request.form["date_played"]
        is_skunk = 'is_skunk' in request.form
        is_double_skunk = 'is_double_skunk' in request.form
        
        if winner_id == loser_id:
            flash("Winner and loser cannot be the same player!", "error")
            return redirect(url_for("games"))
        
        execute_query("""
            INSERT INTO games (board_id, winner_id, loser_id, date_played, is_skunk, is_double_skunk)
            VALUES (?, ?, ?, ?, ?, ?)
        """, [board_id, winner_id, loser_id, date_played, is_skunk, is_double_skunk])
        
        flash("Game recorded successfully!", "success")
        
    except Exception as e:
        flash(f"Error recording game: {e}", "error")
    
    return redirect(url_for("games"))

@app.route("/stats")
def stats():
    try:
        # Player statistics
        player_stats = execute_query("""
            SELECT p.first_name || ' ' || p.last_name as player_name,
                   COUNT(CASE WHEN g.winner_id = p.id THEN 1 END) as wins,
                   COUNT(CASE WHEN g.loser_id = p.id THEN 1 END) as losses,
                   COUNT(*) as total_games
            FROM players p
            LEFT JOIN games g ON (g.winner_id = p.id OR g.loser_id = p.id)
            GROUP BY p.id, p.first_name, p.last_name
            HAVING COUNT(*) > 0
            ORDER BY wins DESC
        """, fetch=True)
        
        # Board usage statistics  
        board_stats = execute_query("""
            SELECT b.roman_number, b.wood_type,
                   COUNT(g.id) as games_played
            FROM boards b
            LEFT JOIN games g ON g.board_id = b.id
            GROUP BY b.id, b.roman_number, b.wood_type
            ORDER BY games_played DESC
        """, fetch=True)
        
        return render_template("stats.html", player_stats=player_stats, board_stats=board_stats)
        
    except Exception as e:
        flash(f"Database error: {e}", "error")
        return render_template("stats.html", player_stats=[], board_stats=[])

if __name__ == "__main__":
    if IS_RAILWAY:
        print("🐘 Running on Railway with PostgreSQL")
        port = int(os.environ.get('PORT', 5000))
        app.run(host='0.0.0.0', port=port, debug=False)
    else:
        print("🗃️  Running locally with SQLite")
        app.run(host='127.0.0.1', port=5000, debug=True)
