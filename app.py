
"""
app.py — Smart Road Infrastructure Monitoring System
Main Streamlit entry point / Home page.
"""

import os
import sys

import streamlit as st

# ── path bootstrap ────────────────────────────────────────────────────────────
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from database.db_connection import init_db
from database.complaint_repository import (
    fetch_all_complaints,
    fetch_severity_counts,
    fetch_status_counts,
)
from config.settings import APP_TITLE, APP_ICON, APP_VERSION

# ── ensure DB schema exists ───────────────────────────────────────────────────
init_db()

# ── page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════════════════════
# Global CSS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;0,900;1,400&display=swap');

/* ─── Reset & Base ───────────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewBlockContainer"] {
    background: #0a0f1e !important;
    font-family: 'Inter', sans-serif !important;
    color: #e2e8f0 !important;
}

/* ─── Sidebar ────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1528 0%, #0a0f1e 100%) !important;
    border-right: 1px solid #1e293b !important;
}
[data-testid="stSidebar"] * { color: #cbd5e1 !important; }
[data-testid="stSidebar"] a:hover { color: #f97316 !important; }

/* ─── Headings ───────────────────────────────────────────────── */
h1, h2, h3, h4 { color: #f1f5f9 !important; }

/* ─── Hide default header decorations ───────────────────────── */
[data-testid="stDecoration"] { display: none !important; }
#MainMenu { visibility: hidden; }
footer    { visibility: hidden; }

/* ─── Hero section ───────────────────────────────────────────── */
.hero {
    background: linear-gradient(135deg, #0f2447 0%, #1a0a2e 60%, #0c1a3a 100%);
    border: 1px solid #1e3a5f;
    border-radius: 24px;
    padding: 56px 60px;
    position: relative;
    overflow: hidden;
    margin-bottom: 36px;
}
.hero::before {
    content: '';
    position: absolute;
    top: -80px; right: -80px;
    width: 500px; height: 500px;
    background: radial-gradient(circle, rgba(249,115,22,0.12) 0%, transparent 70%);
    border-radius: 50%;
    pointer-events: none;
}
.hero::after {
    content: '';
    position: absolute;
    bottom: -100px; left: 40%;
    width: 400px; height: 400px;
    background: radial-gradient(circle, rgba(96,165,250,0.08) 0%, transparent 70%);
    border-radius: 50%;
    pointer-events: none;
}
.hero-eyebrow {
    display: inline-block;
    background: linear-gradient(135deg, rgba(249,115,22,0.2), rgba(251,191,36,0.15));
    border: 1px solid rgba(249,115,22,0.4);
    border-radius: 50px;
    padding: 5px 18px;
    font-size: 0.78rem;
    font-weight: 600;
    color: #fbbf24;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 18px;
}
.hero-title {
    font-size: clamp(2rem, 4vw, 3rem);
    font-weight: 900;
    background: linear-gradient(90deg, #f97316 0%, #fbbf24 50%, #60a5fa 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 1.15;
    margin-bottom: 16px;
}
.hero-sub {
    color: #94a3b8;
    font-size: 1.05rem;
    line-height: 1.7;
    max-width: 620px;
    margin-bottom: 30px;
}
.hero-badges {
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
}
.hero-badge {
    background: rgba(255,255,255,0.05);
    border: 1px solid #334155;
    border-radius: 50px;
    padding: 6px 16px;
    font-size: 0.82rem;
    color: #94a3b8;
    backdrop-filter: blur(4px);
}

/* ─── KPI cards ──────────────────────────────────────────────── */
.kpi-grid { display: flex; gap: 16px; flex-wrap: wrap; margin-bottom: 36px; }
.kpi {
    flex: 1;
    min-width: 150px;
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 18px;
    padding: 24px 20px;
    text-align: center;
    position: relative;
    overflow: hidden;
    transition: transform 0.25s, border-color 0.25s, box-shadow 0.25s;
}
.kpi::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: var(--kpi-accent, #60a5fa);
    border-radius: 18px 18px 0 0;
}
.kpi:hover {
    transform: translateY(-6px);
    border-color: #475569;
    box-shadow: 0 16px 40px rgba(0,0,0,0.4);
}
.kpi-icon { font-size: 1.6rem; margin-bottom: 10px; }
.kpi-num  { font-size: 2.4rem; font-weight: 800; color: var(--kpi-accent, #60a5fa); line-height: 1; }
.kpi-lbl  { font-size: 0.75rem; color: #64748b; margin-top: 8px; text-transform: uppercase; letter-spacing: 0.06em; }

/* ─── Feature cards ──────────────────────────────────────────── */
.feat-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px,1fr)); gap: 18px; margin-bottom: 36px; }
.feat-card {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 18px;
    padding: 28px 22px;
    transition: transform 0.25s, border-color 0.25s, box-shadow 0.25s;
    position: relative;
    overflow: hidden;
}
.feat-card::after {
    content: '';
    position: absolute;
    bottom: 0; right: 0;
    width: 80px; height: 80px;
    background: radial-gradient(circle, var(--feat-glow, rgba(249,115,22,0.12)) 0%, transparent 70%);
    border-radius: 50%;
}
.feat-card:hover {
    transform: translateY(-5px);
    border-color: var(--feat-border, #f97316);
    box-shadow: 0 12px 40px rgba(0,0,0,0.35);
}
.feat-icon { font-size: 2rem; margin-bottom: 14px; }
.feat-title { font-size: 1rem; font-weight: 700; color: #f1f5f9; margin-bottom: 8px; }
.feat-desc  { font-size: 0.83rem; color: #64748b; line-height: 1.6; }

/* ─── Flow steps ─────────────────────────────────────────────── */
.flow-step {
    display: flex;
    align-items: flex-start;
    gap: 18px;
    padding: 18px 20px;
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 14px;
    margin-bottom: 10px;
    transition: border-color 0.2s;
}
.flow-step:hover { border-color: #f97316; }
.flow-num {
    width: 36px; height: 36px;
    border-radius: 50%;
    background: linear-gradient(135deg, #f97316, #ea580c);
    color: white;
    font-weight: 800;
    font-size: 0.9rem;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    box-shadow: 0 4px 12px rgba(249,115,22,0.4);
}
.flow-body .flow-title { font-weight: 700; color: #f1f5f9; font-size: 0.95rem; }
.flow-body .flow-desc  { color: #64748b; font-size: 0.82rem; margin-top: 3px; }

/* ─── Section heading ────────────────────────────────────────── */
.sec-heading {
    font-size: 0.7rem;
    font-weight: 700;
    color: #475569;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 10px;
}
.sec-heading::after {
    content: '';
    flex: 1;
    height: 1px;
    background: #1e293b;
}

/* ─── Sidebar nav helper ──────────────────────────────────────── */
.nav-hint {
    background: linear-gradient(135deg, #1e3a5f, #1a2744);
    border: 1px solid #334155;
    border-radius: 14px;
    padding: 20px;
    margin-top: 20px;
}
.nav-hint p { color: #94a3b8; font-size: 0.83rem; margin: 0; }

/* ─── Buttons ────────────────────────────────────────────────── */
div[data-testid="stButton"] > button {
    background: linear-gradient(135deg, #f97316, #ea580c) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
    padding: 14px 28px !important;
    font-size: 1rem !important;
    letter-spacing: 0.02em !important;
    transition: all 0.25s ease !important;
    box-shadow: 0 4px 20px rgba(249,115,22,0.35) !important;
}
div[data-testid="stButton"] > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 30px rgba(249,115,22,0.55) !important;
}

/* ─── Plotly chart background fix ────────────────────────────── */
.js-plotly-plot .plotly { background: transparent !important; }

/* ─── Footer ─────────────────────────────────────────────────── */
.custom-footer {
    text-align: center;
    color: #1e293b;
    font-size: 0.78rem;
    margin-top: 48px;
    padding-top: 20px;
    border-top: 1px solid #1e293b;
}
.custom-footer span { color: #334155; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# Sidebar
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(f"""
    <div style='text-align:center; padding: 24px 0 20px 0;'>
        <div style='font-size:2.8rem;'>🚧</div>
        <div style='font-weight:800; font-size:1.05rem; color:#f1f5f9; margin-top:8px;'>
            Smart Road Monitor
        </div>
        <div style='font-size:0.72rem; color:#475569; margin-top:4px;'>v{APP_VERSION}</div>
    </div>
    <hr style='border-color:#1e293b; margin:0 0 16px 0;'>
    """, unsafe_allow_html=True)

    st.markdown("""
    **Navigation**

    Use the pages below to explore the system:

    - 🏠 **Home** — You are here
    - 🚧 **Report Damage** — Submit a complaint
    - 🏛️ **Government Panel** — Authority dashboard
    - 📋 **Complaint History** — View all reports
    - 📊 **Analytics** — Insights & charts
    """)

    st.markdown("""
    <hr style='border-color:#1e293b; margin:16px 0;'>
    <div style='font-size:0.75rem; color:#334155; text-align:center;'>
        🔐 Govt Login: <code style='color:#64748b;'>admin / admin123</code><br>
        Passkey: <code style='color:#64748b;'>SMARTROAD2024</code>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# Live data
# ══════════════════════════════════════════════════════════════════════════════
all_complaints  = fetch_all_complaints()
severity_counts = fetch_severity_counts()
status_counts   = fetch_status_counts()

total    = len(all_complaints)
resolved = status_counts.get("Resolved", 0)
pending  = status_counts.get("Pending",  0)
high_sev = severity_counts.get("High",   0)
res_rate = f"{resolved/total*100:.0f}%" if total > 0 else "—"


# ══════════════════════════════════════════════════════════════════════════════
# Hero
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="hero">
    <div class="hero-eyebrow">🇮🇳 Smart City Initiative • AI-Powered</div>
    <div class="hero-title">Smart Road Infrastructure<br>Monitoring System</div>
    <div class="hero-sub">
        An AI-powered civic platform that lets citizens report potholes and road
        damage instantly. Government authorities get a real-time monitoring panel,
        while urban planners gain deep infrastructure analytics.
    </div>
    <div class="hero-badges">
        <span class="hero-badge">🤖 CNN / YOLO Detection</span>
        <span class="hero-badge">🗺️ PyDeck Mapping</span>
        <span class="hero-badge">☁️ AWS S3 Storage</span>
        <span class="hero-badge">📊 Plotly Analytics</span>
        <span class="hero-badge">🔐 Gov't Auth</span>
    </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# Live KPIs
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="sec-heading">Live System Stats</div>', unsafe_allow_html=True)

st.markdown(f"""
<div class="kpi-grid">
    <div class="kpi" style="--kpi-accent:#60a5fa;">
        <div class="kpi-icon">📝</div>
        <div class="kpi-num">{total}</div>
        <div class="kpi-lbl">Total Complaints</div>
    </div>
    <div class="kpi" style="--kpi-accent:#ef4444;">
        <div class="kpi-icon">⏳</div>
        <div class="kpi-num">{pending}</div>
        <div class="kpi-lbl">Pending</div>
    </div>
    <div class="kpi" style="--kpi-accent:#22c55e;">
        <div class="kpi-icon">✅</div>
        <div class="kpi-num">{resolved}</div>
        <div class="kpi-lbl">Resolved</div>
    </div>
    <div class="kpi" style="--kpi-accent:#dc2626;">
        <div class="kpi-icon">🚨</div>
        <div class="kpi-num">{high_sev}</div>
        <div class="kpi-lbl">High Severity</div>
    </div>
    <div class="kpi" style="--kpi-accent:#a78bfa;">
        <div class="kpi-icon">📈</div>
        <div class="kpi-num">{res_rate}</div>
        <div class="kpi-lbl">Resolution Rate</div>
    </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# Feature Overview
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="sec-heading">Platform Features</div>', unsafe_allow_html=True)

st.markdown("""
<div class="feat-grid">
    <div class="feat-card" style="--feat-border:#f97316; --feat-glow:rgba(249,115,22,0.12);">
        <div class="feat-icon">🚧</div>
        <div class="feat-title">Citizen Complaint Portal</div>
        <div class="feat-desc">
            Upload pothole images, enter location and description. Our AI
            analyses severity in seconds and files your report automatically.
        </div>
    </div>
    <div class="feat-card" style="--feat-border:#ef4444; --feat-glow:rgba(239,68,68,0.12);">
        <div class="feat-icon">🤖</div>
        <div class="feat-title">AI Pothole Detection</div>
        <div class="feat-desc">
            CNN / ResNet-18 model classifies damage severity as Low, Medium,
            or High with a confidence score from 0 to 1.
        </div>
    </div>
    <div class="feat-card" style="--feat-border:#60a5fa; --feat-glow:rgba(96,165,250,0.12);">
        <div class="feat-icon">🗺️</div>
        <div class="feat-title">Interactive Map</div>
        <div class="feat-desc">
            Location names are geocoded to GPS coordinates and displayed on
            a 3‑D PyDeck map with colour-coded severity markers.
        </div>
    </div>
    <div class="feat-card" style="--feat-border:#22c55e; --feat-glow:rgba(34,197,94,0.12);">
        <div class="feat-icon">🏛️</div>
        <div class="feat-title">Government Panel</div>
        <div class="feat-desc">
            Passkey-protected authority dashboard. View, filter, assign
            officers, and update complaint statuses in one click.
        </div>
    </div>
    <div class="feat-card" style="--feat-border:#a78bfa; --feat-glow:rgba(167,139,250,0.12);">
        <div class="feat-icon">📊</div>
        <div class="feat-title">Analytics Dashboard</div>
        <div class="feat-desc">
            Monthly trends, severity breakdown, location heat maps, and
            resolution rate gauge — all in an interactive Plotly dashboard.
        </div>
    </div>
    <div class="feat-card" style="--feat-border:#fbbf24; --feat-glow:rgba(251,191,36,0.12);">
        <div class="feat-icon">☁️</div>
        <div class="feat-title">Cloud Storage</div>
        <div class="feat-desc">
            Images auto-upload to AWS S3. Metadata (coordinates, severity,
            status) is stored in SQLite for fast local queries.
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# How it works
# ══════════════════════════════════════════════════════════════════════════════
left_col, right_col = st.columns([3, 2], gap="large")

with left_col:
    st.markdown('<div class="sec-heading">How It Works</div>', unsafe_allow_html=True)

    steps = [
        ("Citizen uploads image",
         "Upload a clear photo of the road damage along with your details and location name."),
        ("AI analyses the image",
         "Our CNN model predicts pothole presence and severity score (0–1) in real time."),
        ("Location is geocoded",
         "The location name is converted to GPS coordinates (lat/lon) via Geopy + Nominatim."),
        ("Data stored securely",
         "Image goes to AWS S3; metadata (severity, coords, status) is saved to SQLite."),
        ("Government reviews",
         "Authorities log in with a passkey, view complaints on the map, and assign officers."),
        ("Analytics updated",
         "Charts, heat maps, and KPIs refresh automatically as new reports arrive."),
    ]
    for i, (title, desc) in enumerate(steps, 1):
        st.markdown(f"""
        <div class="flow-step">
            <div class="flow-num">{i}</div>
            <div class="flow-body">
                <div class="flow-title">{title}</div>
                <div class="flow-desc">{desc}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

with right_col:
    st.markdown('<div class="sec-heading">Severity Legend</div>', unsafe_allow_html=True)

    legend = [
        ("🔴", "High",     "#DC2626", "Score 0.7 – 1.0",  "Immediate action required"),
        ("🟠", "Medium",   "#F97316", "Score 0.3 – 0.7",  "Repair within 2 weeks"),
        ("🟡", "Low",      "#EAB308", "Score 0.0 – 0.3",  "Schedule for routine maintenance"),
        ("🟢", "Resolved", "#22C55E", "Any score",         "Repaired & verified"),
    ]
    for icon, label, clr, score, action in legend:
        st.markdown(f"""
        <div style='background:#1e293b; border:1px solid #334155; border-left: 4px solid {clr};
                    border-radius:12px; padding:14px 18px; margin-bottom:10px;
                    transition:transform 0.2s;'>
            <div style='font-weight:700; color:{clr}; font-size:0.95rem;'>{icon} {label}</div>
            <div style='color:#64748b; font-size:0.8rem; margin-top:4px;'>{score}</div>
            <div style='color:#94a3b8; font-size:0.82rem;'>{action}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="sec-heading">Tech Stack</div>', unsafe_allow_html=True)

    tech = [
        ("🐍", "Streamlit",   "Web framework"),
        ("📊", "Plotly",      "Charts & analytics"),
        ("🗺️", "PyDeck",      "3-D map visualisation"),
        ("📍", "Geopy",       "Location geocoding"),
        ("🤖", "PyTorch",     "AI / CNN model"),
        ("☁️", "AWS S3",      "Image cloud storage"),
        ("🗄️", "SQLite",      "Local metadata DB"),
    ]
    for icon, name, desc in tech:
        st.markdown(f"""
        <div style='display:flex; align-items:center; gap:12px; padding:9px 14px;
                    background:#1e293b; border-radius:10px; margin-bottom:8px;
                    border:1px solid #334155;'>
            <span style='font-size:1.1rem;'>{icon}</span>
            <span style='font-weight:600; color:#f1f5f9; font-size:0.88rem;'>{name}</span>
            <span style='color:#475569; font-size:0.8rem; margin-left:auto;'>{desc}</span>
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# CTA
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("""
<div style='background: linear-gradient(135deg, #0f2447 0%, #1a0a2e 100%);
            border: 1px solid #334155; border-radius: 20px;
            padding: 40px; text-align: center; margin-bottom: 30px;'>
    <h2 style='color:#f1f5f9; font-size:1.6rem; margin-bottom:12px;'>
        Ready to report road damage? 🚧
    </h2>
    <p style='color:#94a3b8; margin-bottom:24px;'>
        Use the sidebar to navigate to the <strong style='color:#f97316;'>Report Damage</strong> page
        and submit your first complaint in under 2 minutes.
    </p>
</div>
""", unsafe_allow_html=True)

# Latest 5 complaints preview
if all_complaints:
    st.markdown('<div class="sec-heading">Recent Complaints</div>', unsafe_allow_html=True)
    for c in all_complaints[:5]:
        from config.settings import SEVERITY_HEX
        sev_col  = SEVERITY_HEX.get(c.get("severity_level", "Unknown"), "#64748b")
        stat_map = {"Pending": "#ef4444", "In Progress": "#f97316", "Resolved": "#22c55e"}
        sta_col  = stat_map.get(c.get("status", ""), "#64748b")
        st.markdown(f"""
        <div style='background:#1e293b; border:1px solid #334155; border-radius:12px;
                    padding:14px 18px; margin-bottom:8px; display:flex;
                    justify-content:space-between; align-items:center;
                    transition:border-color 0.2s;'>
            <div>
                <span style='color:#60a5fa; font-size:0.78rem; font-weight:700;'>
                    #SMRT-{c["id"]:04d}
                </span>
                <span style='color:#e2e8f0; font-weight:600; margin-left:10px;'>
                    📍 {c["location_name"]}
                </span>
                <span style='color:#64748b; font-size:0.8rem; margin-left:12px;'>
                    {str(c["date"])[:10]}
                </span>
            </div>
            <div style='display:flex; gap:8px;'>
                <span style='background:{sev_col}22; color:{sev_col};
                             border:1px solid {sev_col}; padding:2px 12px;
                             border-radius:50px; font-size:0.75rem; font-weight:700;'>
                    {c["severity_level"]}
                </span>
                <span style='background:{sta_col}22; color:{sta_col};
                             border:1px solid {sta_col}; padding:2px 12px;
                             border-radius:50px; font-size:0.75rem; font-weight:600;'>
                    {c["status"]}
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)


# ── footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="custom-footer">
    <span>Smart Road Infrastructure Monitoring System</span> •
    <span>AI-Powered Civic Complaint Platform</span> •
    <span>Built with Streamlit 🚀</span>
</div>
""", unsafe_allow_html=True)
