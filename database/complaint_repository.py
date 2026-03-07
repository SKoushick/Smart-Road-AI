
import os
import sys
from typing import Optional, List, Dict, Any
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from database.db_connection import get_connection, init_db

# Ensure schema exists at import time
init_db()


# ──────────────────────────────────────────────
# INSERT
# ──────────────────────────────────────────────

def insert_complaint(data: Dict[str, Any]) -> int:
    """Insert a new complaint record and return its ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO complaints
            (name, email, phone, location_name, latitude, longitude,
             description, image_path, image_url, severity_level,
             severity_score, pothole_detected, status, date)
        VALUES
            (:name, :email, :phone, :location_name, :latitude, :longitude,
             :description, :image_path, :image_url, :severity_level,
             :severity_score, :pothole_detected, :status, :date)
    """, data)
    conn.commit()
    last_id = cursor.lastrowid
    conn.close()
    return last_id


# ──────────────────────────────────────────────
# FETCH
# ──────────────────────────────────────────────

def fetch_all_complaints() -> List[Dict[str, Any]]:
    """Return all complaints as a list of dicts."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM complaints ORDER BY date DESC")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


def fetch_complaint_by_id(complaint_id: int) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM complaints WHERE id = ?", (complaint_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def fetch_complaints_by_status(status: str) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM complaints WHERE status = ? ORDER BY date DESC",
        (status,)
    )
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


# ──────────────────────────────────────────────
# UPDATE
# ──────────────────────────────────────────────

def update_complaint_status(
    complaint_id: int,
    new_status: str,
    resolved_by: str = "",
    notes: str = "",
) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE complaints
        SET status = ?, resolved_by = ?, notes = ?
        WHERE id = ?
    """, (new_status, resolved_by, notes, complaint_id))
    conn.commit()
    updated = cursor.rowcount > 0
    conn.close()
    return updated


# ──────────────────────────────────────────────
# DELETE
# ──────────────────────────────────────────────

def delete_complaint(complaint_id: int) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM complaints WHERE id = ?", (complaint_id,))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted


# ──────────────────────────────────────────────
# ANALYTICS HELPERS
# ──────────────────────────────────────────────

def fetch_severity_counts() -> Dict[str, int]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT severity_level, COUNT(*) as cnt FROM complaints GROUP BY severity_level"
    )
    result = {row["severity_level"]: row["cnt"] for row in cursor.fetchall()}
    conn.close()
    return result


def fetch_status_counts() -> Dict[str, int]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT status, COUNT(*) as cnt FROM complaints GROUP BY status"
    )
    result = {row["status"]: row["cnt"] for row in cursor.fetchall()}
    conn.close()
    return result


def fetch_monthly_counts() -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT strftime('%Y-%m', date) AS month, COUNT(*) AS cnt
        FROM complaints
        GROUP BY month
        ORDER BY month
    """)
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


def fetch_location_counts() -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT location_name, COUNT(*) AS cnt
        FROM complaints
        GROUP BY location_name
        ORDER BY cnt DESC
        LIMIT 15
    """)
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows
