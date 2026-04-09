
import os
import sys
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from services.complaint_service import submit_complaint
from config.settings import SEVERITY_HEX, SEVERITY_COLOURS
from utils.theme_utils import inject_global_css

st.set_page_config(
    page_title="Report Pothole | Smart Road Monitor",
    page_icon="🚧",
    layout="wide",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
inject_global_css()

st.markdown("""
<style>
/* ─── Page 1 Specific Styles: Sci-Fi Scanner HUD ────────────────────────── */

/* ── Hero ── */
.report-hero {
    background: linear-gradient(90deg, rgba(15,23,42,0.8) 0%, rgba(30,41,59,0.4) 100%);
    border-left: 4px solid #ec4899;
    padding: 30px 40px;
    border-radius: 0 16px 16px 0;
    margin-bottom: 40px;
    box-shadow: 0 10px 25px rgba(0,0,0,0.2);
}
.report-title {
    font-size: 2.2rem;
    font-weight: 800;
    letter-spacing: 0.05em;
    color: #fff;
    margin-bottom: 8px;
}
.report-sub {
    color: #94a3b8;
    font-size: 1.1rem;
}

/* ── Form Section Cards ── */
.form-section {
    background: rgba(15,23,42,0.5);
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 20px;
    padding: 30px;
    margin-bottom: 24px;
    backdrop-filter: blur(10px);
    transition: all 0.3s;
}
.form-section:hover {
    border-color: rgba(236,72,153,0.3);
    box-shadow: inset 0 0 20px rgba(236,72,153,0.05);
}
.step-indicator {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 28px; height: 28px;
    border-radius: 8px;
    background: rgba(236,72,153,0.2);
    color: #ec4899;
    font-weight: 800;
    margin-right: 12px;
    border: 1px solid rgba(236,72,153,0.5);
}
.step-title {
    font-size: 1.2rem;
    font-weight: 700;
    color: #e2e8f0;
}

/* ── AI Results HUD ── */
.ai-hud {
    position: relative;
    background: rgba(15,23,42,0.8);
    border: 1px solid #38bdf8;
    border-radius: 24px;
    padding: 35px;
    margin-top: 30px;
    overflow: hidden;
    animation: slideUp 0.6s cubic-bezier(0.2, 0.8, 0.2, 1);
    box-shadow: 0 0 30px rgba(56,189,248,0.15), inset 0 0 20px rgba(56,189,248,0.1);
}
.ai-hud::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background: 
        linear-gradient(90deg, rgba(56,189,248,0.03) 1px, transparent 1px) 0 0 / 20px 20px,
        linear-gradient(rgba(56,189,248,0.03) 1px, transparent 1px) 0 0 / 20px 20px;
    pointer-events: none;
}
.ai-hud::after {
    content: '';
    position: absolute;
    top: -50%; left: -50%; width: 200%; height: 2px;
    background: #38bdf8;
    opacity: 0.5;
    box-shadow: 0 0 15px #38bdf8;
    animation: scanner 3s linear infinite;
    pointer-events: none;
}
@keyframes scanner {
    0% { transform: translateY(0); }
    100% { transform: translateY(800px); }
}
@keyframes slideUp {
    from { opacity: 0; transform: translateY(30px); }
    to { opacity: 1; transform: translateY(0); }
}

.hud-header {
    display: flex; align-items: center; gap: 12px;
    margin-bottom: 24px;
    border-bottom: 1px solid rgba(56,189,248,0.2);
    padding-bottom: 16px;
}
.hud-title { font-size: 1.4rem; font-weight: 800; color: #38bdf8; text-transform: uppercase; letter-spacing: 0.1em; }
.hud-blink { width: 10px; height: 10px; border-radius: 50%; background: #38bdf8; animation: blink 1s infinite alternate; box-shadow: 0 0 10px #38bdf8; }
@keyframes blink { 0% { opacity: 0.3; } 100% { opacity: 1; } }

.metric-hud {
    background: rgba(0,0,0,0.4);
    border: 1px solid rgba(255,255,255,0.05);
    border-left: 3px solid var(--hud-colour);
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    position: relative;
}
.metric-hud .val { font-size: 2rem; font-weight: 900; color: #fff; text-shadow: 0 0 15px var(--hud-colour); font-family: monospace; }
.metric-hud .lbl { font-size: 0.8rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.1em; margin-top: 8px; }

.success-banner {
    background: linear-gradient(90deg, rgba(16,185,129,0.2) 0%, transparent 100%);
    border-left: 4px solid #10b981;
    padding: 20px;
    border-radius: 12px;
    margin-top: 24px;
    animation: slideUp 0.5s;
}

div[data-testid="stButton"] > button {
    background: linear-gradient(90deg, #db2777 0%, #be185d 100%) !important;
    box-shadow: 0 0 20px rgba(219, 39, 119, 0.3) !important;
    text-transform: uppercase; letter-spacing: 0.1em;
}
div[data-testid="stButton"] > button:hover {
    box-shadow: 0 0 30px rgba(219, 39, 119, 0.6) !important;
}

</style>
""", unsafe_allow_html=True)


# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="report-hero">
    <div class="report-title">TARGET ACQUISITION: REPORT DAMAGE</div>
    <div class="report-sub">
        Upload visual evidence. Our Neural Network will triangulate and assess severity immediately.
    </div>
</div>
""", unsafe_allow_html=True)

# ── Form ──────────────────────────────────────────────────────────────────────
with st.form("complaint_form", clear_on_submit=False):
    # Section 1 — Personal details
    st.markdown("""<div class="form-section">
        <div><span class="step-indicator">01</span><span class="step-title">Operative ID</span></div><br>""",
        unsafe_allow_html=True,
    )
    c1, c2, c3 = st.columns(3)
    with c1:
        name  = st.text_input("Full Name *", placeholder="Aarav Kumar")
        name_err = st.empty()
    with c2:
        email = st.text_input("Email *", placeholder="aarav@example.com")
        email_err = st.empty()
    with c3:
        phone = st.text_input("Phone *", placeholder="9876543210")
        phone_err = st.empty()
    st.markdown("</div>", unsafe_allow_html=True)

    # Section 2 — Location
    st.markdown("""<div class="form-section">
        <div><span class="step-indicator">02</span><span class="step-title">Spatial Coordinates</span></div><br>""",
        unsafe_allow_html=True,
    )
    location = st.text_input(
        "Road / Area Name *",
        placeholder="e.g. Marina Beach Chennai, Gandhipuram Coimbatore"
    )
    location_err = st.empty()
    description = st.text_area(
        "Describe the anomaly *",
        placeholder="Structural decay observed near the traffic signal…",
        height=110,
    )
    desc_err = st.empty()
    st.markdown("</div>", unsafe_allow_html=True)

    # Section 3 — Image
    st.markdown("""<div class="form-section">
        <div><span class="step-indicator">03</span><span class="step-title">Visual Evidence Feed</span></div><br>""",
        unsafe_allow_html=True,
    )
    uploaded = st.file_uploader(
        "Upload clear image (JPG, JPEG, PNG)",
        type=["jpg", "jpeg", "png"],
        help="A clear, well-lit image helps the AI assess severity more accurately.",
    )
    upload_err = st.empty()
    if uploaded:
        st.image(uploaded, caption="Preview", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    submitted = st.form_submit_button("🚀 INITIATE SCAN & SUBMIT", use_container_width=True)


# ── Submission logic ──────────────────────────────────────────────────────────
import re

if submitted:
    # Validation
    is_valid = True
    
    if not name.strip() or len(name.strip()) < 3 or not re.match(r"^[A-Za-z\s]+$", name.strip()):
        name_err.error("Name must contain only letters and be at least 3 characters long.")
        is_valid = False

    email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    if not email.strip() or not re.match(email_regex, email.strip()):
        email_err.error("Please enter a valid email address.")
        is_valid = False

    if not phone.strip() or not re.match(r"^\d{10}$", phone.strip()):
        phone_err.error("Phone number must contain exactly 10 digits.")
        is_valid = False

    if not location.strip() or len(location.strip()) < 5:
        location_err.error("Location must be at least 5 characters long.")
        is_valid = False

    if not description.strip() or len(description.strip()) < 15:
        desc_err.error("Description must be at least 15 characters.")
        is_valid = False

    if not uploaded:
        upload_err.error("Please upload a valid image (JPG, JPEG, PNG only).")
        is_valid = False
    else:
        file_size = len(uploaded.getvalue())
        if file_size > 5 * 1024 * 1024:
            upload_err.error("Image file size must be less than 5MB.")
            is_valid = False

    if is_valid:
        st.success("Report submitted successfully.")
        with st.spinner("🔍 Analysing image with AI… this may take a moment"):
            image_bytes    = uploaded.getvalue()
            image_filename = uploaded.name

            result = submit_complaint(
                name=name,
                email=email,
                phone=phone,
                location_name=location,
                description=description,
                image_bytes=image_bytes,
                image_filename=image_filename,
            )

        ai = result.get("ai_result", {})
        sev_level = result.get("severity_level", "Unknown")
        sev_score = result.get("severity_score", 0.0)
        detected  = result.get("pothole_detected", 0)
        colour    = SEVERITY_HEX.get(sev_level, "#64748b")

        # Success card
        st.markdown(f"""
<div class="success-banner">
<h3 style='color:#10b981; margin:0 0 4px 0; font-size:1.3rem; font-weight:800;'>[ UPLOAD COMPLETE ] EVENT ID: #{result['id']:06d}</h3>
<p style='color:#a7f3d0; margin:0; font-size:0.95rem;'>Data packet transferred to Authority Server mapping layer.</p>
</div>
""", unsafe_allow_html=True)

        # AI Results
        st.markdown(f"""
<div class="ai-hud" id="hud-anchor">
<div class="hud-header">
<div class="hud-blink"></div>
<div class="hud-title">Deep Scanner Active</div>
<div style="margin-left:auto; color:#38bdf8; opacity:0.6; font-family:monospace;">SYS// {ai.get("method","–").upper()}</div>
</div>
<div style='display:grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap:20px;'>
<div class='metric-hud' style='--hud-colour:{"#10b981" if detected else "#ef4444"};'>
<div class='val' style='color:{"#10b981" if detected else "#ef4444"};'>{"DETECTED" if detected else "CLEAR"}</div>
<div class='lbl'>Anomaly Status</div>
</div>
<div class='metric-hud' style='--hud-colour:{colour};'>
<div class='val' style='color:{colour};'>{sev_score:.2f}</div>
<div class='lbl'>Severity Score</div>
</div>
<div class='metric-hud' style='--hud-colour:{colour};'>
<div class='val' style='color:{colour}; font-size:1.6rem;'>{sev_level.upper()}</div>
<div class='lbl'>Danger Class</div>
</div>
</div>
<div style='margin-top:24px; border-top:1px dashed rgba(56,189,248,0.3); padding-top:16px; color:#7dd3fc; font-family:monospace; font-size:0.85rem;'>
> EXTRACTED SPATIAL DATA: {result.get("latitude", "N/A")}° N, {result.get("longitude", "N/A")}° E<br>
> RESOLUTION ESTIMATE: REQUIRED<br>
> END TRANSMISSION.
</div>
</div>
<script>
// Smooth scroll to HUD
setTimeout(() => {{
    const el = document.getElementById("hud-anchor");
    if (el) el.scrollIntoView({{behavior: 'smooth', block: 'center'}});
}}, 100);
</script>
""", unsafe_allow_html=True)
