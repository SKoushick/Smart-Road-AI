
import os
import sys
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.auth_utils import login_form, logout
from database.complaint_repository import (
    fetch_all_complaints, update_complaint_status, fetch_complaints_by_status,
)
from utils.map_utils import build_complaint_map
from config.settings import STATUS_OPTIONS, SEVERITY_HEX

st.set_page_config(
    page_title="Government Panel | Smart Road Monitor",
    page_icon="🏛️",
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
    display: flex;
    align-items: center;
    gap: 20px;
}
.stat-card {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 16px;
    padding: 24px 20px;
    text-align: center;
    transition: transform 0.2s;
}
.stat-card:hover { transform: translateY(-4px); }
.stat-num { font-size: 2.4rem; font-weight: 800; }
.stat-lbl { font-size: 0.8rem; color: #64748b; margin-top: 4px; }

.complaint-card {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 14px;
    padding: 20px 22px;
    margin-bottom: 14px;
    transition: border-color 0.2s;
}
.complaint-card:hover { border-color: #f97316; }

.sev-badge {
    display: inline-block;
    padding: 3px 14px;
    border-radius: 50px;
    font-size: 0.82rem;
    font-weight: 700;
}
.status-badge {
    display: inline-block;
    padding: 3px 14px;
    border-radius: 50px;
    font-size: 0.82rem;
    font-weight: 600;
    background: #0f172a;
    border: 1px solid #475569;
    color: #94a3b8;
}

div[data-testid="stButton"] > button {
    background: linear-gradient(135deg, #f97316, #ea580c) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    transition: all 0.2s !important;
}
div[data-testid="stSelectbox"] select,
div[data-testid="stTextInput"] input {
    background: #0f172a !important;
    border: 1px solid #334155 !important;
    color: #e2e8f0 !important;
    border-radius: 10px !important;
}
</style>
""", unsafe_allow_html=True)


# ── Auth gate ─────────────────────────────────────────────────────────────────
if not login_form():
    st.stop()


# ── Header ────────────────────────────────────────────────────────────────────
col_head, col_user = st.columns([5, 1])
with col_head:
    st.markdown("""
    <div class="page-header">
        <span style='font-size:3rem;'>🏛️</span>
        <div>
            <h1 style='margin:0; font-size:1.9rem;'>Government Monitoring Panel</h1>
            <p style='color:#94a3b8; margin:0;'>
                Manage, monitor & resolve citizen road damage complaints.
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
with col_user:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔓 Logout", use_container_width=True):
        logout()


# ── Stats ─────────────────────────────────────────────────────────────────────
all_complaints = fetch_all_complaints()
total    = len(all_complaints)
pending  = sum(1 for c in all_complaints if c["status"] == "Pending")
progress = sum(1 for c in all_complaints if c["status"] == "In Progress")
resolved = sum(1 for c in all_complaints if c["status"] == "Resolved")
high     = sum(1 for c in all_complaints if c["severity_level"] == "High")

s1, s2, s3, s4, s5 = st.columns(5)
metrics = [
    (s1, total,    "#60a5fa", "Total Reports"),
    (s2, pending,  "#ef4444", "Pending"),
    (s3, progress, "#f97316", "In Progress"),
    (s4, resolved, "#22c55e", "Resolved"),
    (s5, high,     "#dc2626", "High Severity"),
]
for col, val, clr, lbl in metrics:
    with col:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-num" style="color:{clr};">{val}</div>
            <div class="stat-lbl">{lbl}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# ── Map ───────────────────────────────────────────────────────────────────────
with st.expander("🗺️ Live Complaint Map", expanded=True):
    deck = build_complaint_map(all_complaints)
    if deck:
        st.pydeck_chart(deck, use_container_width=True)
    else:
        st.info("📍 No geo-located complaints yet, or PyDeck is not installed.")


# ── Filter + Table ────────────────────────────────────────────────────────────
st.markdown("### 📋 Complaint Management")

f1, f2, f3 = st.columns([2, 2, 1])
with f1:
    status_filter = st.selectbox(
        "Filter by Status",
        ["All"] + STATUS_OPTIONS,
        key="status_filter",
    )
with f2:
    severity_filter = st.selectbox(
        "Filter by Severity",
        ["All", "High", "Medium", "Low", "Unknown"],
        key="sev_filter",
    )
with f3:
    sort_by = st.selectbox("Sort by", ["Newest First", "Oldest First", "Severity"], key="sort_by")

# Apply filters
filtered = all_complaints
if status_filter != "All":
    filtered = [c for c in filtered if c["status"] == status_filter]
if severity_filter != "All":
    filtered = [c for c in filtered if c["severity_level"] == severity_filter]

# Sort
if sort_by == "Oldest First":
    filtered.sort(key=lambda x: x["date"])
elif sort_by == "Severity":
    _order = {"High": 0, "Medium": 1, "Low": 2, "Unknown": 3}
    filtered.sort(key=lambda x: _order.get(x["severity_level"], 9))
# default: newest first (already from DB)

st.markdown(f"**{len(filtered)} complaint(s) found**")
st.markdown("<br>", unsafe_allow_html=True)

# ── Render complaint cards ────────────────────────────────────────────────────
for c in filtered:
    sev_col = SEVERITY_HEX.get(c["severity_level"], "#64748b")
    with st.container():
        st.markdown(f"""
        <div class="complaint-card">
            <div style='display:flex; justify-content:space-between; align-items:flex-start;'>
                <div>
                    <span style='color:#60a5fa; font-weight:700; font-size:0.85rem;'>
                        #SMRT-{c["id"]:04d}
                    </span> &nbsp;
                    <span style='color:#e2e8f0; font-weight:600; font-size:1.05rem;'>
                        📍 {c["location_name"]}
                    </span>
                </div>
                <div style='text-align:right;'>
                    <span class='sev-badge' style='background:{sev_col}22; color:{sev_col}; border:1px solid {sev_col};'>
                        {c["severity_level"]}
                    </span>
                    &nbsp;
                    <span class='status-badge'>{c["status"]}</span>
                </div>
            </div>
            <div style='margin-top:10px; color:#94a3b8; font-size:0.88rem;'>
                👤 {c["name"]} &nbsp;|&nbsp;
                📅 {c["date"][:10]} &nbsp;|&nbsp;
                📊 Score: {c["severity_score"]:.2f} &nbsp;|&nbsp;
                🔍 Pothole: {"✅" if c["pothole_detected"] else "❌"}
            </div>
            {f'<div style="margin-top:8px; color:#64748b; font-size:0.85rem;">📝 {c["description"][:120]}…</div>' if c.get("description") else ""}
        </div>
        """, unsafe_allow_html=True)

        # Expand for image + update
        with st.expander(f"🔧 Update Status — #{c['id']}"):
            cols = st.columns([2, 1])
            with cols[0]:
                # Show image if available
                img_path = c.get("image_path") or c.get("image_url") or ""
                if img_path and os.path.exists(img_path):
                    try:
                        st.image(img_path, caption="Complaint Image", use_container_width=True)
                    except Exception:
                        st.caption("⚠️ Could not load image.")
                elif img_path.startswith("http"):
                    st.image(img_path, caption="Complaint Image", use_container_width=True)
                else:
                    st.info("📷 No image available.")

                if c.get("latitude"):
                    st.caption(f"🌐 Lat: {c['latitude']}, Lon: {c['longitude']}")

            with cols[1]:
                new_status  = st.selectbox(
                    "New Status",
                    STATUS_OPTIONS,
                    index=STATUS_OPTIONS.index(c["status"]) if c["status"] in STATUS_OPTIONS else 0,
                    key=f"status_{c['id']}",
                )
                resolved_by = st.text_input(
                    "Officer Name",
                    value=c.get("resolved_by") or "",
                    key=f"officer_{c['id']}",
                )
                notes = st.text_area(
                    "Notes",
                    value=c.get("notes") or "",
                    key=f"notes_{c['id']}",
                    height=80,
                )
                if st.button("💾 Save Update", key=f"upd_{c['id']}"):
                    ok = update_complaint_status(c["id"], new_status, resolved_by, notes)
                    if ok:
                        st.success("✅ Status updated!")
                        st.rerun()
                    else:
                        st.error("❌ Update failed.")
