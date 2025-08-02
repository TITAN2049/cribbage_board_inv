
DROP TABLE IF EXISTS boards;
DROP TABLE IF EXISTS players;
DROP TABLE IF EXISTS games;
DROP TABLE IF EXISTS wood_types;
DROP TABLE IF EXISTS material_types;

CREATE TABLE wood_types (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT UNIQUE NOT NULL
);

CREATE TABLE material_types (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT UNIQUE NOT NULL
);

CREATE TABLE boards (
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

CREATE TABLE players (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  first_name TEXT,
  last_name TEXT
);

CREATE TABLE games (
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
