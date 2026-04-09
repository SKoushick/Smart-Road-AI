import sqlite3
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config.settings import DB_PATH


def get_connection() -> sqlite3.Connection:
    """Return a SQLite connection with row_factory set."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Create tables if they do not exist."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS complaints (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            name            TEXT    NOT NULL,
            email           TEXT,
            phone           TEXT,
            location_name   TEXT    NOT NULL,
            latitude        REAL,
            longitude       REAL,
            description     TEXT,
            image_path      TEXT,
            image_url       TEXT,
            severity_level  TEXT    DEFAULT 'Unknown',
            severity_score  REAL    DEFAULT 0.0,
            pothole_detected INTEGER DEFAULT 0,
            status          TEXT    DEFAULT 'Pending',
            date            TEXT    NOT NULL,
            resolved_by     TEXT,
            notes           TEXT
        )
    """)

    # Alter complaints table to add new columns if they don't exist
    try:
        cursor.execute("ALTER TABLE complaints ADD COLUMN assigned_officer_id INTEGER")
    except sqlite3.OperationalError:
        pass
    
    try:
        cursor.execute("ALTER TABLE complaints ADD COLUMN assigned_time TEXT")
    except sqlite3.OperationalError:
        pass
        
    try:
        cursor.execute("ALTER TABLE complaints ADD COLUMN repair_status TEXT")
    except sqlite3.OperationalError:
        pass

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS officers (
            officer_id INTEGER PRIMARY KEY AUTOINCREMENT,
            officer_name TEXT NOT NULL,
            gmail TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            state TEXT NOT NULL,
            assigned_region TEXT,
            status TEXT DEFAULT 'Active'
        )
    """)

    # Create dummy officers if none exist
    cursor.execute("SELECT COUNT(*) as cnt FROM officers")
    if cursor.fetchone()["cnt"] == 0:
        demo_officers = [
            ("Officer 1", "Koushick715@gmail.com", "Hindusthan@1", "Tamil Nadu", "Chennai", "Active"),
            ("Officer 2", "720823108063@hit.edu.in", "Hindusthan@2", "Tamil Nadu", "Madurai", "Active"),
            ("Officer 3", "720823108022@hit.edu.in", "Hindusthan@3", "Tamil Nadu", "Coimbatore", "Active"),
            ("Officer 4", "720823108054@hit.edu.in", "Hindusthan@4", "Tamil Nadu", "Salem", "Active"),
            ("Officer 5", "720823108042@hit.edu.in", "Hindusthan@5", "Tamil Nadu", "Trichy", "Active"),
            ("Officer 6", "gvmadhubalan@gmail.com", "Hindusthan@6", "Tamil Nadu", "Kanyakumari", "Active")
        ]
        cursor.executemany("""
            INSERT INTO officers (officer_name, gmail, password, state, assigned_region, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, demo_officers)

    conn.commit()
    conn.close()
