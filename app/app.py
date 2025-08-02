import os
import sqlite3
import uuid
import time
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'cribbage_board_collection_secret_key_2024'

# Get the base directory (one level up from app directory)
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_dir = os.path.join(base_dir, "data")
uploads_dir = os.path.join(data_dir, "uploads")

# Ensure data directories exist
os.makedirs(data_dir, exist_ok=True)
os.makedirs(uploads_dir, exist_ok=True)

# Configure upload folder to use data directory
app.config["UPLOAD_FOLDER"] = uploads_dir

# Also maintain the old static/uploads for backward compatibility
app_dir = os.path.dirname(os.path.abspath(__file__))
old_uploads_dir = os.path.join(app_dir, "static", "uploads")
os.makedirs(old_uploads_dir, exist_ok=True)

def get_db():
    # Use database in data directory (safe from code updates)
    db_path = os.path.join(data_dir, "database.db")
    
    # If database doesn't exist in data directory, check old location
    if not os.path.exists(db_path):
        old_db_path = os.path.join(app_dir, "database.db")
        if os.path.exists(old_db_path):
            print(f"⚠️  Database found in old location, consider running migrate_data.py")
            db_path = old_db_path
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def generate_unique_filename(original_filename, prefix=""):
    """Generate a unique filename to prevent overwrites"""
    if not original_filename:
        return f"{prefix}_{int(time.time())}_{uuid.uuid4().hex[:8]}.jpg"
    
    # Get file extension
    filename = secure_filename(original_filename)
    name, ext = os.path.splitext(filename)
    if not ext:
        ext = '.jpg'
    
    # Generate unique filename with timestamp and UUID
    timestamp = int(time.time())
    unique_id = uuid.uuid4().hex[:8]
    return f"{prefix}_{timestamp}_{unique_id}_{name}{ext}"

def safe_delete_file(filename):
    """Safely delete a file if it exists - checks both data and app directories"""
    if filename:
        try:
            # Try data directory first (new location)
            file_path = os.path.join(uploads_dir, filename)
            if os.path.exists(file_path):
                os.remove(file_path)
                return
            
            # Try old location for backward compatibility
            old_file_path = os.path.join(old_uploads_dir, filename)
            if os.path.exists(old_file_path):
                os.remove(old_file_path)
                return
                
        except Exception as e:
            print(f"Warning: Could not delete file {filename}: {e}")

@app.route("/")
def index():
    db = get_db()
    
    # Build query with filters
    query = "SELECT * FROM boards WHERE 1=1"
    params = []
    
    # Filter by collection status
    filter_collection = request.args.get("filter_collection")
    if filter_collection:
        query += " AND in_collection = ?"
        params.append(int(filter_collection))
    
    # Filter by gifted status
    filter_gifted = request.args.get("filter_gifted")
    if filter_gifted:
        query += " AND is_gift = ?"
        params.append(int(filter_gifted))
    
    # Filter by gifted to
    filter_gifted_to = request.args.get("filter_gifted_to")
    if filter_gifted_to:
        query += " AND gifted_to LIKE ?"
        params.append(f"%{filter_gifted_to}%")
    
    boards = db.execute(query, params).fetchall()
    wood_types = db.execute("SELECT * FROM wood_types").fetchall()
    material_types = db.execute("SELECT * FROM material_types").fetchall()
    return render_template("index.html", boards=boards, wood_types=wood_types, material_types=material_types)

@app.route("/add_board", methods=["POST"])
def add_board():
    db = get_db()
    date = request.form.get("date")
    roman = request.form.get("roman")
    desc = request.form.get("desc")
    wood = request.form.get("wood")
    material = request.form.get("material")
    new_wood = request.form.get("new_wood")
    new_mat = request.form.get("new_material")
    is_gift = int("is_gift" in request.form)
    gifted_to = request.form.get("gifted_to") if is_gift else None
    gifted_from = request.form.get("gifted_from") if is_gift else None

    # Check for duplicate roman numeral (if provided)
    if roman and roman.strip():
        existing_board = db.execute(
            "SELECT id FROM boards WHERE UPPER(roman_number) = UPPER(?)", 
            (roman.strip(),)
        ).fetchone()
        
        if existing_board:
            flash(f"Board with Roman numeral '{roman}' already exists!", "error")
            return redirect(url_for("index"))

    if new_wood:
        db.execute("INSERT OR IGNORE INTO wood_types (name) VALUES (?)", (new_wood,))
        wood = db.execute("SELECT name FROM wood_types WHERE name = ?", (new_wood,)).fetchone()["name"]
    if new_mat:
        db.execute("INSERT OR IGNORE INTO material_types (name) VALUES (?)", (new_mat,))
        material = db.execute("SELECT name FROM material_types WHERE name = ?", (new_mat,)).fetchone()["name"]

    front_img = request.files["front"]
    back_img = request.files["back"]
    
    # Validate that both images are provided
    if not front_img or not front_img.filename:
        flash("Front image is required!", "error")
        return redirect(url_for("index"))
    
    if not back_img or not back_img.filename:
        flash("Back image is required!", "error")
        return redirect(url_for("index"))
    
    # Generate unique filenames to prevent overwrites
    front_filename = generate_unique_filename(front_img.filename, "front")
    back_filename = generate_unique_filename(back_img.filename, "back")
    
    # Save images
    front_img.save(os.path.join(app.config["UPLOAD_FOLDER"], front_filename))
    back_img.save(os.path.join(app.config["UPLOAD_FOLDER"], back_filename))

    in_collection = int("in_collection" in request.form)
    db.execute("""
        INSERT INTO boards (date, roman_number, description, wood_type, material_type,
                            image_front, image_back, is_gift, gifted_to, gifted_from, in_collection)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (date, roman, desc, wood, material, front_filename, back_filename, is_gift, gifted_to, gifted_from, in_collection))
    db.commit()
    flash("Board added successfully!", "success")
    return redirect(url_for("index"))

@app.route("/delete_board/<int:board_id>", methods=["POST"])
def delete_board(board_id):
    db = get_db()
    
    # Get the board info before deleting to clean up images
    board = db.execute("SELECT image_front, image_back FROM boards WHERE id = ?", (board_id,)).fetchone()
    
    if board:
        # Clean up image files
        safe_delete_file(board["image_front"])
        safe_delete_file(board["image_back"])
    
    # Delete the board record
    db.execute("DELETE FROM boards WHERE id = ?", (board_id,))
    db.commit()
    flash("Board deleted successfully!", "success")
    return redirect(url_for("index"))

@app.route("/edit_board/<int:board_id>", methods=["GET", "POST"])
def edit_board(board_id):
    db = get_db()
    board = db.execute("SELECT * FROM boards WHERE id = ?", (board_id,)).fetchone()
    
    if request.method == "POST":
        date = request.form.get("date")
        roman = request.form.get("roman")
        desc = request.form.get("desc")
        wood = request.form.get("wood")
        material = request.form.get("material")
        is_gift = int("is_gift" in request.form)
        gifted_to = request.form.get("gifted_to") if is_gift else None
        gifted_from = request.form.get("gifted_from") if is_gift else None
        in_collection = int("in_collection" in request.form)
        
        # Handle image updates if new files are uploaded
        front_img = request.files.get("front")
        back_img = request.files.get("back")
        front_filename = board["image_front"]
        back_filename = board["image_back"]
        
        if front_img and front_img.filename:
            # Delete old front image
            safe_delete_file(front_filename)
            # Save new front image
            front_filename = generate_unique_filename(front_img.filename, "front")
            front_img.save(os.path.join(app.config["UPLOAD_FOLDER"], front_filename))
            
        if back_img and back_img.filename:
            # Delete old back image
            safe_delete_file(back_filename)
            # Save new back image
            back_filename = generate_unique_filename(back_img.filename, "back")
            back_img.save(os.path.join(app.config["UPLOAD_FOLDER"], back_filename))
        
        db.execute("""
            UPDATE boards SET date=?, roman_number=?, description=?, wood_type=?, material_type=?,
                             image_front=?, image_back=?, is_gift=?, gifted_to=?, gifted_from=?, in_collection=?
            WHERE id=?
        """, (date, roman, desc, wood, material, front_filename, back_filename, is_gift, gifted_to, gifted_from, in_collection, board_id))
        db.commit()
        return redirect(url_for("index"))
    
    return render_template("edit_board.html", board=board)

@app.route("/boards/<int:board_id>")
def board_detail(board_id):
    db = get_db()
    board = db.execute("SELECT * FROM boards WHERE id = ?", (board_id,)).fetchone()
    games = db.execute("""
        SELECT g.*, 
               p1.first_name || ' ' || p1.last_name AS winner_name,
               p2.first_name || ' ' || p2.last_name AS loser_name
        FROM games g
        JOIN players p1 ON g.winner_id = p1.id
        JOIN players p2 ON g.loser_id = p2.id
        WHERE g.board_id = ?
        ORDER BY date_played DESC
    """, (board_id,)).fetchall()
    return render_template("board_detail.html", board=board, games=games)

@app.route("/players")
def players():
    db = get_db()
    players = db.execute("SELECT * FROM players").fetchall()
    return render_template("players.html", players=players)

@app.route("/add_player", methods=["POST"])
def add_player():
    db = get_db()
    first = request.form.get("first")
    last = request.form.get("last")
    
    # Check for duplicate player names
    existing_player = db.execute(
        "SELECT id FROM players WHERE LOWER(first_name) = LOWER(?) AND LOWER(last_name) = LOWER(?)", 
        (first, last)
    ).fetchone()
    
    if existing_player:
        flash(f"Player '{first} {last}' already exists!", "error")
        return redirect(url_for("players"))
    
    db.execute("INSERT INTO players (first_name, last_name) VALUES (?, ?)", (first, last))
    db.commit()
    flash(f"Player '{first} {last}' added successfully!", "success")
    return redirect(url_for("players"))

@app.route("/delete_player/<int:player_id>", methods=["POST"])
def delete_player(player_id):
    db = get_db()
    
    # Check if player has any games recorded
    games_count = db.execute("SELECT COUNT(*) FROM games WHERE winner_id = ? OR loser_id = ?", 
                             (player_id, player_id)).fetchone()[0]
    
    if games_count > 0:
        flash(f"Cannot delete player - they have {games_count} game(s) recorded. Delete games first.", "error")
        return redirect(url_for("players"))
    
    # Safe to delete player
    db.execute("DELETE FROM players WHERE id = ?", (player_id,))
    db.commit()
    flash("Player deleted successfully!", "success")
    return redirect(url_for("players"))

@app.route("/delete_game/<int:game_id>", methods=["POST"])
def delete_game(game_id):
    db = get_db()
    
    # Get the board_id for redirect
    game = db.execute("SELECT board_id FROM games WHERE id = ?", (game_id,)).fetchone()
    if not game:
        flash("Game not found!", "error")
        return redirect(url_for("index"))
    
    board_id = game[0]
    
    # Delete the game
    db.execute("DELETE FROM games WHERE id = ?", (game_id,))
    db.commit()
    flash("Game deleted successfully!", "success")
    return redirect(url_for("board_detail", board_id=board_id))

@app.route("/games")
def games():
    db = get_db()
    games = db.execute("""
        SELECT g.*, 
               b.roman_number, 
               p1.first_name || ' ' || p1.last_name AS winner,
               p2.first_name || ' ' || p2.last_name AS loser
        FROM games g
        JOIN boards b ON g.board_id = b.id
        JOIN players p1 ON g.winner_id = p1.id
        JOIN players p2 ON g.loser_id = p2.id
        ORDER BY date_played DESC
    """).fetchall()
    boards = db.execute("SELECT * FROM boards").fetchall()
    players = db.execute("SELECT * FROM players").fetchall()
    return render_template("games.html", games=games, boards=boards, players=players)

@app.route("/add_game", methods=["POST"])
def add_game():
    db = get_db()
    board_id = request.form.get("board_id")
    winner_id = request.form.get("winner_id")
    loser_id = request.form.get("loser_id")
    date_played = request.form.get("date_played")
    
    # Validate that winner and loser are different
    if winner_id == loser_id:
        flash("Winner and loser cannot be the same player!", "error")
        return redirect(url_for("games"))
    
    # Check for duplicate game (same board, players, and date)
    existing_game = db.execute("""
        SELECT id FROM games 
        WHERE board_id = ? AND winner_id = ? AND loser_id = ? AND date_played = ?
    """, (board_id, winner_id, loser_id, date_played)).fetchone()
    
    if existing_game:
        flash("This exact game (same board, players, and date) has already been recorded!", "error")
        return redirect(url_for("games"))
    
    # Get skunk status from checkboxes
    is_skunk = int("is_skunk" in request.form)
    is_double_skunk = int("is_double_skunk" in request.form)
    
    # Set default scores (can be null or default values since we're not tracking them)
    winner_score = 121
    loser_score = 0
    
    db.execute("""
        INSERT INTO games (board_id, winner_id, loser_id, winner_score, loser_score, 
                          is_skunk, is_double_skunk, date_played) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (board_id, winner_id, loser_id, winner_score, loser_score, is_skunk, is_double_skunk, date_played))
    db.commit()
    flash("Game recorded successfully!", "success")
    return redirect(url_for("games"))

@app.route("/stats")
def stats():
    db = get_db()
    
    # Get basic player stats
    players = db.execute("""
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
    """).fetchall()
    
    # For each player, get their nemesis and favorite victim
    enhanced_stats = []
    for player in players:
        # Get nemesis
        nemesis = db.execute("""
            SELECT 
                CASE WHEN g.winner_id = ? THEN p2.first_name || ' ' || p2.last_name 
                     ELSE p1.first_name || ' ' || p1.last_name END AS opponent_name,
                SUM(CASE WHEN g.loser_id = ? THEN 1 ELSE 0 END) AS losses_to_them
            FROM games g
            JOIN players p1 ON g.winner_id = p1.id
            JOIN players p2 ON g.loser_id = p2.id
            WHERE g.winner_id = ? OR g.loser_id = ?
            GROUP BY opponent_name
            HAVING COUNT(*) >= 2
            ORDER BY losses_to_them DESC
            LIMIT 1
        """, (player['id'], player['id'], player['id'], player['id'])).fetchone()
        
        # Get favorite victim
        favorite_victim = db.execute("""
            SELECT 
                CASE WHEN g.winner_id = ? THEN p2.first_name || ' ' || p2.last_name 
                     ELSE p1.first_name || ' ' || p1.last_name END AS opponent_name,
                SUM(CASE WHEN g.winner_id = ? THEN 1 ELSE 0 END) AS wins_against_them
            FROM games g
            JOIN players p1 ON g.winner_id = p1.id
            JOIN players p2 ON g.loser_id = p2.id
            WHERE g.winner_id = ? OR g.loser_id = ?
            GROUP BY opponent_name
            HAVING COUNT(*) >= 2
            ORDER BY wins_against_them DESC
            LIMIT 1
        """, (player['id'], player['id'], player['id'], player['id'])).fetchone()
        
        enhanced_stats.append({
            'player': player,
            'nemesis': nemesis,
            'favorite_victim': favorite_victim
        })
    
    return render_template("stats.html", stats=enhanced_stats)

@app.route("/player/<int:player_id>")
def player_detail(player_id):
    db = get_db()
    
    # Get player info
    player = db.execute("SELECT * FROM players WHERE id = ?", (player_id,)).fetchone()
    
    # Get player overall stats
    player_stats = db.execute("""
        SELECT 
            SUM(CASE WHEN p.id = g.winner_id THEN 1 ELSE 0 END) AS wins,
            SUM(CASE WHEN p.id = g.loser_id AND g.is_double_skunk = 1 THEN 3
                     WHEN p.id = g.loser_id AND g.is_skunk = 1 THEN 2
                     WHEN p.id = g.loser_id THEN 1 ELSE 0 END) AS total_losses,
            SUM(CASE WHEN p.id = g.winner_id AND g.is_skunk = 1 THEN 1 ELSE 0 END) AS skunks_given,
            SUM(CASE WHEN p.id = g.winner_id AND g.is_double_skunk = 1 THEN 1 ELSE 0 END) AS double_skunks_given,
            SUM(CASE WHEN p.id = g.loser_id AND g.is_skunk = 1 THEN 1 ELSE 0 END) AS skunks_received,
            SUM(CASE WHEN p.id = g.loser_id AND g.is_double_skunk = 1 THEN 1 ELSE 0 END) AS double_skunks_received,
            COUNT(CASE WHEN p.id = g.winner_id OR p.id = g.loser_id THEN 1 END) AS total_games
        FROM players p
        LEFT JOIN games g ON p.id = g.winner_id OR p.id = g.loser_id
        WHERE p.id = ?
        GROUP BY p.id
    """, (player_id,)).fetchone()
    
    # Get head-to-head records
    head_to_head = db.execute("""
        SELECT 
            CASE WHEN g.winner_id = ? THEN g.loser_id ELSE g.winner_id END AS opponent_id,
            CASE WHEN g.winner_id = ? THEN p2.first_name || ' ' || p2.last_name 
                 ELSE p1.first_name || ' ' || p1.last_name END AS opponent_name,
            SUM(CASE WHEN g.winner_id = ? THEN 1 ELSE 0 END) AS wins,
            SUM(CASE WHEN g.loser_id = ? THEN 1 ELSE 0 END) AS losses,
            COUNT(*) AS total_games,
            SUM(CASE WHEN g.winner_id = ? AND g.is_skunk = 1 THEN 1 ELSE 0 END) AS skunks_given,
            SUM(CASE WHEN g.loser_id = ? AND g.is_skunk = 1 THEN 1 ELSE 0 END) AS skunks_received
        FROM games g
        JOIN players p1 ON g.winner_id = p1.id
        JOIN players p2 ON g.loser_id = p2.id
        WHERE g.winner_id = ? OR g.loser_id = ?
        GROUP BY opponent_id, opponent_name
        ORDER BY total_games DESC
    """, (player_id, player_id, player_id, player_id, player_id, player_id, player_id, player_id)).fetchall()
    
    # Find nemesis (opponent with most losses against)
    nemesis = db.execute("""
        SELECT 
            CASE WHEN g.winner_id = ? THEN g.loser_id ELSE g.winner_id END AS opponent_id,
            CASE WHEN g.winner_id = ? THEN p2.first_name || ' ' || p2.last_name 
                 ELSE p1.first_name || ' ' || p1.last_name END AS opponent_name,
            SUM(CASE WHEN g.winner_id = ? THEN 1 ELSE 0 END) AS wins,
            SUM(CASE WHEN g.loser_id = ? THEN 1 ELSE 0 END) AS losses,
            COUNT(*) AS total_games
        FROM games g
        JOIN players p1 ON g.winner_id = p1.id
        JOIN players p2 ON g.loser_id = p2.id
        WHERE g.winner_id = ? OR g.loser_id = ?
        GROUP BY opponent_id, opponent_name
        HAVING COUNT(*) >= 3
        ORDER BY losses DESC, (CAST(wins AS FLOAT) / COUNT(*)) ASC
        LIMIT 1
    """, (player_id, player_id, player_id, player_id, player_id, player_id)).fetchone()
    
    # Find favorite opponent (opponent with most wins against)
    favorite_opponent = db.execute("""
        SELECT 
            CASE WHEN g.winner_id = ? THEN g.loser_id ELSE g.winner_id END AS opponent_id,
            CASE WHEN g.winner_id = ? THEN p2.first_name || ' ' || p2.last_name 
                 ELSE p1.first_name || ' ' || p1.last_name END AS opponent_name,
            SUM(CASE WHEN g.winner_id = ? THEN 1 ELSE 0 END) AS wins,
            SUM(CASE WHEN g.loser_id = ? THEN 1 ELSE 0 END) AS losses,
            COUNT(*) AS total_games
        FROM games g
        JOIN players p1 ON g.winner_id = p1.id
        JOIN players p2 ON g.loser_id = p2.id
        WHERE g.winner_id = ? OR g.loser_id = ?
        GROUP BY opponent_id, opponent_name
        HAVING COUNT(*) >= 3
        ORDER BY wins DESC, (CAST(wins AS FLOAT) / COUNT(*)) DESC
        LIMIT 1
    """, (player_id, player_id, player_id, player_id, player_id, player_id)).fetchone()
    
    # Get recent games
    recent_games = db.execute("""
        SELECT g.*, b.roman_number,
               CASE WHEN g.winner_id = ? THEN p2.first_name || ' ' || p2.last_name 
                    ELSE p1.first_name || ' ' || p1.last_name END AS opponent_name
        FROM games g
        JOIN boards b ON g.board_id = b.id
        JOIN players p1 ON g.winner_id = p1.id
        JOIN players p2 ON g.loser_id = p2.id
        WHERE g.winner_id = ? OR g.loser_id = ?
        ORDER BY date_played DESC
        LIMIT 10
    """, (player_id, player_id, player_id)).fetchall()
    
    return render_template("player_detail.html", 
                         player=player, 
                         player_stats=player_stats,
                         head_to_head=head_to_head,
                         nemesis=nemesis,
                         favorite_opponent=favorite_opponent,
                         recent_games=recent_games)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
