-- PostgreSQL Schema for Cribbage Board Collection
-- This schema is compatible with Railway's PostgreSQL database

DROP TABLE IF EXISTS games CASCADE;
DROP TABLE IF EXISTS players CASCADE;
DROP TABLE IF EXISTS boards CASCADE;
DROP TABLE IF EXISTS wood_types CASCADE;
DROP TABLE IF EXISTS material_types CASCADE;

CREATE TABLE wood_types (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) UNIQUE NOT NULL
);

CREATE TABLE material_types (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) UNIQUE NOT NULL
);

CREATE TABLE boards (
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

CREATE TABLE players (
  id SERIAL PRIMARY KEY,
  first_name VARCHAR(255),
  last_name VARCHAR(255),
  photo VARCHAR(255),
  date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE games (
  id SERIAL PRIMARY KEY,
  board_id INTEGER,
  winner_id INTEGER,
  loser_id INTEGER,
  winner_score INTEGER DEFAULT 121,
  loser_score INTEGER DEFAULT 0,
  is_skunk INTEGER DEFAULT 0,
  is_double_skunk INTEGER DEFAULT 0,
  date_played VARCHAR(255) DEFAULT CURRENT_DATE::TEXT,
  FOREIGN KEY (board_id) REFERENCES boards(id) ON DELETE SET NULL,
  FOREIGN KEY (winner_id) REFERENCES players(id) ON DELETE CASCADE,
  FOREIGN KEY (loser_id) REFERENCES players(id) ON DELETE CASCADE
);

-- Create indexes for better performance
CREATE INDEX idx_boards_roman_number ON boards(roman_number);
CREATE INDEX idx_boards_material_type ON boards(material_type);
CREATE INDEX idx_boards_wood_type ON boards(wood_type);
CREATE INDEX idx_boards_in_collection ON boards(in_collection);
CREATE INDEX idx_games_board_id ON games(board_id);
CREATE INDEX idx_games_winner_id ON games(winner_id);
CREATE INDEX idx_games_loser_id ON games(loser_id);
CREATE INDEX idx_games_date_played ON games(date_played);
