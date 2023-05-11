-- Drop tables if they already exist in the database.
DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS issue;
DROP TABLE IF EXISTS classification;
-- Foreign-key constraints are not enforced by default in SQLite
-- The command below enables foreign keys
PRAGMA foreign_keys = ON;
-- Create Tables
CREATE TABLE user (
  user_id INTEGER PRIMARY KEY AUTOINCREMENT,
  email TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE issue (
  issue_id INTEGER PRIMARY KEY AUTOINCREMENT,
  comment TEXT NOT NULL,
  issue TEXT,
  date_created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  author_id INTEGER NOT NULL,
  classified_id INTEGER NOT NULL,
  FOREIGN KEY (author_id) REFERENCES user (user_id),
  FOREIGN KEY (classified_id) REFERENCES classification (classification_id)
);

CREATE TABLE classification (
  classification_id INTEGER PRIMARY KEY AUTOINCREMENT,
  classification TEXT UNIQUE NOT NULL
)