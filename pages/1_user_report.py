
import os
import sys
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from services.complaint_service import submit_complaint
from config.settings import SEVERITY_HEX, SEVERITY_COLOURS

st.set_page_config(
    page_title="Report Pothole | Smart Road Monitor",
    page_icon="🚧",
    layout="wide",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
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

h1, h2, h3 { color: #f1f5f9 !important; }

.hero-banner {
    background: linear-gradient(135deg, #1e3a5f 0%, #0f2447 50%, #1a0a2e 100%);
    border: 1px solid #334155;
    border-radius: 20px;
    padding: 40px 50px;
    margin-bottom: 30px;
    position: relative;
    overflow: hidden;
}
.hero-banner::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -10%;
    width: 400px;
    height: 400px;
    background: radial-gradient(circle, rgba(249,115,22,0.15) 0%, transparent 70%);
    border-radius: 50%;
}
.hero-title {
    font-size: 2.4rem;
    font-weight: 800;
    background: linear-gradient(90deg, #f97316, #fbbf24);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 8px;
}
.hero-sub {
    color: #94a3b8;
    font-size: 1.05rem;
}
.step-badge {
    display: inline-block;
    background: linear-gradient(135deg, #f97316, #ea580c);
    color: white;
    border-radius: 50%;
    width: 32px;
    height: 32px;
    line-height: 32px;
    text-align: center;
    font-weight: 700;
    font-size: 0.9rem;
    margin-right: 10px;
}
.section-card {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 16px;
    padding: 28px 30px;
    margin-bottom: 20px;
}
.ai-result-box {
    background: linear-gradient(135deg, #1a2744, #1e3a5f);
    border-radius: 16px;
    padding: 28px;
    margin-top: 24px;
    border: 1px solid #3b4e6b;
    animation: fadeInUp 0.5s ease;
}
@keyframes fadeInUp {
    from { opacity:0; transform: translateY(20px); }
    to   { opacity:1; transform: translateY(0); }
}
.severity-pill {
    display: inline-block;
    padding: 6px 20px;
    border-radius: 50px;
    font-weight: 700;
    font-size: 1rem;
    margin-top: 8px;
}
.metric-mini {
    background: #0f172a;
    border-radius: 12px;
    padding: 16px;
    text-align: center;
}
.metric-mini .val { font-size: 1.8rem; font-weight: 800; }
.metric-mini .lbl { font-size: 0.8rem; color: #64748b; }

div[data-testid="stButton"] > button {
    background: linear-gradient(135deg, #f97316, #ea580c) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    padding: 12px 28px !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 20px rgba(249,115,22,0.35) !important;
}
div[data-testid="stButton"] > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 30px rgba(249,115,22,0.55) !important;
}
div[data-testid="stTextInput"] input,
div[data-testid="stTextArea"] textarea,
div[data-testid="stSelectbox"] select {
    background: #0f172a !important;
    border: 1px solid #334155 !important;
    color: #e2e8f0 !important;
    border-radius: 10px !important;
}
.success-msg {
    background: linear-gradient(135deg, #052e16, #14532d);
    border: 1px solid #22c55e;
    border-radius: 14px;
    padding: 24px;
    margin-top: 20px;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)


# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-banner">
    <div class="hero-title">🚧 Report Road Damage</div>
    <div class="hero-sub">
        Help us build better roads. Upload an image, describe the issue,
        and our AI will assess the severity instantly.
    </div>
</div>
""", unsafe_allow_html=True)

# ── Form ──────────────────────────────────────────────────────────────────────
with st.form("complaint_form", clear_on_submit=False):
    # Section 1 — Personal details
    st.markdown("""<div class="section-card">
        <span class="step-badge">1</span>
        <strong style='font-size:1.1rem;'>Your Details</strong></div>""",
        unsafe_allow_html=True,
    )
    c1, c2, c3 = st.columns(3)
    with c1:
        name  = st.text_input("Full Name *", placeholder="Aarav Kumar")
    with c2:
        email = st.text_input("Email", placeholder="aarav@example.com")
    with c3:
        phone = st.text_input("Phone", placeholder="+91 98765 43210")

    st.markdown("<br>", unsafe_allow_html=True)

    # Section 2 — Location
    st.markdown("""<div class="section-card">
        <span class="step-badge">2</span>
        <strong style='font-size:1.1rem;'>Location Details</strong></div>""",
        unsafe_allow_html=True,
    )
    location = st.text_input(
        "Road / Area Name *",
        placeholder="e.g. Marina Beach Chennai, Gandhipuram Coimbatore"
    )
    description = st.text_area(
        "Describe the damage *",
        placeholder="Large pothole near the traffic signal. Very dangerous for two-wheelers…",
        height=110,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # Section 3 — Image
    st.markdown("""<div class="section-card">
        <span class="step-badge">3</span>
        <strong style='font-size:1.1rem;'>Upload Pothole Image</strong></div>""",
        unsafe_allow_html=True,
    )
    uploaded = st.file_uploader(
        "Upload clear image (JPG / PNG / WEBP)",
        type=["jpg", "jpeg", "png", "webp"],
        help="A clear, well-lit image helps the AI assess severity more accurately.",
    )
    if uploaded:
        st.image(uploaded, caption="Preview", use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    submitted = st.form_submit_button("🚀 Submit Complaint & Analyse", use_container_width=True)


# ── Submission logic ──────────────────────────────────────────────────────────
if submitted:
    # Validation
    errors = []
    if not name.strip():
        errors.append("Full Name is required.")
    if not location.strip():
        errors.append("Location is required.")
    if not description.strip():
        errors.append("Description is required.")
    if not uploaded:
        errors.append("Please upload an image of the damage.")

    if errors:
        for err in errors:
            st.error(f"⚠️ {err}")
    else:
        with st.spinner("🔍 Analysing image with AI… this may take a moment"):
            image_bytes    = uploaded.read()
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
        <div class="success-msg">
            <h2 style='color:#22c55e; margin:0 0 6px 0;'>
                ✅ Complaint #{result['id']} Submitted!
            </h2>
            <p style='color:#86efac; margin:0;'>
                Your report has been received and will be reviewed by authorities shortly.
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # AI Results
        st.markdown(f"""
        <div class="ai-result-box">
            <h3 style='color:#f97316; margin-top:0;'>🤖 AI Analysis Result</h3>
            <div style='display:flex; gap:20px; flex-wrap:wrap; margin-top:12px;'>
                <div class='metric-mini' style='flex:1; min-width:140px;'>
                    <div class='val' style='color:{"#22c55e" if detected else "#ef4444"};'>
                        {"✅ YES" if detected else "❌ NO"}
                    </div>
                    <div class='lbl'>Pothole Detected</div>
                </div>
                <div class='metric-mini' style='flex:1; min-width:140px;'>
                    <div class='val' style='color:{colour};'>{sev_score:.2f}</div>
                    <div class='lbl'>Severity Score (0–1)</div>
                </div>
                <div class='metric-mini' style='flex:1; min-width:140px;'>
                    <span class='severity-pill' style='background:{colour}22; color:{colour}; border:2px solid {colour};'>
                        {sev_level}
                    </span>
                    <div class='lbl' style='margin-top:6px;'>Severity Level</div>
                </div>
                <div class='metric-mini' style='flex:1; min-width:140px;'>
                    <div class='val' style='color:#60a5fa; font-size:1rem;'>{ai.get("method","–")}</div>
                    <div class='lbl'>Detection Method</div>
                </div>
            </div>
            <div style='margin-top:16px; color:#94a3b8; font-size:0.85rem;'>
                📍 Coordinates: {result.get("latitude", "N/A")}°N, {result.get("longitude", "N/A")}°E
            </div>
        </div>
        """, unsafe_allow_html=True)
