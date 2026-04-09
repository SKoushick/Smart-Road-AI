import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ===========================================================
# Smart Road Infrastructure Monitoring System - Settings
# ===========================================================

# --- Application ---
APP_TITLE = "Smart Road Infrastructure Monitoring System"
APP_ICON = "🚧"
APP_VERSION = "1.0.0"

# --- Database ---
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database", "smart_road.db")

# --- Uploads ---
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads", "temp_images")
os.makedirs(UPLOAD_DIR, exist_ok=True)



# --- Email Notifications (SendGrid) ---
SENDGRID_API_KEY      = os.getenv("SENDGRID_API_KEY", "")
SENDGRID_SENDER_EMAIL = os.getenv("SENDGRID_SENDER_EMAIL", "")

# --- Authentication ---
GOVT_USERNAME = os.getenv("GOVT_USERNAME", "adminsmartroad@gmail.com")
GOVT_PASSWORD = os.getenv("GOVT_PASSWORD", "Hindusthan@63")
GOVT_PASSKEY  = os.getenv("GOVT_PASSKEY",  "SMARTROAD2024")

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
