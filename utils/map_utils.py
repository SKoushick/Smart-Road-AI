
"""
Map utilities — build PyDeck / pydeck layers from complaint data.
"""

import os
import sys
from typing import List, Dict, Any

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config.settings import SEVERITY_COLOURS, DEFAULT_MAP_CENTER, MAP_ZOOM

try:
    import pydeck as pdk
    PYDECK_AVAILABLE = True
except ImportError:
    PYDECK_AVAILABLE = False


# ──────────────────────────────────────────────────────────────────────────────
# Colour mapping
# ──────────────────────────────────────────────────────────────────────────────

def _get_colour(complaint: Dict[str, Any]) -> List[int]:
    if complaint.get("status") == "Resolved":
        return SEVERITY_COLOURS["Resolved"]
    level = complaint.get("severity_level", "Low")
    return SEVERITY_COLOURS.get(level, [100, 100, 100])


# ──────────────────────────────────────────────────────────────────────────────
# Build pydeck map
# ──────────────────────────────────────────────────────────────────────────────

def build_complaint_map(complaints: List[Dict[str, Any]]):
    """
    Build and return a pydeck.Deck object ready to pass to st.pydeck_chart.
    Returns None if pydeck is not installed or no valid coordinates exist.
    """
    if not PYDECK_AVAILABLE:
        return None

    valid = [
        c for c in complaints
        if c.get("latitude") is not None and c.get("longitude") is not None
    ]
    if not valid:
        return None

    for c in valid:
        c["colour"] = _get_colour(c)
        c["radius"] = 800 if c.get("severity_level") == "High" else (
                       550 if c.get("severity_level") == "Medium" else 350)

    # Scatterplot layer
    scatter_layer = pdk.Layer(
        "ScatterplotLayer",
        data=valid,
        get_position=["longitude", "latitude"],
        get_fill_color="colour",
        get_radius="radius",
        pickable=True,
        opacity=0.8,
        stroked=True,
        get_line_color=[255, 255, 255],
        line_width_min_pixels=1,
    )

    # Tooltip
    tooltip = {
        "html": """
            <div style='font-family:sans-serif; padding:6px;'>
                <b>📍 {location_name}</b><br/>
                <span style='color:#F97316;'>Severity:</span> {severity_level}
                ({severity_score})<br/>
                <span style='color:#60a5fa;'>Status:</span> {status}<br/>
                Reported by: {name}<br/>
                Date: {date}
            </div>
        """,
        "style": {
            "backgroundColor": "#1e293b",
            "color": "white",
            "borderRadius": "8px",
        },
    }

    # Determine map centre
    lats = [c["latitude"]  for c in valid]
    lons = [c["longitude"] for c in valid]
    centre_lat = sum(lats) / len(lats)
    centre_lon = sum(lons) / len(lons)

    # View state
    view_state = pdk.ViewState(
        latitude=centre_lat,
        longitude=centre_lon,
        zoom=MAP_ZOOM,
        pitch=40,
        bearing=0,
    )

    return pdk.Deck(
        layers=[scatter_layer],
        initial_view_state=view_state,
        tooltip=tooltip,
        map_style="https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json",
    )


def build_heatmap(complaints: List[Dict[str, Any]]):
    """Return a heatmap deck for density visualisation."""
    if not PYDECK_AVAILABLE:
        return None

    valid = [
        {"latitude": c["latitude"], "longitude": c["longitude"], "weight": 1}
        for c in complaints
        if c.get("latitude") is not None and c.get("longitude") is not None
    ]
    if not valid:
        return None

    layer = pdk.Layer(
        "HeatmapLayer",
        data=valid,
        get_position=["longitude", "latitude"],
        get_weight="weight",
        aggregation="SUM",
        radius_pixels=60,
    )

    lats = [v["latitude"]  for v in valid]
    lons = [v["longitude"] for v in valid]

    view_state = pdk.ViewState(
        latitude=sum(lats) / len(lats),
        longitude=sum(lons) / len(lons),
        zoom=MAP_ZOOM,
        pitch=0,
    )

    return pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        map_style="https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json",
    )
