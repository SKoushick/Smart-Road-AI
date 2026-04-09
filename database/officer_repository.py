import os
import sys
from typing import Optional, List, Dict, Any

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from database.db_connection import get_connection, init_db

# Ensure schema exists at import time
init_db()


# ──────────────────────────────────────────────
# INSERT
# ──────────────────────────────────────────────

def insert_officer(data: Dict[str, Any]) -> int:
    """Insert a new officer record and return their ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO officers
            (officer_name, gmail, password, state, assigned_region, status)
        VALUES
            (:officer_name, :gmail, :password, :state, :assigned_region, :status)
    """, data)
    conn.commit()
    last_id = cursor.lastrowid
    conn.close()
    return last_id


# ──────────────────────────────────────────────
# FETCH
# ──────────────────────────────────────────────

def fetch_all_officers() -> List[Dict[str, Any]]:
    """Return all officers as a list of dicts."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM officers ORDER BY state, assigned_region, officer_name")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


def fetch_officer_by_id(officer_id: int) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM officers WHERE officer_id = ?", (officer_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def authenticate_officer(gmail: str, password: str) -> Optional[Dict[str, Any]]:
    """Check credentials and return officer data if valid."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM officers WHERE lower(gmail) = lower(?) AND password = ? AND status = 'Active'",
        (gmail.strip(), password.strip())
    )
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


# ──────────────────────────────────────────────
# UPDATE
# ──────────────────────────────────────────────

def update_officer(officer_id: int, data: Dict[str, Any]) -> bool:
    """Update officer attributes."""
    conn = get_connection()
    cursor = conn.cursor()
    data["officer_id"] = officer_id
    cursor.execute("""
        UPDATE officers
        SET officer_name = :officer_name,
            gmail = :gmail,
            password = :password,
            state = :state,
            assigned_region = :assigned_region,
            status = :status
        WHERE officer_id = :officer_id
    """, data)
    conn.commit()
    updated = cursor.rowcount > 0
    conn.close()
    return updated


# ──────────────────────────────────────────────
# DELETE
# ──────────────────────────────────────────────

def delete_officer(officer_id: int) -> bool:
    """Permanently remove an officer."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM officers WHERE officer_id = ?", (officer_id,))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted
