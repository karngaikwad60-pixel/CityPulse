import sqlite3

conn = sqlite3.connect("citypulse.db")
cursor = conn.cursor()

cursor.executescript("""

CREATE TABLE IF NOT EXISTS users(
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT,
email TEXT UNIQUE,
phone TEXT,
age INTEGER,
gender TEXT,
password TEXT
);

CREATE TABLE IF NOT EXISTS admins(
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT,
role TEXT,
phone TEXT,
password TEXT,
lat REAL,
lon REAL
);

CREATE TABLE IF NOT EXISTS civic_issues(
id INTEGER PRIMARY KEY AUTOINCREMENT,
user_id INTEGER,
category TEXT,
issue_type TEXT,
description TEXT,
image TEXT,
lat REAL,
lon REAL,
manual_location TEXT,
assigned_admin INTEGER,
status TEXT DEFAULT 'SUBMITTED'
);

CREATE TABLE IF NOT EXISTS emergencies(
id INTEGER PRIMARY KEY AUTOINCREMENT,
user_id INTEGER,
emergency_type TEXT,
lat REAL,
lon REAL,
manual_location TEXT,
image TEXT,
assigned_admin INTEGER,
status TEXT DEFAULT 'SUBMITTED'
);

CREATE TABLE IF NOT EXISTS women_alerts(
id INTEGER PRIMARY KEY AUTOINCREMENT,
user_id INTEGER,
lat REAL,
lon REAL,
assigned_police INTEGER,
status TEXT DEFAULT 'SOS'
);

CREATE TABLE IF NOT EXISTS chat_messages(
id INTEGER PRIMARY KEY AUTOINCREMENT,
request_type TEXT,
request_id INTEGER,
sender TEXT,
sender_id INTEGER,
message TEXT,
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

""")

cursor.execute("""
INSERT OR IGNORE INTO admins
(name,role,phone,password,lat,lon)
VALUES
('Municipal Admin','Municipal','1234567890','municipal123',18.5204,73.8567)
""")

conn.commit()
conn.close()

print("Database created")