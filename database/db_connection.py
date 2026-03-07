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

    conn.commit()
    conn.close()
