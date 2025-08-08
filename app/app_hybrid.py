#!/usr/bin/env python3
"""
Hybrid Flask App for Cribbage Board Collection
Works with both PostgreSQL (Railway) and SQLite (local)
"""

import os
import sqlite3
import uuid
import time
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, url_for, flash

# Check if we're on Railway (has DATABASE_URL)
DATABASE_URL = os.environ.get('DATABASE_URL')
IS_RAILWAY = bool(DATABASE_URL)

# Cloudinary configuration
USE_CLOUDINARY = IS_RAILWAY and os.environ.get('CLOUDINARY_URL')

if USE_CLOUDINARY:
    import cloudinary
    import cloudinary.uploader
    import cloudinary.api
    print("✅ Cloudinary configured for image storage")
else:
    print("⚠️  Using local file storage (images will be lost on Railway redeploy)")

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'cribbage_board_collection_secret_key_2024')

# Configure file uploads (Railway uses temp storage, local uses data directory)
if IS_RAILWAY:
    # On Railway, use temp storage (files will be lost on redeploy)
    app.config["UPLOAD_FOLDER"] = "/tmp/uploads"
    try:
        os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
        print(f"✅ Upload directory created/verified: {app.config['UPLOAD_FOLDER']}")
        print(f"📁 Directory exists: {os.path.exists(app.config['UPLOAD_FOLDER'])}")
        print(f"📝 Directory writable: {os.access(app.config['UPLOAD_FOLDER'], os.W_OK)}")
    except Exception as e:
        print(f"❌ Error creating upload directory: {e}")
else:
    # Local development - use data directory
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, "data")
    uploads_dir = os.path.join(data_dir, "uploads")
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(uploads_dir, exist_ok=True)
    app.config["UPLOAD_FOLDER"] = uploads_dir
    print(f"✅ Local upload directory: {app.config['UPLOAD_FOLDER']}")

def init_database():
    """Initialize database tables on startup"""
    if IS_RAILWAY:
        # PostgreSQL table creation
        postgres_schema = """
        CREATE TABLE IF NOT EXISTS wood_types (
          id SERIAL PRIMARY KEY,
          name VARCHAR(255) UNIQUE NOT NULL
        );

        CREATE TABLE IF NOT EXISTS material_types (
          id SERIAL PRIMARY KEY,
          name VARCHAR(255) UNIQUE NOT NULL
        );

        CREATE TABLE IF NOT EXISTS boards (
          id SERIAL PRIMARY KEY,
          date VARCHAR(255),
          roman_number VARCHAR(255),
          description TEXT,
          wood_type VARCHAR(255),
          material_type VARCHAR(255),
          image_front VARCHAR(255),
          image_back VARCHAR(255),
          is_gift INTEGER DEFAULT 0,
          gifted_to VARCHAR(255),
          gifted_from VARCHAR(255),
          in_collection INTEGER DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS players (
          id SERIAL PRIMARY KEY,
          first_name VARCHAR(255),
          last_name VARCHAR(255),
          photo VARCHAR(255),
          date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS games (
          id SERIAL PRIMARY KEY,
          board_id INTEGER,
          winner_id INTEGER,
          loser_id INTEGER,
          winner_score INTEGER DEFAULT 121,
          loser_score INTEGER DEFAULT 0,
          is_skunk INTEGER DEFAULT 0,
          is_double_skunk INTEGER DEFAULT 0,
          date_played VARCHAR(255) DEFAULT CURRENT_DATE::TEXT,
          FOREIGN KEY (board_id) REFERENCES boards(id),
          FOREIGN KEY (winner_id) REFERENCES players(id),
          FOREIGN KEY (loser_id) REFERENCES players(id)
        );
        """
        
        try:
            # Execute each CREATE TABLE statement separately
            statements = [stmt.strip() for stmt in postgres_schema.split(';') if stmt.strip()]
            for statement in statements:
                if statement:
                    execute_query(statement)
            print("✅ PostgreSQL tables initialized successfully")
        except Exception as e:
            print(f"❌ Error initializing PostgreSQL tables: {e}")
    else:
        # SQLite table creation (local development)
        sqlite_schema = """
        CREATE TABLE IF NOT EXISTS wood_types (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          name TEXT UNIQUE NOT NULL
        );

        CREATE TABLE IF NOT EXISTS material_types (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          name TEXT UNIQUE NOT NULL
        );

        CREATE TABLE IF NOT EXISTS boards (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          date TEXT,
          roman_number TEXT,
          description TEXT,
          wood_type TEXT,
          material_type TEXT,
          image_front TEXT,
          image_back TEXT,
          is_gift INTEGER DEFAULT 0,
          gifted_to TEXT,
          gifted_from TEXT,
          in_collection INTEGER DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS players (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          first_name TEXT,
          last_name TEXT,
          photo TEXT,
          date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS games (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          board_id INTEGER,
          winner_id INTEGER,
          loser_id INTEGER,
          winner_score INTEGER DEFAULT 121,
          loser_score INTEGER DEFAULT 0,
          is_skunk INTEGER DEFAULT 0,
          is_double_skunk INTEGER DEFAULT 0,
          date_played TEXT DEFAULT (DATE('now')),
          FOREIGN KEY (board_id) REFERENCES boards(id),
          FOREIGN KEY (winner_id) REFERENCES players(id),
          FOREIGN KEY (loser_id) REFERENCES players(id)
        );
        """
        
        try:
            # Execute each CREATE TABLE statement separately
            statements = [stmt.strip() for stmt in sqlite_schema.split(';') if stmt.strip()]
            for statement in statements:
                if statement:
                    execute_query(statement)
            print("✅ SQLite tables initialized successfully")
        except Exception as e:
            print(f"❌ Error initializing SQLite tables: {e}")

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

def upload_image_to_cloudinary(file, folder="cribbage_boards"):
    """Upload image to Cloudinary cloud storage"""
    try:
        if not USE_CLOUDINARY:
            return None
            
        result = cloudinary.uploader.upload(
            file,
            folder=folder,
            resource_type="image",
            format="jpg",
            quality="auto",
            fetch_format="auto"
        )
        return result['secure_url']
    except Exception as e:
        print(f"❌ Cloudinary upload failed: {e}")
        return None

def upload_image(file, prefix=""):
    """Upload image - use Cloudinary on Railway, local storage otherwise"""
    if USE_CLOUDINARY:
        # Upload to Cloudinary
        url = upload_image_to_cloudinary(file)
        if url:
            print(f"✅ Image uploaded to Cloudinary: {url}")
            return url
        else:
            print("❌ Cloudinary upload failed, falling back to local storage")
    
    # Fallback to local storage
    try:
        filename = generate_unique_filename(file.filename, prefix)
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(file_path)
        print(f"✅ Image saved locally: {file_path}")
        return filename
    except Exception as e:
        print(f"❌ Local image save failed: {e}")
        return None

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
    """Serve uploaded files (images) - handle both Cloudinary URLs and local files"""
    try:
        # If filename is a full Cloudinary URL, redirect to it
        if filename.startswith('http'):
            from flask import redirect
            return redirect(filename)
        
        print(f"🖼️ Serving file request: {filename}")
        print(f"📁 Upload folder: {app.config['UPLOAD_FOLDER']}")
        print(f"📂 Directory exists: {os.path.exists(app.config['UPLOAD_FOLDER'])}")
        
        if os.path.exists(app.config['UPLOAD_FOLDER']):
            files_in_dir = os.listdir(app.config['UPLOAD_FOLDER'])
            print(f"📂 Files in upload directory: {files_in_dir}")
        
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        print(f"📄 Looking for file: {file_path}")
        print(f"📄 File exists: {os.path.exists(file_path)}")
        
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            print(f"📊 File size: {file_size} bytes")
        
        from flask import send_from_directory, send_file
        
        # Check if file exists
        if os.path.exists(file_path):
            return send_from_directory(app.config["UPLOAD_FOLDER"], filename)
        else:
            print(f"⚠️ File not found, returning placeholder")
            # Return a 1x1 transparent PNG as placeholder
            import io
            import base64
            
            # 1x1 transparent PNG in base64
            transparent_png = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==')
            return send_file(
                io.BytesIO(transparent_png),
                mimetype='image/png',
                as_attachment=False
            )
    except Exception as e:
        print(f"❌ Error serving file {filename}: {e}")
        print(f"🔍 Exception type: {type(e)}")
        import traceback
        print(f"📍 Full traceback: {traceback.format_exc()}")
        # Return a placeholder image or 404
        from flask import abort
        abort(404)

@app.route("/debug/filesystem")
def debug_filesystem():
    """Debug route to check filesystem status"""
    try:
        debug_info = {
            "upload_folder": app.config.get("UPLOAD_FOLDER"),
            "upload_folder_exists": os.path.exists(app.config.get("UPLOAD_FOLDER", "")),
            "current_working_directory": os.getcwd(),
            "is_railway": IS_RAILWAY,
        }
        
        if app.config.get("UPLOAD_FOLDER") and os.path.exists(app.config["UPLOAD_FOLDER"]):
            debug_info["upload_folder_writable"] = os.access(app.config["UPLOAD_FOLDER"], os.W_OK)
            debug_info["upload_folder_readable"] = os.access(app.config["UPLOAD_FOLDER"], os.R_OK)
            debug_info["files_in_upload_folder"] = os.listdir(app.config["UPLOAD_FOLDER"])
            debug_info["upload_folder_permissions"] = oct(os.stat(app.config["UPLOAD_FOLDER"]).st_mode)[-3:]
        
        # Test write capability
        test_file = os.path.join(app.config.get("UPLOAD_FOLDER", "/tmp"), "test_write.txt")
        try:
            with open(test_file, 'w') as f:
                f.write("test")
            debug_info["write_test"] = "SUCCESS"
            if os.path.exists(test_file):
                os.remove(test_file)
        except Exception as e:
            debug_info["write_test"] = f"FAILED: {e}"
        
        return f"<pre>{str(debug_info)}</pre>"
        
    except Exception as e:
        return f"Debug error: {e}"

@app.route("/static/<path:filename>")
def static_files(filename):
    """Serve static files"""
    try:
        from flask import send_from_directory
        import os
        static_dir = os.path.join(os.path.dirname(__file__), 'static')
        return send_from_directory(static_dir, filename)
    except Exception as e:
        print(f"Error serving static file {filename}: {e}")
        from flask import abort
        abort(404)

# Initialize database tables when the app starts
try:
    init_database()
except Exception as e:
    print(f"Warning: Database initialization failed: {e}")

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
            print("🆕 Adding new board...")
            print(f"📋 Form data received: {dict(request.form)}")
            
            # Get form data
            date = request.form.get("date", "")
            roman_number = request.form.get("roman_number", "")
            description = request.form.get("description", "")
            wood_type = request.form.get("wood_type", "")
            material_type = request.form.get("material_type", "")
            is_gift = int(request.form.get("is_gift", "0"))
            gifted_to = request.form.get("gifted_to", "")
            gifted_from = request.form.get("gifted_from", "")
            in_collection = int(request.form.get("in_collection", "1"))  # Default to 1 (in collection)
            
            print(f"📝 Processed form data: date={date}, roman_number={roman_number}, is_gift={is_gift}, in_collection={in_collection}")
            
            # Handle "Other" options with custom input (support both naming conventions)
            wood_type_other = request.form.get("wood_type_other", "") or request.form.get("custom_wood_type", "")
            if wood_type == "Other" and wood_type_other.strip():
                wood_type = wood_type_other.strip()
                
            material_type_other = request.form.get("material_type_other", "") or request.form.get("custom_material_type", "")
            if material_type == "Other" and material_type_other.strip():
                material_type = material_type_other.strip()
            
            # Handle file uploads
            front_image_file = request.files.get("front_view") or request.files.get("image_front")
            back_image_file = request.files.get("back_view") or request.files.get("image_back")
            
            front_filename = None
            back_filename = None
            
            if front_image_file and front_image_file.filename and front_image_file.filename.strip():
                print(f"🖼️ Processing front image: {front_image_file.filename}")
                front_filename = upload_image(front_image_file, "front")
                if front_filename:
                    print(f"✅ Front image uploaded successfully")
                else:
                    print(f"❌ Front image upload failed")
            
            if back_image_file and back_image_file.filename and back_image_file.filename.strip():
                print(f"�️ Processing back image: {back_image_file.filename}")
                back_filename = upload_image(back_image_file, "back")
                if back_filename:
                    print(f"✅ Back image uploaded successfully")
                else:
                    print(f"❌ Back image upload failed")
            
            # Insert into database
            print(f"💾 Inserting board into database...")
            print(f"📊 Values: [{date}, {roman_number}, {description}, {wood_type}, {material_type}, {front_filename}, {back_filename}, {is_gift}, {gifted_to}, {gifted_from}, {in_collection}]")
            
            result = execute_query("""
                INSERT INTO boards (date, roman_number, description, wood_type, material_type, 
                                  image_front, image_back, is_gift, gifted_to, gifted_from, in_collection)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, [date, roman_number, description, wood_type, material_type, 
                  front_filename, back_filename, is_gift, gifted_to, gifted_from, in_collection])
            
            print(f"✅ Board inserted successfully with ID: {result}")
            flash("Board added successfully!", "success")
            return redirect(url_for("index"))
            
        except Exception as e:
            print(f"❌ Error adding board: {e}")
            print(f"🔍 Exception type: {type(e)}")
            import traceback
            print(f"📍 Full traceback: {traceback.format_exc()}")
            flash(f"Error adding board: {e}", "error")
    
    return render_template("add_board.html")

@app.route("/board/<int:board_id>/edit", methods=["GET", "POST"])
def edit_board(board_id):
    if request.method == "GET":
        try:
            board = execute_query("SELECT * FROM boards WHERE id = ?", [board_id], fetch=True)
            if not board:
                flash("Board not found", "error")
                return redirect(url_for("index"))
            return render_template("edit_board.html", board=board[0])
        except Exception as e:
            flash(f"Error loading board: {e}", "error")
            return redirect(url_for("index"))
    
    else:  # POST - update board
        try:
            print(f"✏️ Editing board ID: {board_id}")
            print(f"📋 Form data received: {dict(request.form)}")
            
            # Get form data
            date = request.form.get("date", "")
            roman_number = request.form.get("roman_number", "")
            description = request.form.get("description", "")
            wood_type = request.form.get("wood_type", "")
            material_type = request.form.get("material_type", "")
            is_gift = int(request.form.get("is_gift", "0"))
            gifted_to = request.form.get("gifted_to", "")
            gifted_from = request.form.get("gifted_from", "")
            in_collection = int(request.form.get("in_collection", "1"))  # Default to 1 (in collection)
            
            # Handle "Other" options with custom input (support both naming conventions)
            wood_type_other = request.form.get("wood_type_other", "") or request.form.get("custom_wood_type", "")
            if wood_type == "Other" and wood_type_other.strip():
                wood_type = wood_type_other.strip()
                
            material_type_other = request.form.get("material_type_other", "") or request.form.get("custom_material_type", "")
            if material_type == "Other" and material_type_other.strip():
                material_type = material_type_other.strip()
            
            # Handle file uploads
            front_image = request.files.get("front_view") or request.files.get("image_front") 
            back_image = request.files.get("back_view") or request.files.get("image_back")
            
            # Get current filenames
            current_board = execute_query("SELECT image_front, image_back FROM boards WHERE id = ?", [board_id], fetch=True)
            front_filename = current_board[0]['image_front'] if current_board else None
            back_filename = current_board[0]['image_back'] if current_board else None
            
            # Update filenames if new files uploaded
            if front_image and front_image.filename and front_image.filename.strip():
                print(f"🖼️ Processing front image for edit: {front_image.filename}")
                new_front_filename = upload_image(front_image, "front")
                if new_front_filename:
                    front_filename = new_front_filename
                    print(f"✅ Front image updated successfully")
                else:
                    print(f"❌ Front image update failed")
            
            if back_image and back_image.filename and back_image.filename.strip():
                print(f"🖼️ Processing back image for edit: {back_image.filename}")
                new_back_filename = upload_image(back_image, "back")
                if new_back_filename:
                    back_filename = new_back_filename
                    print(f"✅ Back image updated successfully")
                else:
                    print(f"❌ Back image update failed")
            
            # Update database
            execute_query("""
                UPDATE boards SET date = ?, roman_number = ?, description = ?, wood_type = ?, 
                                material_type = ?, image_front = ?, image_back = ?, is_gift = ?, 
                                gifted_to = ?, gifted_from = ?, in_collection = ?
                WHERE id = ?
            """, [date, roman_number, description, wood_type, material_type, 
                  front_filename, back_filename, is_gift, gifted_to, gifted_from, in_collection, board_id])
            
            flash("Board updated successfully!", "success")
            return redirect(url_for("board_detail", board_id=board_id))
            
        except Exception as e:
            flash(f"Error updating board: {e}", "error")
            return redirect(url_for("edit_board", board_id=board_id))

@app.route("/board/<int:board_id>/delete", methods=["POST"])
def delete_board(board_id):
    try:
        print(f"🗑️ Deleting board ID: {board_id}")
        
        # Get board info for cleanup
        board = execute_query("SELECT image_front, image_back FROM boards WHERE id = ?", [board_id], fetch=True)
        
        if board:
            print(f"✅ Board found, proceeding with deletion")
            # Delete the board from database
            execute_query("DELETE FROM boards WHERE id = ?", [board_id])
            print(f"✅ Board deleted successfully from database")
            flash("Board deleted successfully!", "success")
        else:
            print(f"❌ Board not found in database")
            flash("Board not found", "error")
            
    except Exception as e:
        print(f"❌ Error deleting board: {e}")
        print(f"🔍 Exception type: {type(e)}")
        import traceback
        print(f"📍 Full traceback: {traceback.format_exc()}")
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
            try:
                print(f"👤 Processing player photo: {photo.filename}")
                print(f"📁 Upload folder: {app.config['UPLOAD_FOLDER']}")
                print(f"📊 Photo content type: {photo.content_type}")
                
                # Ensure upload directory exists
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                
                photo_filename = generate_unique_filename(photo.filename, "player")
                upload_path = os.path.join(app.config["UPLOAD_FOLDER"], photo_filename)
                
                print(f"💾 Saving player photo to: {upload_path}")
                photo.save(upload_path)
                
                print(f"📄 Player photo exists after save: {os.path.exists(upload_path)}")
                if os.path.exists(upload_path):
                    file_size = os.path.getsize(upload_path)
                    print(f"📊 Player photo size: {file_size} bytes")
                    print(f"✅ Player photo saved successfully")
                else:
                    print(f"❌ Player photo does not exist after save")
                    photo_filename = None
                    
            except Exception as e:
                print(f"❌ Error saving player photo: {e}")
                import traceback
                print(f"📍 Full traceback: {traceback.format_exc()}")
                photo_filename = None
        
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
        
        # Get all games involving this player
        games = execute_query("""
            SELECT g.*, 
                   pw.first_name || ' ' || pw.last_name as winner_name,
                   pl.first_name || ' ' || pl.last_name as loser_name,
                   b.roman_number
            FROM games g
            LEFT JOIN players pw ON g.winner_id = pw.id
            LEFT JOIN players pl ON g.loser_id = pl.id
            LEFT JOIN boards b ON g.board_id = b.id
            WHERE g.winner_id = ? OR g.loser_id = ?
            ORDER BY g.date_played DESC
        """, [player_id, player_id], fetch=True)
        
        # Calculate comprehensive stats
        wins = len([g for g in games if g['winner_id'] == player_id])
        losses = len([g for g in games if g['loser_id'] == player_id])
        total_games = wins + losses
        win_percentage = (wins / total_games * 100) if total_games > 0 else 0
        
        skunks_given = len([g for g in games if g['winner_id'] == player_id and (g['is_skunk'] or g['is_double_skunk'])])
        skunks_received = len([g for g in games if g['loser_id'] == player_id and (g['is_skunk'] or g['is_double_skunk'])])
        double_skunks_given = len([g for g in games if g['winner_id'] == player_id and g['is_double_skunk']])
        double_skunks_received = len([g for g in games if g['loser_id'] == player_id and g['is_double_skunk']])
        
        stats = {
            'wins': wins,
            'losses': losses,
            'total_games': total_games,
            'win_percentage': win_percentage,
            'skunks_given': skunks_given,
            'skunks_received': skunks_received,
            'double_skunks_given': double_skunks_given,
            'double_skunks_received': double_skunks_received,
            'avg_winning_score': 121.0,
            'current_streak': 'N/A',
            'recent_form': 'N/A',
            'favorite_opponent': None,  # Changed from 'N/A' to None
            'nemesis': None  # Changed from 'N/A' to None
        }
        
        return render_template("player_detail.html", player=player[0], stats=stats, recent_games=games)
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
                try:
                    print(f"👤 Updating player photo: {photo.filename}")
                    # Delete old photo if it exists
                    if current_photo:
                        print(f"🗑️ Deleting old photo: {current_photo}")
                        safe_delete_file(current_photo)
                    
                    # Ensure upload directory exists
                    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                    
                    # Save new photo
                    photo_filename = generate_unique_filename(photo.filename, "player")
                    upload_path = os.path.join(app.config["UPLOAD_FOLDER"], photo_filename)
                    
                    print(f"💾 Saving updated player photo to: {upload_path}")
                    photo.save(upload_path)
                    
                    print(f"📄 Updated photo exists after save: {os.path.exists(upload_path)}")
                    if os.path.exists(upload_path):
                        file_size = os.path.getsize(upload_path)
                        print(f"📊 Updated photo size: {file_size} bytes")
                        print(f"✅ Player photo updated successfully")
                    else:
                        print(f"❌ Updated photo does not exist after save")
                        photo_filename = current_photo  # Revert to old photo
                        
                except Exception as e:
                    print(f"❌ Error updating player photo: {e}")
                    import traceback
                    print(f"📍 Full traceback: {traceback.format_exc()}")
                    photo_filename = current_photo  # Revert to old photo
            
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

@app.route("/game/<int:game_id>/edit")
def edit_game(game_id):
    try:
        game = execute_query("SELECT * FROM games WHERE id = ?", [game_id], fetch=True)
        if not game:
            flash("Game not found!", "error")
            return redirect(url_for("games"))
        
        game = game[0]
        players = execute_query("SELECT * FROM players ORDER BY first_name, last_name", fetch=True)
        boards = execute_query("SELECT * FROM boards ORDER BY roman_number", fetch=True)
        
        return render_template("edit_game.html", game=game, players=players, boards=boards)
        
    except Exception as e:
        flash(f"Error loading game: {e}", "error")
        return redirect(url_for("games"))

@app.route("/game/<int:game_id>/edit", methods=["POST"])
def update_game(game_id):
    try:
        board_id = request.form["board_id"]
        winner_id = request.form["winner_id"]
        loser_id = request.form["loser_id"]
        date_played = request.form["date_played"]
        winner_score = request.form.get("winner_score", 121)
        loser_score = request.form.get("loser_score", 0)
        notes = request.form.get("notes", "")
        is_skunk = 'is_skunk' in request.form
        is_double_skunk = 'is_double_skunk' in request.form
        
        if winner_id == loser_id:
            flash("Winner and loser cannot be the same player!", "error")
            return redirect(url_for("edit_game", game_id=game_id))
        
        execute_query("""
            UPDATE games 
            SET board_id = ?, winner_id = ?, loser_id = ?, date_played = ?, 
                winner_score = ?, loser_score = ?, is_skunk = ?, is_double_skunk = ?
            WHERE id = ?
        """, [board_id, winner_id, loser_id, date_played, winner_score, loser_score, is_skunk, is_double_skunk, game_id])
        
        flash("Game updated successfully!", "success")
        
    except Exception as e:
        flash(f"Error updating game: {e}", "error")
    
    return redirect(url_for("games"))

@app.route("/game/<int:game_id>/delete", methods=["POST"])
def delete_game(game_id):
    try:
        execute_query("DELETE FROM games WHERE id = ?", [game_id])
        flash("Game deleted successfully!", "success")
        
    except Exception as e:
        flash(f"Error deleting game: {e}", "error")
    
    return redirect(url_for("games"))

@app.route("/stats")
def stats():
    try:
        # Get basic data for the template
        players = execute_query("SELECT * FROM players ORDER BY first_name, last_name", fetch=True)
        boards = execute_query("SELECT * FROM boards ORDER BY roman_number", fetch=True)
        
        # Get games with player names for display
        games_query = """
            SELECT g.*, 
                   w.first_name || ' ' || w.last_name as winner,
                   l.first_name || ' ' || l.last_name as loser,
                   b.roman_number
            FROM games g
            JOIN players w ON g.winner_id = w.id
            JOIN players l ON g.loser_id = l.id
            LEFT JOIN boards b ON g.board_id = b.id
            ORDER BY g.date_played DESC, g.id DESC
        """
        games = execute_query(games_query, fetch=True)
        
        # Simple leaderboard - basic win/loss stats
        leaderboard = []
        for player in players:
            wins = len([g for g in games if g['winner_id'] == player['id']])
            losses = len([g for g in games if g['loser_id'] == player['id']])
            total_games = wins + losses
            
            if total_games > 0:
                win_percentage = (wins / total_games) * 100
                player_stats = {
                    'id': player['id'],
                    'first_name': player['first_name'],
                    'last_name': player['last_name'],
                    'photo': player['photo'] if 'photo' in player.keys() else None,
                    'wins': wins,
                    'losses': losses,
                    'total_games': total_games,
                    'win_percentage': win_percentage,
                    'skunks_given': len([g for g in games if g['winner_id'] == player['id'] and (g['is_skunk'] or g['is_double_skunk'])]),
                    'skunks_received': len([g for g in games if g['loser_id'] == player['id'] and (g['is_skunk'] or g['is_double_skunk'])]),
                    'double_skunks_given': len([g for g in games if g['winner_id'] == player['id'] and g['is_double_skunk']]),
                    'double_skunks_received': len([g for g in games if g['loser_id'] == player['id'] and g['is_double_skunk']]),
                }
                leaderboard.append(player_stats)
        
        # Sort by win percentage
        leaderboard.sort(key=lambda x: x['win_percentage'], reverse=True)
        
        return render_template("stats.html", 
                             players=players, 
                             boards=boards, 
                             games=games,
                             leaderboard=leaderboard)
        
    except Exception as e:
        flash(f"Database error: {e}", "error")
        return render_template("stats.html", 
                             players=[], 
                             boards=[], 
                             games=[],
                             leaderboard=[])

if __name__ == "__main__":
    # Initialize database tables on startup
    init_database()
    
    if IS_RAILWAY:
        print("🐘 Running on Railway with PostgreSQL")
        port = int(os.environ.get('PORT', 5000))
        app.run(host='0.0.0.0', port=port, debug=False)
    else:
        print("🗃️  Running locally with SQLite")
        app.run(host='127.0.0.1', port=5000, debug=True)
