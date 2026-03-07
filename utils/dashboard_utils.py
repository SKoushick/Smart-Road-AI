
"""
Dashboard utilities — Plotly chart builders for the analytics page.
"""

import os
import sys
from typing import List, Dict, Any, Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config.settings import SEVERITY_HEX

try:
    import plotly.graph_objects as go
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

import pandas as pd


# ── Shared theme ─────────────────────────────────────────────────────────────
DARK_BG    = "#0f172a"
CARD_BG    = "#1e293b"
TEXT_COLOR = "#e2e8f0"
GRID_COLOR = "#334155"

DARK_TEMPLATE = dict(
    paper_bgcolor=DARK_BG,
    plot_bgcolor=CARD_BG,
    font_color=TEXT_COLOR,
    xaxis=dict(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR),
    yaxis=dict(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR),
)


def _apply_theme(fig):
    fig.update_layout(**DARK_TEMPLATE)
    return fig


# ──────────────────────────────────────────────────────────────────────────────
# Chart functions
# ──────────────────────────────────────────────────────────────────────────────

def monthly_trend_chart(monthly_data: List[Dict[str, Any]]) -> Optional[Any]:
    if not PLOTLY_AVAILABLE or not monthly_data:
        return None

    df = pd.DataFrame(monthly_data)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["month"], y=df["cnt"],
        mode="lines+markers",
        line=dict(color="#F97316", width=3),
        marker=dict(size=8, color="#F97316"),
        fill="tozeroy",
        fillcolor="rgba(249,115,22,0.15)",
        name="Complaints",
    ))
    fig.update_layout(
        title="📈 Monthly Complaint Trends",
        xaxis_title="Month",
        yaxis_title="Complaints",
        **DARK_TEMPLATE,
    )
    return fig


def severity_pie_chart(severity_counts: Dict[str, int]) -> Optional[Any]:
    if not PLOTLY_AVAILABLE or not severity_counts:
        return None

    labels  = list(severity_counts.keys())
    values  = list(severity_counts.values())
    colours = [SEVERITY_HEX.get(l, "#64748b") for l in labels]

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        marker_colors=colours,
        hole=0.45,
        textinfo="label+percent",
        textfont_size=13,
    )])
    fig.update_layout(
        title="🍩 Severity Distribution",
        paper_bgcolor=DARK_BG,
        font_color=TEXT_COLOR,
    )
    return fig


def location_bar_chart(location_data: List[Dict[str, Any]]) -> Optional[Any]:
    if not PLOTLY_AVAILABLE or not location_data:
        return None

    df = pd.DataFrame(location_data).sort_values("cnt", ascending=True)
    fig = go.Figure(go.Bar(
        x=df["cnt"],
        y=df["location_name"],
        orientation="h",
        marker=dict(
            color=df["cnt"],
            colorscale=[[0, "#EAB308"], [0.5, "#F97316"], [1, "#DC2626"]],
            showscale=True,
        ),
        text=df["cnt"],
        textposition="outside",
    ))
    fig.update_layout(
        title="📊 Most Affected Locations",
        xaxis_title="Number of Complaints",
        yaxis_title="",
        height=max(400, len(df) * 36),
        **DARK_TEMPLATE,
    )
    return fig


def status_bar_chart(status_counts: Dict[str, int]) -> Optional[Any]:
    if not PLOTLY_AVAILABLE or not status_counts:
        return None

    colours_map = {
        "Pending":     "#DC2626",
        "In Progress": "#F97316",
        "Resolved":    "#22C55E",
    }
    labels  = list(status_counts.keys())
    values  = list(status_counts.values())
    colours = [colours_map.get(l, "#64748b") for l in labels]

    fig = go.Figure(go.Bar(
        x=labels,
        y=values,
        marker_color=colours,
        text=values,
        textposition="outside",
    ))
    fig.update_layout(
        title="🔧 Resolution Status Overview",
        xaxis_title="Status",
        yaxis_title="Count",
        **DARK_TEMPLATE,
    )
    return fig


def resolution_gauge(resolved: int, total: int) -> Optional[Any]:
    if not PLOTLY_AVAILABLE or total == 0:
        return None

    pct = round(resolved / total * 100, 1)
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=pct,
        delta={"reference": 70, "valueformat": ".1f"},
        title={"text": "Resolution Rate (%)", "font": {"color": TEXT_COLOR}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": TEXT_COLOR},
            "bar":  {"color": "#22C55E"},
            "steps": [
                {"range": [0,   40], "color": "#DC2626"},
                {"range": [40,  70], "color": "#F97316"},
                {"range": [70, 100], "color": "#166534"},
            ],
            "threshold": {
                "line": {"color": "white", "width": 4},
                "thickness": 0.75,
                "value": 70,
            },
        },
        number={"suffix": "%", "font": {"color": TEXT_COLOR}},
    ))
    fig.update_layout(paper_bgcolor=DARK_BG, font_color=TEXT_COLOR, height=280)
    return fig
