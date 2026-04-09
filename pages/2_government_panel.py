import os
import sys
import streamlit as st
import base64
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.auth_utils import login_form, logout
from database.complaint_repository import (
    fetch_all_complaints, update_complaint_status, fetch_complaints_by_status,
    update_complaint_assignment, fetch_complaints_by_officer, update_complaint_repair_status
)
from database.officer_repository import (
    fetch_all_officers, insert_officer, delete_officer, update_officer
)
from utils.map_utils import build_complaint_map
from config.settings import STATUS_OPTIONS, SEVERITY_HEX
from utils.theme_utils import inject_global_css
from utils.email_utils import send_assignment_email

st.set_page_config(
    page_title="Government & Officer Panel | Smart Road Monitor",
    page_icon="🏛️",
    layout="wide",
)

# ── CSS (Unified & Highly Interactive) ────────────────────────────────────────
inject_global_css()

st.markdown("""
<style>
/* ── Glassmorphism & Animations ── */
@keyframes fadeInSlideUp {
    0% { opacity: 0; transform: translateY(20px); }
    100% { opacity: 1; transform: translateY(0); }
}

@keyframes pulseGlow {
    0% { box-shadow: 0 0 10px rgba(56, 189, 248, 0.4); }
    50% { box-shadow: 0 0 25px rgba(56, 189, 248, 0.8), 0 0 40px rgba(56, 189, 248, 0.4); }
    100% { box-shadow: 0 0 10px rgba(56, 189, 248, 0.4); }
}

@keyframes pulseRedGlow {
    0% { box-shadow: 0 0 10px rgba(239, 68, 68, 0.4); }
    50% { box-shadow: 0 0 25px rgba(239, 68, 68, 0.8), 0 0 40px rgba(239, 68, 68, 0.4); }
    100% { box-shadow: 0 0 10px rgba(239, 68, 68, 0.4); }
}

.cmd-header {
    background: linear-gradient(135deg, rgba(30, 27, 75, 0.8) 0%, rgba(49, 46, 129, 0.8) 100%);
    backdrop-filter: blur(15px);
    border: 1px solid rgba(79, 70, 229, 0.5);
    border-radius: 20px;
    padding: 30px 40px;
    margin-bottom: 30px;
    display: flex;
    align-items: center;
    gap: 24px;
    box-shadow: 0 10px 30px rgba(49, 46, 129, 0.4);
    position: relative;
    overflow: hidden;
    animation: fadeInSlideUp 0.6s ease-out;
}
.cmd-icon {
    font-size: 3.5rem;
    filter: drop-shadow(0 0 15px rgba(99, 102, 241, 0.8));
    animation: pulseGlow 3s infinite;
    border-radius: 50%;
}
.cmd-title {
    font-size: 2.2rem;
    font-weight: 900;
    color: #fff;
    margin: 0;
    letter-spacing: 0.05em;
    text-shadow: 0 2px 10px rgba(0,0,0,0.5);
    background: -webkit-linear-gradient(45deg, #fff, #a5b4fc);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.cmd-sub {
    color: #c7d2fe;
    margin: 0;
    font-size: 1.1rem;
    font-weight: 500;
}

.stat-card {
    background: rgba(15, 23, 42, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-bottom: 4px solid var(--st-color);
    border-radius: 16px;
    padding: 24px 20px;
    text-align: center;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    backdrop-filter: blur(12px);
    position: relative;
    overflow: hidden;
    animation: fadeInSlideUp 0.8s ease-out backwards;
}
.stat-card:hover {
    transform: translateY(-8px) scale(1.02);
    box-shadow: 0 15px 30px rgba(0,0,0,0.4);
    border-color: var(--st-color);
    background: rgba(30, 41, 59, 0.8);
}
.stat-card::after {
    content: '';
    position: absolute;
    top: -50%; left: -50%; width: 200%; height: 200%;
    background: radial-gradient(circle, var(--st-color) 0%, transparent 70%);
    opacity: 0;
    pointer-events: none;
    transition: opacity 0.3s;
}
.stat-card:hover::after {
    opacity: 0.15;
}
.stat-num {
    font-size: 3rem;
    font-weight: 900;
    color: #fff;
    line-height: 1;
    margin-bottom: 8px;
    text-shadow: 0 0 20px var(--st-color);
}
.stat-lbl {
    font-size: 0.85rem;
    color: #cbd5e1;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    font-weight: 700;
}

.complaint-card {
    background: rgba(30, 41, 59, 0.5);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-left: 4px solid var(--sev-color);
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 20px;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    backdrop-filter: blur(12px);
    animation: fadeInSlideUp 0.5s ease-out backwards;
}
.complaint-card:hover {
    background: rgba(40, 53, 75, 0.8);
    box-shadow: 0 12px 30px rgba(0,0,0,0.3);
    transform: translateX(5px);
    border-left-width: 8px;
}

.high-sev-animate {
    animation: pulseRedGlow 2s infinite;
}

.sev-badge {
    display: inline-block;
    padding: 6px 14px;
    border-radius: 8px;
    font-size: 0.75rem;
    font-weight: 900;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    box-shadow: 0 0 10px rgba(0,0,0,0.2);
}
.status-badge {
    display: inline-block;
    padding: 6px 14px;
    border-radius: 8px;
    font-size: 0.75rem;
    font-weight: 800;
    background: rgba(15, 23, 42, 0.8);
    border: 1px solid rgba(255,255,255,0.2);
    color: #e2e8f0;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* Enhancing Streamlit Buttons */
div[data-testid="stButton"] > button {
    background: linear-gradient(90deg, #3b82f6 0%, #2563eb 100%) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    box-shadow: 0 4px 15px rgba(37, 99, 235, 0.4) !important;
    text-transform: uppercase; 
    letter-spacing: 0.1em;
    font-weight: 700 !important;
    transition: all 0.3s ease !important;
    border-radius: 8px !important;
}
div[data-testid="stButton"] > button:hover {
    box-shadow: 0 8px 25px rgba(37, 99, 235, 0.6) !important;
    transform: translateY(-2px) !important;
    background: linear-gradient(90deg, #60a5fa 0%, #3b82f6 100%) !important;
}

/* Logout button override */
.logout-btn div[data-testid="stButton"] > button {
    background: rgba(239, 68, 68, 0.15) !important;
    border: 1px solid rgba(239, 68, 68, 0.4) !important;
    color: #fca5a5 !important;
    box-shadow: 0 4px 15px rgba(239, 68, 68, 0.2) !important;
}
.logout-btn div[data-testid="stButton"] > button:hover {
    background: rgba(239, 68, 68, 0.3) !important;
    border-color: #f87171 !important;
    color: #fff !important;
    box-shadow: 0 6px 20px rgba(239, 68, 68, 0.4) !important;
}

/* Action button overrides inside cards */
.action-btn div[data-testid="stButton"] > button {
    background: linear-gradient(90deg, #10b981 0%, #059669 100%) !important;
    box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3) !important;
}
.action-btn div[data-testid="stButton"] > button:hover {
    box-shadow: 0 8px 25px rgba(16, 185, 129, 0.5) !important;
}

/* Custom Grid Items */
.grid-item {
    background: rgba(0,0,0,0.25); 
    padding: 12px; 
    border-radius: 8px;
    border: 1px solid rgba(255,255,255,0.05);
    transition: background 0.2s;
}
.grid-item:hover {
    background: rgba(0,0,0,0.4);
    border-color: rgba(255,255,255,0.1);
}
</style>
""", unsafe_allow_html=True)


# ── Auth gate ─────────────────────────────────────────────────────────────────
if not login_form():
    st.stop()

# Get the authenticated user's role
role = st.session_state.get('role')

# ── Header (Dynamically Rendered based on Role) ───────────────────────────────
col_head, col_user = st.columns([5, 1])
with col_head:
    if role == 'admin':
        st.markdown("""
        <div class="cmd-header">
            <div class="cmd-icon">🏛️</div>
            <div>
                <h1 class="cmd-title">CENTRAL COMMAND PANEL</h1>
                <p class="cmd-sub">Real-time infrastructure monitoring operations</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    elif role == 'officer':
        officer_name = st.session_state.get("govt_user", "Field Operative")
        st.markdown(f"""
        <div class="cmd-header" style="background: linear-gradient(135deg, rgba(15, 23, 42, 0.8) 0%, rgba(30, 41, 59, 0.8) 100%); border-color: #38bdf8;">
            <div class="cmd-icon" style="filter: drop-shadow(0 0 15px rgba(56, 189, 248, 0.8));">🛡️</div>
            <div>
                <h1 class="cmd-title" style="background: -webkit-linear-gradient(45deg, #fff, #7dd3fc); -webkit-background-clip: text;">OFFICER DASHBOARD</h1>
                <p class="cmd-sub" style="color: #bae6fd;">Welcome back, <strong>{officer_name}</strong>. View your active assignments below.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

with col_user:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="logout-btn">', unsafe_allow_html=True)
    if st.button("🔌 DISCONNECT", use_container_width=True):
        logout()
    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# ── ADMIN VIEW ────────────────────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════
if role == "admin":
    # ── Stats ─────────────────────────────────────────────────────────────────
    all_complaints = fetch_all_complaints()
    total    = len(all_complaints)
    pending  = sum(1 for c in all_complaints if c["status"] == "Pending")
    progress = sum(1 for c in all_complaints if c["status"] == "In Progress")
    resolved = sum(1 for c in all_complaints if c["status"] == "Resolved")
    high     = sum(1 for c in all_complaints if c["severity_level"] == "High")

    s1, s2, s3, s4, s5 = st.columns(5)
    metrics = [
        (s1, total,    "#3b82f6", "Total Tickets"),
        (s2, pending,  "#ef4444", "Pending"),
        (s3, progress, "#f59e0b", "In Progress"),
        (s4, resolved, "#10b981", "Resolved"),
        (s5, high,     "#ec4899", "Critical Level"),
    ]
    for i, (col, val, clr, lbl) in enumerate(metrics):
        with col:
            st.markdown(f"""
<div class="stat-card" style="--st-color: {clr}; animation-delay: {i * 0.1}s;">
    <div class="stat-num">{val}</div>
    <div class="stat-lbl">{lbl}</div>
</div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Map ───────────────────────────────────────────────────────────────────
    with st.expander("🗺️ Live Geographic Overview", expanded=True):
        deck = build_complaint_map(all_complaints)
        if deck:
            st.pydeck_chart(deck, use_container_width=True)
        else:
            st.info("📍 No geo-located complaints yet, or PyDeck is not installed.")

    # ── Officer Management ────────────────────────────────────────────────────
    st.markdown("### 👮 Officer Command Console")
    with st.expander("Manage Active Field Operatives", expanded=False):
        officers = fetch_all_officers()
        
        o_c1, o_c2 = st.columns([2, 1])
        with o_c1:
            st.markdown("#### Operational Roster")
            if not officers:
                st.info("No officers found.")
            else:
                for off in officers:
                    with st.container():
                        st.markdown(f"""
<div style="background: rgba(0,0,0,0.3); padding: 15px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.05); margin-bottom: 10px;">
<div style="display:flex; justify-content: space-between; align-items: center;">
<div>
<strong style="color: #60a5fa; font-size: 1.1rem;">{off['officer_name']}</strong> <span style="color: #94a3b8; font-family: monospace;">({off['gmail']})</span><br>
<span style="font-size: 0.9rem; color: #cbd5e1;">📍 {off['assigned_region']}, {off['state']}</span>
</div>
<div>
<span class="status-badge" style="background: {'rgba(16,185,129,0.2)' if off['status'] == 'Active' else 'rgba(239,68,68,0.2)'}; color: {'#10b981' if off['status'] == 'Active' else '#ef4444'};">
{off['status']}
</span>
</div>
</div>
</div>
                        """, unsafe_allow_html=True)
                        
                        @st.dialog("Edit Operative Profile")
                        def edit_officer_dialog(curr_off):
                            with st.form(f"edit_off_{curr_off['officer_id']}", clear_on_submit=False):
                                e_c1, e_c2 = st.columns(2)
                                with e_c1:
                                    e_name = st.text_input("Name", value=curr_off['officer_name'])
                                    e_email = st.text_input("Gmail", value=curr_off['gmail'])
                                    e_pass = st.text_input("Password", value=curr_off['password'], type="password")
                                with e_c2:
                                    e_state = st.text_input("State", value=curr_off['state'])
                                    e_region = st.text_input("Region", value=curr_off['assigned_region'])
                                    e_status = st.selectbox("Status", ["Active", "Inactive"], index=0 if curr_off['status'] == 'Active' else 1)
                                if st.form_submit_button("💾 Save Profile Changes", use_container_width=True):
                                    update_officer(curr_off['officer_id'], {
                                        "officer_name": e_name, "gmail": e_email, "password": e_pass,
                                        "state": e_state, "assigned_region": e_region, "status": e_status
                                    })
                                    st.success("Operative profile updated!")
                                    st.rerun()

                        cols = st.columns([3, 1, 1])
                        with cols[1]:
                            if st.button("⚙️ Edit", key=f"edit_btn_{off['officer_id']}", use_container_width=True):
                                edit_officer_dialog(off)
                        with cols[2]:
                            if st.button("🗑️ Revoke", key=f"del_off_{off['officer_id']}", use_container_width=True):
                                delete_officer(off['officer_id'])
                                st.rerun()
                        
                        st.markdown("<hr style='border: 1px solid rgba(255,255,255,0.05); margin-top: 15px;'>", unsafe_allow_html=True)
                        
        with o_c2:
            st.markdown("#### Add Operative")
            with st.form("add_officer_form", clear_on_submit=True):
                o_name = st.text_input("Name")
                o_email = st.text_input("Gmail")
                o_pass = st.text_input("Password", type="password")
                o_state = st.text_input("State", value="Tamil Nadu")
                o_region = st.text_input("Region")
                o_status = st.selectbox("Status", ["Active", "Inactive"])
                
                if st.form_submit_button("➕ Register Operative", use_container_width=True):
                    try:
                        insert_officer({
                            "officer_name": o_name, "gmail": o_email, "password": o_pass,
                            "state": o_state, "assigned_region": o_region, "status": o_status
                        })
                        st.success("Operative registered!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error adding officer: {e}")

    # ── Complaint Management ──────────────────────────────────────────────────
    st.markdown("### 📋 Intelligence Queue")

    f1, f2, f3 = st.columns([2, 2, 1])
    with f1:
        status_filter = st.selectbox("Filter Operational Status", ["All"] + STATUS_OPTIONS, key="status_filter")
    with f2:
        severity_filter = st.selectbox("Filter Threat Severity", ["All", "High", "Medium", "Low", "Unknown"], key="sev_filter")
    with f3:
        sort_by = st.selectbox("Sort Priority", ["Newest First", "Oldest First", "Severity"], key="sort_by")

    filtered = all_complaints
    if status_filter != "All":
        filtered = [c for c in filtered if c["status"] == status_filter]
    if severity_filter != "All":
        filtered = [c for c in filtered if c["severity_level"] == severity_filter]

    if sort_by == "Oldest First":
        filtered.sort(key=lambda x: x["date"])
    elif sort_by == "Severity":
        _order = {"High": 0, "Medium": 1, "Low": 2, "Unknown": 3}
        filtered.sort(key=lambda x: _order.get(x["severity_level"], 9))

    st.markdown(f"**{len(filtered)} signals detected**")
    st.markdown("<br>", unsafe_allow_html=True)

    for i, c in enumerate(filtered):
        sev_col = SEVERITY_HEX.get(c["severity_level"], "#64748b")
        is_high_sev = c["severity_level"] == "High"
        animate_class = "high-sev-animate" if is_high_sev else ""

        with st.container():
            img_html = ""
            img_path = c.get("image_path") or c.get("image_url") or ""
            if img_path:
                if os.path.exists(img_path):
                    try:
                        with open(img_path, "rb") as f:
                            b64 = base64.b64encode(f.read()).decode("utf-8")
                        img_html = f"<div style='margin-bottom:15px; border-radius:12px; overflow:hidden; border:1px solid rgba(255,255,255,0.1);'><img src='data:image/jpeg;base64,{b64}' style='width:100%; max-height:300px; object-fit:cover; display:block;'></div>"
                    except Exception:
                        pass
                elif str(img_path).startswith("http"):
                    img_html = f"<div style='margin-bottom:15px; border-radius:12px; overflow:hidden; border:1px solid rgba(255,255,255,0.1);'><img src='{img_path}' style='width:100%; max-height:300px; object-fit:cover; display:block;'></div>"

            if img_html:
                st.markdown(img_html, unsafe_allow_html=True)
                
            st.markdown(f"""
<div class="complaint-card {animate_class}" style="--sev-color: {sev_col}; animation-delay: {i * 0.05}s;">
<div style='display:flex; justify-content:space-between; align-items:flex-start; margin-bottom: 16px;'>
<div>
<span style='color:#818cf8; font-family:monospace; font-weight:800; font-size:1.1rem; margin-right:12px;'>SYS-{c["id"]:05d}</span>
<span style='color:#f8fafc; font-weight:700; font-size:1.2rem; letter-spacing: 0.02em;'>{c["location_name"]}</span>
</div>
<div style='display:flex; gap:10px;'>
<span class='sev-badge' style='background:{sev_col}20; color:{sev_col}; border:1px solid {sev_col}50;'>{c["severity_level"]} PRIORITY</span>
<span class='status-badge'>{c["status"]}</span>
</div>
</div>

<div style='display:grid; grid-template-columns: repeat(4, 1fr); gap:12px; margin-bottom: 16px; font-size:0.85rem; color:#94a3b8; font-family:monospace;'>
<div class='grid-item'><span style='opacity:0.6'>REPORTER</span><br><span style='color:#cbd5e1; font-weight:600;'>{c["name"]}</span></div>
<div class='grid-item'><span style='opacity:0.6'>TIMESTAMP</span><br><span style='color:#cbd5e1; font-weight:600;'>{c["date"][:10]} {c["date"][11:16]}</span></div>
<div class='grid-item'><span style='opacity:0.6'>SEV. INDEX</span><br><span style='color:{sev_col}; font-weight:800;'>{c["severity_score"]:.2f}</span></div>
<div class='grid-item'><span style='opacity:0.6'>AI TARGET</span><br><span style='color:{"#10b981" if c["pothole_detected"] else "#ef4444"}; font-weight:800;'>{"POSITIVE" if c["pothole_detected"] else "NEGATIVE"}</span></div>
</div>
{f'<div style="color:#e2e8f0; font-size:0.95rem; line-height:1.6; padding: 15px; background: rgba(0,0,0,0.3); border-radius:10px; border-left: 3px solid rgba(255,255,255,0.2);">"{c["description"]}"</div>' if c.get("description") else ""}
</div>
            """, unsafe_allow_html=True)

            with st.expander(f"⚙️ Action Command — #{c['id']}"):
                cols = st.columns([1, 1])
                with cols[0]:
                    if c.get("latitude"):
                        st.markdown(f"<span style='font-family: monospace; color: #60a5fa;'>🌐 Coordinates: {c['latitude']}, {c['longitude']}</span>", unsafe_allow_html=True)
                    
                    st.markdown("##### Dispatch Operative")
                    active_officers = [o for o in fetch_all_officers() if o['status'] == 'Active']
                    officer_options = {o['officer_id']: o['officer_name'] for o in active_officers}
                    officer_names = ["Select Operative"] + list(officer_options.values())
                    
                    current_assignee_id = c.get("assigned_officer_id")
                    current_assignee_name = officer_options.get(current_assignee_id, "Select Operative") if current_assignee_id else "Select Operative"
                    
                    try:
                        def_index = officer_names.index(current_assignee_name)
                    except ValueError:
                        def_index = 0
                        
                    assignee_name = st.selectbox("Unit Selection", officer_names, index=def_index, key=f"assign_{c['id']}")
                    if assignee_name != "Select Operative":
                        selected_officer_id = [k for k, v in officer_options.items() if v == assignee_name][0]
                    else:
                        selected_officer_id = None
                    
                    if st.button("📡 INITIATE DISPATCH", key=f"btn_assign_{c['id']}", use_container_width=True):
                        if selected_officer_id:
                            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            ok = update_complaint_assignment(c["id"], selected_officer_id, now)
                            if ok:
                                # Fetch the actual officer email to send the notification
                                for o in active_officers:
                                    if o['officer_id'] == selected_officer_id:
                                        officer_email = o['gmail']
                                        # Send the assignment email
                                        send_assignment_email(officer_email, c)
                                        break
                                
                                st.success("✅ Target dispatched to Operative! Notification email sent.")
                                        
                                st.rerun()
                        else:
                            st.warning("⚠️ Select an operative to dispatch.")

                with cols[1]:
                    st.markdown("##### Override System Status")
                    new_status  = st.selectbox(
                        "Force Status",
                        STATUS_OPTIONS,
                        index=STATUS_OPTIONS.index(c["status"]) if c["status"] in STATUS_OPTIONS else 0,
                        key=f"status_{c['id']}",
                    )
                    resolved_by = st.text_input(
                        "Confirming Authority",
                        value=c.get("resolved_by") or "",
                        key=f"officer_{c['id']}",
                    )
                    notes = st.text_area(
                        "Command Logs",
                        value=c.get("notes") or "",
                        key=f"notes_{c['id']}",
                        height=68,
                    )
                    
                    st.markdown('<div class="action-btn">', unsafe_allow_html=True)
                    if st.button("💾 ENFORCE OVERRIDE", key=f"upd_{c['id']}", use_container_width=True):
                        ok = update_complaint_status(c["id"], new_status, resolved_by, notes)
                        if ok:
                            st.success("✅ System Status Overridden.")
                            st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# ── OFFICER VIEW ──────────────────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════
elif role == "officer":
    officer_id = st.session_state.get("officer_id")
    if not officer_id:
        st.error("Invalid secure session.")
        st.stop()

    st.markdown("### 📋 Active Mission Objectives")
    assigned_complaints = fetch_complaints_by_officer(officer_id)

    if not assigned_complaints:
        st.info("No active assignments. Standby for dispatch.")
    else:
        for i, c in enumerate(assigned_complaints):
            sev_col = SEVERITY_HEX.get(c["severity_level"], "#64748b")
            
            with st.container():
                st.markdown(f"""
<div class="complaint-card" style="--sev-color: {sev_col}; animation-delay: {i * 0.1}s;">
<div style='display:flex; justify-content:space-between; align-items:flex-start; margin-bottom: 16px;'>
<div>
<span style='color:#38bdf8; font-family:monospace; font-weight:800; font-size:1.1rem; margin-right:12px;'>TARGET-{c["id"]:05d}</span>
<span style='color:#f8fafc; font-weight:700; font-size:1.2rem;'>{c["location_name"]}</span>
</div>
<div style='display:flex; gap:10px;'>
<span class='status-badge' style='background: rgba(56, 189, 248, 0.2); color: #38bdf8; border-color: rgba(56,189,248,0.5);'>
{c["repair_status"]}
</span>
<span class='status-badge'>{c["status"]}</span>
</div>
</div>

<div style='display:grid; grid-template-columns: repeat(3, 1fr); gap:12px; margin-bottom: 16px; font-size:0.85rem; color:#94a3b8;'>
<div class='grid-item'>
<span style='opacity:0.6; font-family:monospace;'>RECEIVED UPLINK</span><br>
<span style='color:#cbd5e1; font-weight:600;'>{c.get("assigned_time", "N/A")}</span>
</div>
<div class='grid-item'>
<span style='opacity:0.6; font-family:monospace;'>THREAT LEVEL</span><br>
<span style='color:{sev_col}; font-weight:800;'>{c["severity_level"]}</span>
</div>
<div class='grid-item'>
<span style='opacity:0.6; font-family:monospace;'>GPS VECTOR</span><br>
<span style='color:#cbd5e1; font-weight:600;'>{c.get("latitude", "N/A")}, {c.get("longitude", "N/A")}</span>
</div>
</div>

<div style="color:#e2e8f0; font-size:0.95rem; line-height:1.6; padding: 15px; background: rgba(0,0,0,0.3); border-radius:10px; border-left: 3px solid #38bdf8;">
<strong style="color: #38bdf8; font-family: monospace;">[COMMAND_INTEL]:</strong> {c.get("description", "No additional context provided.")}
</div>
</div>
                """, unsafe_allow_html=True)
                
                with st.expander("🛠️ Tactical Actions & Evidence Upload"):
                    st.markdown("##### 📸 Post-Repair Validation")
                    upload_col, info_col = st.columns([2, 1])
                    
                    with upload_col:
                        proof_img = st.file_uploader("Upload visual proof of resolution (Required for closure)", type=["jpg", "png", "jpeg"], key=f"uploader_{c['id']}")
                        
                        st.markdown("<br>", unsafe_allow_html=True)
                        cmd1, cmd2 = st.columns(2)
                        
                        with cmd1:
                            if st.button("▶️ ENGAGE PROTOCOL", key=f"start_{c['id']}", use_container_width=True):
                                if c["repair_status"] != "In Progress":
                                    ok = update_complaint_repair_status(c["id"], "In Progress", "In Progress")
                                    if ok:
                                        st.success("✅ Protocol Engaged.")
                                        st.rerun()
                                else:
                                    st.info("Protocol already active.")
                                    
                        with cmd2:
                            st.markdown('<div class="action-btn">', unsafe_allow_html=True)
                            if st.button("✅ MARK RESOLVED", key=f"comp_{c['id']}", use_container_width=True):
                                if proof_img:
                                    os.makedirs("uploads/proofs", exist_ok=True)
                                    proof_path = os.path.join("uploads/proofs", f"proof_{c['id']}.jpg")
                                    with open(proof_path, "wb") as f:
                                        f.write(proof_img.getbuffer())
                                
                                ok = update_complaint_repair_status(c["id"], "Resolved", "Completed")
                                if ok:
                                    st.success("✅ Target Resolved & Closed.")
                                    st.rerun()
                            st.markdown('</div>', unsafe_allow_html=True)
                    
                    with info_col:
                        if c.get("image_path") and os.path.exists(c["image_path"]):
                            st.markdown("<div style='color:#38bdf8; font-family:monospace; margin-bottom:8px;'>[ORIGINAL_TARGET_SCAN]</div>", unsafe_allow_html=True)
                            st.image(c["image_path"], use_container_width=True)
                        elif c.get("image_url"):
                            st.markdown("<div style='color:#38bdf8; font-family:monospace; margin-bottom:8px;'>[ORIGINAL_TARGET_SCAN]</div>", unsafe_allow_html=True)
                            st.image(c["image_url"], use_container_width=True)
