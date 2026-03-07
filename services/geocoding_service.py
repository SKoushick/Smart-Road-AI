
"""
Geocoding service — converts a location name string into (lat, lon).

Uses Geopy → Nominatim (OpenStreetMap) with a graceful fallback to a
small hand-curated dictionary of popular Indian cities so the app is
still functional without an internet connection.
"""

import os
import sys
import time
from typing import Tuple, Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# ── Optional geopy ──────────────────────────────────────────────────────────
try:
    from geopy.geocoders import Nominatim
    from geopy.exc import GeocoderTimedOut, GeocoderServiceError
    GEOPY_AVAILABLE = True
except ImportError:
    GEOPY_AVAILABLE = False


# ── Fallback lookup table (lat, lon) ───────────────────────────────────────
FALLBACK_COORDS = {
    "chennai":          (13.0827, 80.2707),
    "coimbatore":       (11.0168, 76.9558),
    "mumbai":           (19.0760, 72.8777),
    "delhi":            (28.6139, 77.2090),
    "bangalore":        (12.9716, 77.5946),
    "bengaluru":        (12.9716, 77.5946),
    "hyderabad":        (17.3850, 78.4867),
    "kolkata":          (22.5726, 88.3639),
    "pune":             (18.5204, 73.8567),
    "ahmedabad":        (23.0225, 72.5714),
    "jaipur":           (26.9124, 75.7873),
    "lucknow":          (26.8467, 80.9462),
    "surat":            (21.1702, 72.8311),
    "nagpur":           (21.1458, 79.0882),
    "indore":           (22.7196, 75.8577),
    "bhopal":           (23.2599, 77.4126),
    "patna":            (25.5941, 85.1376),
    "chandigarh":       (30.7333, 76.7794),
    "kochi":            (9.9312,  76.2673),
    "thiruvananthapuram":(8.5241, 76.9366),
    "madurai":          (9.9252,  78.1197),
    "salem":            (11.6643, 78.1460),
    "trichy":           (10.7905, 78.7047),
    "vellore":          (12.9165, 79.1325),
    "tirunelveli":      (8.7139,  77.7567),
    "erode":            (11.3410, 77.7172),
    "marina beach":     (13.0500, 80.2824),
    "anna university":  (13.0100, 80.2350),
    "gandhipuram":      (11.0200, 76.9680),
    "india":            (20.5937, 78.9629),
}


def _fuzzy_lookup(location: str) -> Optional[Tuple[float, float]]:
    """Try to match any word in the location string against the fallback table."""
    lower = location.lower()
    for key, coords in FALLBACK_COORDS.items():
        if key in lower:
            return coords
    return None


_geolocator = None

def _get_geolocator():
    global _geolocator
    if _geolocator is None and GEOPY_AVAILABLE:
        _geolocator = Nominatim(user_agent="smart_road_monitor_v1")
    return _geolocator


def geocode_location(location_name: str) -> Tuple[Optional[float], Optional[float]]:
    """
    Convert a location name to (latitude, longitude).

    Returns (None, None) if geocoding fails entirely.
    """
    if not location_name or not location_name.strip():
        return None, None

    # 1. Try Nominatim
    if GEOPY_AVAILABLE:
        geo = _get_geolocator()
        for attempt in range(3):
            try:
                result = geo.geocode(location_name, timeout=10)
                if result:
                    return round(result.latitude, 6), round(result.longitude, 6)
                break
            except GeocoderTimedOut:
                time.sleep(1)
            except Exception:
                break

    # 2. Fallback dictionary
    coords = _fuzzy_lookup(location_name)
    if coords:
        return coords

    # 3. Default — centre of India
    return 20.5937, 78.9629


def format_coordinates(lat: Optional[float], lon: Optional[float]) -> str:
    if lat is None or lon is None:
        return "Coordinates not available"
    return f"{lat:.6f}°N, {lon:.6f}°E"
