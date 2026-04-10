import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ===========================================================
# Smart Road Infrastructure Monitoring System - Settings
# ===========================================================

# --- Application ---
import streamlit as st
APP_TITLE = "Smart Road Infrastructure Monitoring System"
APP_ICON = "🚧"
APP_VERSION = "1.0.0"

# --- Database ---
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database", "smart_road.db")

# --- Uploads ---
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads", "temp_images")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Helper for secure secret retrieval
def get_secret(key, default=""):
    try:
        return st.secrets.get(key, os.getenv(key, default))
    except Exception:
        return os.getenv(key, default)

# --- Email Notifications (SendGrid) ---
SENDGRID_API_KEY      = get_secret("SENDGRID_API_KEY")
SENDGRID_SENDER_EMAIL = get_secret("SENDGRID_SENDER_EMAIL")

# --- Authentication ---
GOVT_USERNAME = get_secret("GOVT_USERNAME", "adminsmartroad@gmail.com")
GOVT_PASSWORD = get_secret("GOVT_PASSWORD", "Hindusthan@63")
GOVT_PASSKEY  = get_secret("GOVT_PASSKEY",  "SMARTROAD2024")

# --- AI Model ---
SEVERITY_THRESHOLDS = {
    "low":    (0.0, 0.3),
    "medium": (0.3, 0.7),
    "high":   (0.7, 1.0),
}

# --- Map ---
DEFAULT_MAP_CENTER = {"lat": 20.5937, "lon": 78.9629}  # India centre
MAP_ZOOM = 4

# --- Severity colour palette ---
SEVERITY_COLOURS = {
    "High":     [220, 38,  38],    # red
    "Medium":   [249, 115, 22],    # orange
    "Low":      [234, 179, 8],     # yellow
    "Resolved": [34,  197, 94],    # green
}

SEVERITY_HEX = {
    "High":     "#DC2626",
    "Medium":   "#F97316",
    "Low":      "#EAB308",
    "Resolved": "#22C55E",
}

# --- Status options ---
STATUS_OPTIONS = ["Pending", "In Progress", "Resolved"]
