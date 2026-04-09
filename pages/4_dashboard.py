
import os
import sys
import streamlit as st
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from database.complaint_repository import (
    fetch_all_complaints,
    fetch_severity_counts,
    fetch_status_counts,
    fetch_monthly_counts,
    fetch_location_counts,
)
from utils.dashboard_utils import (
    monthly_trend_chart,
    severity_pie_chart,
    location_bar_chart,
    status_bar_chart,
    resolution_gauge,
)
from utils.map_utils import build_heatmap
from config.settings import SEVERITY_HEX
from utils.theme_utils import inject_global_css

st.set_page_config(
    page_title="Analytics Dashboard | Smart Road Monitor",
    page_icon="📊",
    layout="wide",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
inject_global_css()

st.markdown("""
<style>
/* ── Analytics Dashboard Specific ── */
.dash-header {
    background: linear-gradient(90deg, #1e293b 0%, #0f172a 100%);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-bottom: 3px solid #6366f1;
    border-radius: 16px;
    padding: 30px 40px;
    margin-bottom: 28px;
    position: relative;
    overflow: hidden;
    backdrop-filter: blur(10px);
    box-shadow: 0 10px 30px rgba(0,0,0,0.3);
}
.dash-header::before {
    content: '';
    position: absolute;
    top: -50%; right: -50%; width: 200%; height: 200%;
    background: radial-gradient(circle at center, rgba(99, 102, 241, 0.15) 0%, transparent 50%);
    pointer-events: none;
    animation: rotate 20s linear infinite;
}
@keyframes rotate { 100% { transform: rotate(360deg); } }

.dash-header::after {
    content: '📊';
    position: absolute;
    right: 40px; top: 10px;
    font-size: 6rem;
    opacity: 0.08;
}

.kpi-card {
    background: rgba(15, 23, 42, 0.7);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 16px;
    padding: 24px 20px;
    text-align: center;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
    backdrop-filter: blur(8px);
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 4px;
    background: var(--accent, #60a5fa);
    box-shadow: 0 0 10px var(--accent, #60a5fa);
    border-radius: 16px 16px 0 0;
}
.kpi-card:hover { 
    transform: translateY(-8px); 
    box-shadow: 0 12px 30px rgba(0,0,0,0.4);
    border-color: rgba(255,255,255,0.1);
}
.kpi-card:hover::after {
    content: '';
    position: absolute; left: 0; right: 0; top: 0; bottom: 0;
    background: radial-gradient(circle, var(--accent) 0%, transparent 60%);
    opacity: 0.1;
    pointer-events: none;
}
.kpi-num { 
    font-size: 2.8rem; 
    font-weight: 900; 
    line-height: 1;
    text-shadow: 0 0 20px rgba(255,255,255,0.1);
}
.kpi-lbl { 
    font-size: 0.82rem; 
    color: #94a3b8; 
    margin-top: 8px; 
    text-transform: uppercase; 
    letter-spacing: 0.08em; 
    font-weight: 700;
}

.chart-card {
    background: rgba(30, 41, 59, 0.4);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 16px;
    padding: 24px 22px;
    margin-bottom: 24px;
    backdrop-filter: blur(10px);
    box-shadow: 0 4px 20px rgba(0,0,0,0.15);
    transition: all 0.3s;
}
.chart-card:hover {
    border-color: rgba(255,255,255,0.1);
    box-shadow: 0 8px 30px rgba(0,0,0,0.25);
}

.insight-pill {
    display: inline-block;
    background: rgba(15, 23, 42, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 50px;
    padding: 8px 18px;
    font-size: 0.85rem;
    color: #cbd5e1;
    margin: 4px;
    backdrop-filter: blur(4px);
    transition: transform 0.2s;
}
.insight-pill:hover { transform: scale(1.05); border-color: rgba(255,255,255,0.2); }
.insight-pill span { font-weight: 800; }
</style>
""", unsafe_allow_html=True)


# ── Data ──────────────────────────────────────────────────────────────────────
all_complaints  = fetch_all_complaints()
severity_counts = fetch_severity_counts()
status_counts   = fetch_status_counts()
monthly_data    = fetch_monthly_counts()
location_data   = fetch_location_counts()

total    = len(all_complaints)
resolved = status_counts.get("Resolved", 0)
pending  = status_counts.get("Pending",  0)
in_prog  = status_counts.get("In Progress", 0)
high_sev = severity_counts.get("High",   0)
med_sev  = severity_counts.get("Medium", 0)
res_rate = round(resolved / total * 100, 1) if total > 0 else 0.0
avg_score = (
    sum(c["severity_score"] for c in all_complaints) / total
    if total else 0.0
)


# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="dash-header">
    <h1 style='margin:0; font-size:2.2rem; color:#fff; font-weight:800; letter-spacing:0.02em;'>Infrastructure Analytics Hub</h1>
    <p style='color:#a5b4fc; margin:8px 0 0 0; font-size:1.1rem;'>
        Real-time telemetry and pattern recognition for the Smart Road network.
    </p>
</div>
""", unsafe_allow_html=True)


# ── Quick Insights ────────────────────────────────────────────────────────────
if total > 0:
    top_loc = location_data[0]["location_name"] if location_data else "N/A"
    st.markdown(f"""
    <div style='margin-bottom:20px;'>
        <span class='insight-pill'>🏆 Most Affected: <span style='color:#f97316;'>{top_loc}</span></span>
        <span class='insight-pill'>⚡ High Severity: <span style='color:#ef4444;'>{high_sev}</span> complaints</span>
        <span class='insight-pill'>✅ Resolution Rate: <span style='color:#22c55e;'>{res_rate}%</span></span>
        <span class='insight-pill'>📈 Avg Score: <span style='color:#60a5fa;'>{avg_score:.2f}</span></span>
    </div>
    """, unsafe_allow_html=True)


# ── KPI Row ───────────────────────────────────────────────────────────────────
k1, k2, k3, k4, k5, k6 = st.columns(6)
kpi_data = [
    (k1, total,    "#60a5fa", "Total Complaints",  ""),
    (k2, pending,  "#ef4444", "Pending",           "🔴"),
    (k3, in_prog,  "#f97316", "In Progress",       "🟠"),
    (k4, resolved, "#22c55e", "Resolved",          "✅"),
    (k5, high_sev, "#dc2626", "High Severity",     "🚨"),
    (k6, f"{res_rate}%", "#a78bfa", "Resolution Rate", ""),
]
for col, val, clr, lbl, icon in kpi_data:
    with col:
        st.markdown(f"""
        <div class="kpi-card" style="--accent:{clr};">
            <div class="kpi-num" style="color:{clr};">{val}</div>
            <div class="kpi-lbl">{icon} {lbl}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# ── No-data guard ─────────────────────────────────────────────────────────────
if total == 0:
    st.markdown("""
    <div style='text-align:center; padding:80px 0; color:#475569;'>
        <div style='font-size:4rem;'>📭</div>
        <h3 style='color:#64748b;'>No Complaint Data Yet</h3>
        <p>Submit complaints via the <strong>Report Page</strong> to start seeing analytics.</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()


# ── Row 1 — Monthly Trend + Severity Pie ─────────────────────────────────────
c_left, c_right = st.columns([3, 2])

with c_left:
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    fig_trend = monthly_trend_chart(monthly_data)
    if fig_trend:
        st.plotly_chart(fig_trend, use_container_width=True, config={"displayModeBar": False})
    else:
        st.info("Not enough data for trend chart.")
    st.markdown("</div>", unsafe_allow_html=True)

with c_right:
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    fig_pie = severity_pie_chart(severity_counts)
    if fig_pie:
        st.plotly_chart(fig_pie, use_container_width=True, config={"displayModeBar": False})
    else:
        st.info("Not enough severity data.")
    st.markdown("</div>", unsafe_allow_html=True)


# ── Row 2 — Location Bar + Resolution Gauge + Status Bar ─────────────────────
r2_left, r2_mid = st.columns([3, 2])

with r2_left:
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    fig_loc = location_bar_chart(location_data)
    if fig_loc:
        st.plotly_chart(fig_loc, use_container_width=True, config={"displayModeBar": False})
    else:
        st.info("No location data.")
    st.markdown("</div>", unsafe_allow_html=True)

with r2_mid:
    # Resolution gauge
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    fig_gauge = resolution_gauge(resolved, total)
    if fig_gauge:
        st.plotly_chart(fig_gauge, use_container_width=True, config={"displayModeBar": False})
    else:
        st.info("No data.")
    st.markdown("</div>", unsafe_allow_html=True)

    # Status bar
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    fig_status = status_bar_chart(status_counts)
    if fig_status:
        st.plotly_chart(fig_status, use_container_width=True, config={"displayModeBar": False})
    else:
        st.info("No status data.")
    st.markdown("</div>", unsafe_allow_html=True)


# ── Row 3 — Heatmap ───────────────────────────────────────────────────────────
st.markdown("### 🌡️ Road Damage Density Heatmap")
st.markdown('<div class="chart-card">', unsafe_allow_html=True)
heatmap_deck = build_heatmap(all_complaints)
if heatmap_deck:
    st.pydeck_chart(heatmap_deck, use_container_width=True)
else:
    st.info("📍 Heatmap requires PyDeck and geo-located complaints.")
st.markdown("</div>", unsafe_allow_html=True)


# ── Row 4 — Data Table ────────────────────────────────────────────────────────
with st.expander("📄 Raw Data Table", expanded=False):
    df = pd.DataFrame(all_complaints)
    if not df.empty:
        display_cols = [
            "id", "name", "location_name", "severity_level",
            "severity_score", "status", "date",
        ]
        existing = [c for c in display_cols if c in df.columns]
        st.dataframe(
            df[existing].rename(columns={  # type: ignore
                "id": "ID", "name": "Reporter",
                "location_name": "Location",
                "severity_level": "Severity",
                "severity_score": "Score",
                "status": "Status", "date": "Date",
            }),
            use_container_width=True,
            hide_index=True,
        )
        csv = df.to_csv(index=False).encode("utf-8")  # type: ignore
        st.download_button(
            "⬇️ Download Full Dataset",
            data=csv,
            file_name="smart_road_analytics.csv",
            mime="text/csv",
        )


# ── Footer note ───────────────────────────────────────────────────────────────
st.markdown("""
<hr style='border-color:#1e293b; margin-top:30px;'>
<p style='text-align:center; color:#334155; font-size:0.8rem;'>
    Smart Road Infrastructure Monitoring System • Analytics refresh on page reload
</p>
""", unsafe_allow_html=True)
