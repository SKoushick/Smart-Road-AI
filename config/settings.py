
import os

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

# --- AWS S3 (optional – set via environment variables or .env) ---
AWS_ACCESS_KEY_ID     = os.getenv("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")
AWS_REGION            = os.getenv("AWS_REGION", "ap-south-1")
S3_BUCKET_NAME        = os.getenv("S3_BUCKET_NAME", "smart-road-images")

# --- Authentication ---
GOVT_USERNAME = os.getenv("GOVT_USERNAME", "admin")
GOVT_PASSWORD = os.getenv("GOVT_PASSWORD", "admin123")
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
