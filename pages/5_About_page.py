
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
from utils.theme_utils import inject_global_css

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
# Global Settings & Theme
# ══════════════════════════════════════════════════════════════════════════════
inject_global_css()

st.markdown("""
<style>
/* ─── App Page Specific Styles ───────────────────────────────────────────── */
.hero {
    position: relative;
    padding: 80px 60px;
    border-radius: 32px;
    background: rgba(30, 41, 59, 0.4);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    overflow: hidden;
    margin-bottom: 40px;
    text-align: center;
    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
}
.hero::before {
    content: '';
    position: absolute;
    top: -50%; left: -20%;
    width: 600px; height: 600px;
    background: radial-gradient(circle, rgba(99, 102, 241, 0.3) 0%, transparent 60%);
    border-radius: 50%;
    pointer-events: none;
    animation: pulse 8s ease-in-out infinite alternate;
}
.hero::after {
    content: '';
    position: absolute;
    bottom: -30%; right: -10%;
    width: 500px; height: 500px;
    background: radial-gradient(circle, rgba(236, 72, 153, 0.25) 0%, transparent 60%);
    border-radius: 50%;
    pointer-events: none;
    animation: pulse 6s ease-in-out infinite alternate-reverse;
}
@keyframes pulse {
    0% { transform: scale(1); opacity: 0.8; }
    100% { transform: scale(1.1); opacity: 1; }
}
.hero-eyebrow {
    display: inline-block;
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.2);
    border-radius: 50px;
    padding: 8px 24px;
    font-size: 0.85rem;
    font-weight: 700;
    color: #cbd5e1;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 24px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}
.hero-title {
    font-size: clamp(3rem, 5vw, 4.5rem);
    font-weight: 900;
    line-height: 1.1;
    margin-bottom: 24px;
    background: linear-gradient(135deg, #fff 0%, #cbd5e1 50%, #94a3b8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.hero-title span {
    background: linear-gradient(135deg, #6366f1 0%, #a855f7 50%, #ec4899 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.hero-sub {
    color: #94a3b8;
    font-size: 1.15rem;
    line-height: 1.8;
    max-width: 700px;
    margin: 0 auto 36px;
    font-weight: 400;
}
.hero-badges {
    display: flex;
    justify-content: center;
    gap: 16px;
    flex-wrap: wrap;
    position: relative;
    z-index: 2;
}
.hero-badge {
    background: rgba(15, 23, 42, 0.6);
    border: 1px solid rgba(99, 102, 241, 0.3);
    border-radius: 12px;
    padding: 10px 20px;
    font-size: 0.9rem;
    font-weight: 600;
    color: #e2e8f0;
    transition: all 0.3s ease;
}
.hero-badge:hover {
    background: rgba(99, 102, 241, 0.2);
    border-color: #8b5cf6;
    transform: translateY(-2px);
}

/* ─── Glowing Neon KPI Cards ────────────────────────────────────────────── */
.kpi-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 20px; margin-bottom: 48px; }
.kpi {
    background: rgba(30, 41, 59, 0.5);
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 20px;
    padding: 30px 24px;
    text-align: center;
    position: relative;
    overflow: hidden;
    backdrop-filter: blur(12px);
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}
.kpi::before {
    content: '';
    position: absolute;
    inset: 0;
    background: radial-gradient(800px circle at var(--mouse-x, 50%) var(--mouse-y, 50%), var(--kpi-glow, rgba(255,255,255,0.06)), transparent 40%);
    opacity: 0;
    transition: opacity 0.5s;
}
.kpi:hover::before { opacity: 1; }
.kpi:hover {
    transform: translateY(-8px) scale(1.02);
    border-color: var(--kpi-glow, #fff);
    box-shadow: 0 20px 40px -10px var(--kpi-glow-dim, rgba(0,0,0,0.5));
}
.kpi-icon { font-size: 2.5rem; margin-bottom: 12px; filter: drop-shadow(0 0 10px var(--kpi-glow)); }
.kpi-num  { font-size: 2.8rem; font-weight: 900; color: #fff; line-height: 1; margin-bottom: 8px; text-shadow: 0 0 20px var(--kpi-glow-dim); }
.kpi-lbl  { font-size: 0.85rem; color: #94a3b8; font-weight: 500; text-transform: uppercase; letter-spacing: 0.08em; }

/* ─── 3D Feature Cards ──────────────────────────────────────────── */
.feat-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px,1fr)); gap: 24px; margin-bottom: 48px; perspective: 1000px; }
.feat-card {
    background: linear-gradient(165deg, rgba(30,41,59,0.7) 0%, rgba(15,23,42,0.8) 100%);
    border: 1px solid rgba(255,255,255,0.1);
    border-top: 1px solid rgba(255,255,255,0.2);
    border-left: 1px solid rgba(255,255,255,0.2);
    border-radius: 24px;
    padding: 36px 28px;
    transition: transform 0.5s ease, box-shadow 0.5s ease;
    transform-style: preserve-3d;
}
.feat-card:hover {
    transform: translateY(-10px) rotateX(5deg) rotateY(-5deg);
    box-shadow: 20px 20px 40px rgba(0,0,0,0.4), -10px -10px 20px rgba(255,255,255,0.05);
    border-color: var(--feat-accent);
}
.feat-icon-wrap {
    width: 64px; height: 64px;
    border-radius: 16px;
    background: var(--feat-bg);
    display: flex; align-items: center; justify-content: center;
    font-size: 2rem;
    margin-bottom: 24px;
    border: 1px solid rgba(255,255,255,0.2);
    box-shadow: inset 0 0 20px rgba(255,255,255,0.2);
}
.feat-title { font-size: 1.3rem; font-weight: 800; color: #fff; margin-bottom: 12px; letter-spacing: -0.01em; }
.feat-desc  { font-size: 0.95rem; color: #94a3b8; line-height: 1.6; font-weight: 400; }

/* ─── Modern Flow Steps ─────────────────────────────────────────────── */
.flow-container {
    background: rgba(15, 23, 42, 0.4);
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 24px;
    padding: 32px;
}
.flow-step {
    display: flex;
    align-items: flex-start;
    gap: 24px;
    padding: 20px;
    background: rgba(255,255,255,0.02);
    border-radius: 16px;
    margin-bottom: 16px;
    transition: all 0.3s;
    border-left: 4px solid transparent;
}
.flow-step:hover { background: rgba(255,255,255,0.05); border-left-color: #a855f7; transform: translateX(5px); }
.flow-num {
    width: 44px; height: 44px;
    border-radius: 12px;
    background: linear-gradient(135deg, #6366f1, #ec4899);
    color: white; font-weight: 800; font-size: 1.2rem;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0; box-shadow: 0 10px 20px rgba(236,72,153,0.3);
}
.flow-body .flow-title { font-weight: 800; color: #f8fafc; font-size: 1.1rem; margin-bottom: 4px; }
.flow-body .flow-desc  { color: #cbd5e1; font-size: 0.9rem; line-height: 1.5; }

/* ─── Section heading ────────────────────────────────────────── */
.sec-heading {
    font-size: 2rem;
    font-weight: 800;
    color: #fff;
    margin: 60px 0 30px;
    position: relative;
    display: inline-block;
}
.sec-heading::after {
    content: '';
    position: absolute;
    bottom: -8px; left: 0;
    width: 100%; height: 4px;
    background: linear-gradient(90deg, #6366f1, transparent);
    border-radius: 4px;
}

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
        🔐 Govt Login: <code style='color:#64748b;'>adminsmartroad@gmail.com / Hindusthan@63</code><br>
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
st.markdown("""
<div class="hero">
    <div class="hero-eyebrow">⚡ Next-Gen Infrastructure Monitoring</div>
    <div class="hero-title">Smart Road <span>Dashboard</span></div>
    <div class="hero-sub">
        An AI-powered civic platform utilizing advanced Deep Learning and dynamic PyDeck maps to process citizen damage reports globally.
    </div>
    <div class="hero-badges">
        <span class="hero-badge">🤖 Deep Learning Vision</span>
        <span class="hero-badge">🗺️ 3D Mapping</span>
        <span class="hero-badge">📊 Predictive Analytics</span>
    </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# Live KPIs
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="sec-heading">System Pulse</div>', unsafe_allow_html=True)

st.markdown(f"""
<div class="kpi-grid">
    <div class="kpi" style="--kpi-glow:#6366f1; --kpi-glow-dim:rgba(99,102,241,0.4);">
        <div class="kpi-icon">📋</div>
        <div class="kpi-num">{total}</div>
        <div class="kpi-lbl">Total Reports</div>
    </div>
    <div class="kpi" style="--kpi-glow:#f59e0b; --kpi-glow-dim:rgba(245,158,11,0.4);">
        <div class="kpi-icon">⏳</div>
        <div class="kpi-num">{pending}</div>
        <div class="kpi-lbl">Awaiting Action</div>
    </div>
    <div class="kpi" style="--kpi-glow:#10b981; --kpi-glow-dim:rgba(16,185,129,0.4);">
        <div class="kpi-icon">✅</div>
        <div class="kpi-num">{resolved}</div>
        <div class="kpi-lbl">Restored Roads</div>
    </div>
    <div class="kpi" style="--kpi-glow:#ef4444; --kpi-glow-dim:rgba(239,68,68,0.4);">
        <div class="kpi-icon">🚧</div>
        <div class="kpi-num">{high_sev}</div>
        <div class="kpi-lbl">High Risk Areas</div>
    </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# Feature Overview
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="sec-heading">Platform Features</div>', unsafe_allow_html=True)

st.markdown("""
<div class="feat-grid">
    <div class="feat-card" style="--feat-accent:#ec4899; --feat-bg:rgba(236,72,153,0.15);">
        <div class="feat-icon-wrap" style="color: #ec4899;">📱</div>
        <div class="feat-title">Citizen Submissions</div>
        <div class="feat-desc">Rapidly submit geospatial photos of damaged areas for crowdsourced risk monitoring.</div>
    </div>
    <div class="feat-card" style="--feat-accent:#8b5cf6; --feat-bg:rgba(139,92,246,0.15);">
        <div class="feat-icon-wrap" style="color: #8b5cf6;">🧠</div>
        <div class="feat-title">AI Assessment Engine</div>
        <div class="feat-desc">Deep neural network auto-flags high-severity craters, estimating immediate risk factors.</div>
    </div>
    <div class="feat-card" style="--feat-accent:#3b82f6; --feat-bg:rgba(59,130,246,0.15);">
        <div class="feat-icon-wrap" style="color: #3b82f6;">🌍</div>
        <div class="feat-title">Dynamic Geolocation</div>
        <div class="feat-desc">Real-time 3D plotting of trouble zones to visualize city-wide structural integrity.</div>
    </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# How it works
# ══════════════════════════════════════════════════════════════════════════════
left_col, right_col = st.columns([3, 2], gap="large")

with left_col:
    st.markdown('<div class="sec-heading" style="margin-top:0;">Operation Workflow</div>', unsafe_allow_html=True)
    st.markdown('<div class="flow-container">', unsafe_allow_html=True)

    steps = [
        ("Capture & Connect", "Citizen photographs damage and uploads location data."),
        ("Neural Inference", "Backend algorithms calculate edge density and CNN scores."),
        ("Authority Dispatch", "Verified severe hazards trigger priority alerts on City HUDs."),
        ("Resolution Tracking", "Repair lifecycle flows from 'Pending' through to 'Resolved'.")
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
    st.markdown('</div>', unsafe_allow_html=True)

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
<div style='background: linear-gradient(135deg, rgba(99,102,241,0.2) 0%, rgba(236,72,153,0.1) 100%);
            border: 1px solid rgba(255,255,255,0.1); border-radius: 24px;
            padding: 40px; text-align: center; margin: 40px 0;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);'>
    <h2 style='color:#fff; font-size:1.8rem; font-weight:800; margin-bottom:12px; letter-spacing:-0.02em;'>
        Shape the Infrastructure Graph
    </h2>
    <p style='color:#cbd5e1; margin-bottom:24px; font-size:1.05rem;'>
        Navigate to the <strong style='color:#a855f7;'>Report Damage</strong> portal to submit visual evidence.
    </p>
</div>
""", unsafe_allow_html=True)

# Latest 5 complaints preview
if all_complaints:
    st.markdown('<div class="sec-heading">Recent Node Updates</div>', unsafe_allow_html=True)
    for c in all_complaints[:5]:
        from config.settings import SEVERITY_HEX
        sev_col  = SEVERITY_HEX.get(c.get("severity_level", "Unknown"), "#64748b")
        stat_map = {"Pending": "#ef4444", "In Progress": "#f59e0b", "Resolved": "#10b981"}
        sta_col  = stat_map.get(c.get("status", ""), "#64748b")
        st.markdown(f"""
        <div style='background:rgba(30,41,59,0.5); border:1px solid rgba(255,255,255,0.05); border-radius:16px;
                    padding:16px 20px; margin-bottom:12px; display:flex;
                    justify-content:space-between; align-items:center; backdrop-filter:blur(8px);
                    transition:transform 0.2s;'>
            <div>
                <span style='color:#8b5cf6; font-size:0.85rem; font-weight:800; letter-spacing:0.05em;'>
                    {c["id"]:04d}
                </span>
                <span style='color:#f8fafc; font-weight:600; font-size:1.05rem; margin-left:14px;'>
                    {c["location_name"]}
                </span>
                <span style='color:#64748b; font-size:0.85rem; margin-left:14px;'>
                    {str(c["date"])[:10]}
                </span>
            </div>
            <div style='display:flex; gap:10px;'>
                <span style='background:{sev_col}15; color:{sev_col};
                             border:1px solid {sev_col}80; padding:4px 14px;
                             border-radius:8px; font-size:0.8rem; font-weight:700;'>
                    {c["severity_level"]}
                </span>
                <span style='background:{sta_col}15; color:{sta_col};
                             border:1px solid {sta_col}80; padding:4px 14px;
                             border-radius:8px; font-size:0.8rem; font-weight:600;'>
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
