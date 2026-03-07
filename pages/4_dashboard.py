
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

st.set_page_config(
    page_title="Analytics Dashboard | Smart Road Monitor",
    page_icon="📊",
    layout="wide",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
*, *::before, *::after { box-sizing: border-box; }
html, body, [data-testid="stAppViewContainer"] {
    background: #0a0f1e !important;
    font-family: 'Inter', sans-serif !important;
    color: #e2e8f0 !important;
}
[data-testid="stSidebar"] { background: #0d1528 !important; }
h1,h2,h3 { color: #f1f5f9 !important; }

.page-header {
    background: linear-gradient(135deg, #0f2447 0%, #1a0a2e 100%);
    border: 1px solid #334155;
    border-radius: 20px;
    padding: 32px 40px;
    margin-bottom: 28px;
    position: relative;
    overflow: hidden;
}
.page-header::after {
    content: '📊';
    position: absolute;
    right: 40px; top: 20px;
    font-size: 5rem;
    opacity: 0.12;
}

.kpi-card {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 16px;
    padding: 22px 18px;
    text-align: center;
    transition: transform 0.25s, border-color 0.25s;
    position: relative;
    overflow: hidden;
}
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: var(--accent, #60a5fa);
    border-radius: 16px 16px 0 0;
}
.kpi-card:hover { transform: translateY(-5px); border-color: #475569; }
.kpi-num { font-size: 2.5rem; font-weight: 800; line-height: 1.1; }
.kpi-lbl { font-size: 0.78rem; color: #64748b; margin-top: 6px; text-transform: uppercase; letter-spacing: 0.05em; }
.kpi-delta { font-size: 0.82rem; margin-top: 6px; }

.chart-card {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 16px;
    padding: 22px 20px;
    margin-bottom: 20px;
}
.section-divider {
    border: none;
    border-top: 1px solid #1e293b;
    margin: 24px 0;
}
.insight-pill {
    display: inline-block;
    background: #0f172a;
    border: 1px solid #334155;
    border-radius: 50px;
    padding: 6px 16px;
    font-size: 0.83rem;
    color: #94a3b8;
    margin: 4px;
}
.insight-pill span { font-weight: 700; }
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
<div class="page-header">
    <h1 style='margin:0; font-size:2rem;'>Infrastructure Analytics Dashboard</h1>
    <p style='color:#94a3b8; margin:6px 0 0 0; font-size:1rem;'>
        Real-time insights into road damage trends, severity distribution,
        and repair performance across India.
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
            df[existing].rename(columns={
                "id": "ID", "name": "Reporter",
                "location_name": "Location",
                "severity_level": "Severity",
                "severity_score": "Score",
                "status": "Status", "date": "Date",
            }),
            use_container_width=True,
            hide_index=True,
        )
        csv = df.to_csv(index=False).encode("utf-8")
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
