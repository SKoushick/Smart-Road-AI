
import os
import sys
import streamlit as st
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from database.complaint_repository import fetch_all_complaints
from config.settings import SEVERITY_HEX, STATUS_OPTIONS
from utils.theme_utils import inject_global_css

st.set_page_config(
    page_title="Complaint History | Smart Road Monitor",
    page_icon="📋",
    layout="wide",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
inject_global_css()

st.markdown("""
<style>
/* ── Archive Specific ── */
.archive-header {
    background: linear-gradient(135deg, rgba(30, 64, 175, 0.4) 0%, rgba(15, 23, 42, 0.8) 100%);
    border: 1px solid rgba(59, 130, 246, 0.3);
    border-left: 4px solid #3b82f6;
    border-radius: 16px;
    padding: 30px 40px;
    margin-bottom: 30px;
    backdrop-filter: blur(10px);
}
.archive-title {
    font-size: 2.2rem;
    font-weight: 800;
    color: #fff;
    margin: 0 0 8px 0;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}
.archive-sub {
    color: #93c5fd;
    margin: 0;
    font-size: 1.1rem;
}

.filter-bar {
    background: rgba(15, 23, 42, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 16px;
    padding: 24px 28px;
    margin-bottom: 24px;
    backdrop-filter: blur(12px);
    box-shadow: 0 4px 20px rgba(0,0,0,0.2);
}

.hist-card {
    background: rgba(30, 41, 59, 0.5);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-left: 3px solid var(--st-color, #64748b);
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 16px;
    transition: all 0.3s;
    backdrop-filter: blur(8px);
}
.hist-card:hover { 
    background: rgba(30, 41, 59, 0.8);
    box-shadow: 0 8px 25px rgba(0,0,0,0.3);
    transform: translateY(-2px);
}

.badge-tag {
    padding: 4px 12px;
    border-radius: 6px;
    font-size: 0.75rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

div[data-testid="stDownloadButton"] > button {
    background: linear-gradient(90deg, #3b82f6 0%, #2563eb 100%) !important;
    border: none !important;
    box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3) !important;
    text-transform: uppercase; letter-spacing: 0.05em;
}
div[data-testid="stDownloadButton"] > button:hover {
    box-shadow: 0 6px 20px rgba(59, 130, 246, 0.5) !important;
}
</style>
""", unsafe_allow_html=True)


# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="archive-header">
    <h1 class="archive-title">🗄️ Master Data Archive</h1>
    <p class="archive-sub">
        Query and export historical reports.
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
    csv_bytes = filtered_df.to_csv(index=False).encode("utf-8") # type: ignore
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
        filtered_df[display_cols].rename(columns={   # type: ignore
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
    for _, row in filtered_df.iterrows(): # type: ignore
        sev_col = SEVERITY_HEX.get(row["severity_level"], "#64748b")
        stat_colours = {
            "Pending": "#ef4444",
            "In Progress": "#f97316",
            "Resolved": "#22c55e",
        }
        stat_col = stat_colours.get(row["status"], "#64748b")

        with st.container():
            img_html = ""
            img_path = row.get("image_path") or row.get("image_url") or ""
            if img_path:
                import base64
                if os.path.exists(str(img_path)):
                    try:
                        with open(str(img_path), "rb") as f:
                            b64 = base64.b64encode(f.read()).decode("utf-8")
                        img_html = f"<div style='margin-bottom:12px;'><img src='data:image/jpeg;base64,{b64}' style='width:100%; max-height:350px; object-fit:cover; border-radius:8px; border:1px solid rgba(255,255,255,0.1);'></div>"
                    except Exception:
                        pass
                elif str(img_path).startswith("http"):
                    img_html = f"<div style='margin-bottom:12px;'><img src='{img_path}' style='width:100%; max-height:350px; object-fit:cover; border-radius:8px; border:1px solid rgba(255,255,255,0.1);'></div>"

            if img_html:
                st.markdown(img_html, unsafe_allow_html=True)

            st.markdown(f"""
<div class="hist-card" style="--st-color: {stat_col};">
<div style='display:flex; justify-content:space-between; align-items:flex-start; margin-bottom: 12px;'>
<div>
<span style='color:#60a5fa; font-family:monospace; font-size:0.9rem; font-weight:700; margin-right: 8px;'>SYS-{int(row["id"]):05d}</span>
<span style='color:#f8fafc; font-weight:600; font-size:1.1rem;'>{row["location_name"]}</span>
</div>
<div style='display:flex; gap:10px; align-items:center;'>
<span class="badge-tag" style='background:{sev_col}15; color:{sev_col}; border:1px solid {sev_col}50;'>{row["severity_level"]}</span>
<span class="badge-tag" style='background:{stat_col}15; color:{stat_col}; border:1px solid {stat_col}50;'>{row["status"]}</span>
</div>
</div>
<div style='display:grid; grid-template-columns: repeat(4, 1fr); gap:10px; margin-bottom: 12px; font-size:0.85rem; color:#94a3b8; font-family:monospace;'>
<div style='background:rgba(0,0,0,0.2); padding:8px; border-radius:6px;'><span style='opacity:0.6'>OPERATIVE</span><br><span style='color:#cbd5e1'>{row["name"]}</span></div>
<div style='background:rgba(0,0,0,0.2); padding:8px; border-radius:6px;'><span style='opacity:0.6'>TIMESTAMP</span><br><span style='color:#cbd5e1'>{str(row["date"])[:10]}</span></div>
<div style='background:rgba(0,0,0,0.2); padding:8px; border-radius:6px;'><span style='opacity:0.6'>SEV. INDEX</span><br><span style='color:{sev_col}'>{row["severity_score"]:.2f}</span></div>
<div style='background:rgba(0,0,0,0.2); padding:8px; border-radius:6px;'><span style='opacity:0.6'>AI TARGET</span><br><span style='color:{"#10b981" if row["pothole_detected"] else "#ef4444"}'>{"POSITIVE" if row["pothole_detected"] else "NEGATIVE"}</span></div>
</div>
{f'<div style="color:#cbd5e1; font-size:0.9rem; line-height:1.5; padding: 12px; background: rgba(255,255,255,0.03); border-radius:8px; border-left: 2px solid rgba(255,255,255,0.1);">"{str(row["description"])}"</div>' if row.get("description") else ""}
</div>
""", unsafe_allow_html=True)
