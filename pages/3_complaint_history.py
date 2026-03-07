
import os
import sys
import streamlit as st
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from database.complaint_repository import fetch_all_complaints
from config.settings import SEVERITY_HEX, STATUS_OPTIONS

st.set_page_config(
    page_title="Complaint History | Smart Road Monitor",
    page_icon="📋",
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
}
.hist-card {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 14px;
    padding: 18px 20px;
    margin-bottom: 12px;
    transition: all 0.2s;
}
.hist-card:hover { border-color: #60a5fa; }

.sev-pip {
    width: 12px; height: 12px;
    border-radius: 50%;
    display: inline-block;
    margin-right: 6px;
}
.filter-bar {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 14px;
    padding: 20px 22px;
    margin-bottom: 20px;
}
div[data-testid="stDownloadButton"] > button {
    background: linear-gradient(135deg, #1d4ed8, #1e40af) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
}
div[data-testid="stTextInput"] input,
div[data-testid="stSelectbox"] select {
    background: #0f172a !important;
    border: 1px solid #334155 !important;
    color: #e2e8f0 !important;
    border-radius: 10px !important;
}
</style>
""", unsafe_allow_html=True)


# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-header">
    <h1 style='margin:0; font-size:1.9rem;'>📋 Complaint History</h1>
    <p style='color:#94a3b8; margin:4px 0 0 0;'>
        Browse all submitted complaints with filtering and export options.
    </p>
</div>
""", unsafe_allow_html=True)


# ── Load data ─────────────────────────────────────────────────────────────────
all_complaints = fetch_all_complaints()

if not all_complaints:
    st.info("🔍 No complaints found yet. Citizens can submit reports via the **Report Page**.")
    st.stop()

df = pd.DataFrame(all_complaints)


# ── Filter bar ────────────────────────────────────────────────────────────────
st.markdown('<div class="filter-bar">', unsafe_allow_html=True)
fc1, fc2, fc3, fc4 = st.columns([3, 2, 2, 1])
with fc1:
    search = st.text_input("🔍 Search location or name", placeholder="e.g. Marina Beach")
with fc2:
    sev_f  = st.selectbox("Severity", ["All", "High", "Medium", "Low", "Unknown"])
with fc3:
    stat_f = st.selectbox("Status", ["All"] + STATUS_OPTIONS)
with fc4:
    st.markdown("<br>", unsafe_allow_html=True)
    show_table = st.checkbox("Table view", value=False)
st.markdown("</div>", unsafe_allow_html=True)

# Apply filters
filtered_df = df.copy()
if search:
    mask = (
        filtered_df["location_name"].str.contains(search, case=False, na=False) |
        filtered_df["name"].str.contains(search, case=False, na=False)
    )
    filtered_df = filtered_df[mask]
if sev_f != "All":
    filtered_df = filtered_df[filtered_df["severity_level"] == sev_f]
if stat_f != "All":
    filtered_df = filtered_df[filtered_df["status"] == stat_f]


# ── Export ────────────────────────────────────────────────────────────────────
st.markdown(f"**{len(filtered_df)} result(s) found**")
col_exp, _ = st.columns([1, 4])
with col_exp:
    csv_bytes = filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Export CSV",
        data=csv_bytes,
        file_name="smart_road_complaints.csv",
        mime="text/csv",
        use_container_width=True,
    )

st.markdown("<br>", unsafe_allow_html=True)


# ── Display ───────────────────────────────────────────────────────────────────
if show_table:
    display_cols = [
        "id", "name", "location_name", "severity_level",
        "severity_score", "status", "date",
    ]
    st.dataframe(
        filtered_df[display_cols].rename(columns={
            "id": "ID",
            "name": "Reporter",
            "location_name": "Location",
            "severity_level": "Severity",
            "severity_score": "Score",
            "status": "Status",
            "date": "Date",
        }),
        use_container_width=True,
        hide_index=True,
    )
else:
    for _, row in filtered_df.iterrows():
        sev_col = SEVERITY_HEX.get(row["severity_level"], "#64748b")
        stat_colours = {
            "Pending": "#ef4444",
            "In Progress": "#f97316",
            "Resolved": "#22c55e",
        }
        stat_col = stat_colours.get(row["status"], "#64748b")

        with st.container():
            st.markdown(f"""
            <div class="hist-card">
                <div style='display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;'>
                    <div>
                        <span style='color:#60a5fa; font-size:0.82rem; font-weight:700;'>
                            #SMRT-{int(row["id"]):04d}
                        </span>
                        <span style='color:#e2e8f0; font-weight:600; font-size:1rem; margin-left:10px;'>
                            📍 {row["location_name"]}
                        </span>
                    </div>
                    <div style='display:flex; gap:10px; align-items:center;'>
                        <span style='background:{sev_col}22; color:{sev_col};
                                     border:1px solid {sev_col}; padding:3px 14px;
                                     border-radius:50px; font-size:0.8rem; font-weight:700;'>
                            {row["severity_level"]}
                        </span>
                        <span style='background:{stat_col}22; color:{stat_col};
                                     border:1px solid {stat_col}; padding:3px 14px;
                                     border-radius:50px; font-size:0.8rem; font-weight:600;'>
                            {row["status"]}
                        </span>
                    </div>
                </div>
                <div style='margin-top:10px; color:#94a3b8; font-size:0.85rem; display:flex; gap:20px; flex-wrap:wrap;'>
                    <span>👤 {row["name"]}</span>
                    <span>📅 {str(row["date"])[:10]}</span>
                    <span>📊 Score: {row["severity_score"]:.2f}</span>
                    <span>🔍 Pothole: {"✅" if row["pothole_detected"] else "❌"}</span>
                </div>
                {f'<div style="margin-top:8px; color:#64748b; font-size:0.83rem; font-style:italic;">"{str(row["description"])[:100]}…"</div>' if row.get("description") else ""}
            </div>
            """, unsafe_allow_html=True)

            # Image preview
            img_path = row.get("image_path") or row.get("image_url") or ""
            if img_path:
                with st.expander(f"🖼️ View Image — #SMRT-{int(row['id']):04d}"):
                    if os.path.exists(str(img_path)):
                        try:
                            st.image(str(img_path), use_container_width=True)
                        except Exception:
                            st.caption("Could not load image.")
                    elif str(img_path).startswith("http"):
                        st.image(str(img_path), use_container_width=True)
