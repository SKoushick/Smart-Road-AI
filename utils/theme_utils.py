import streamlit as st

def inject_global_css():
    """Injects core typography, resets, and vibrant glassmorphic utilities."""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&display=swap');
    
    /* Global Reset & Typography */
    *, *::before, *::after { box-sizing: border-box; }
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #050811 !important;
        background-image: 
            radial-gradient(circle at 20% 20%, rgba(56, 189, 248, 0.08), transparent 40%),
            radial-gradient(circle at 80% 80%, rgba(139, 92, 246, 0.08), transparent 40%),
            radial-gradient(circle at 50% 50%, rgba(236, 72, 153, 0.05), transparent 60%) !important;
        font-family: 'Outfit', sans-serif !important;
        color: #f8fafc !important;
    }

    /* Animated Background Grid Overlay */
    [data-testid="stAppViewContainer"]::before {
        content: "";
        position: fixed;
        top: 0; left: 0; width: 100%; height: 100%;
        background-image: 
            linear-gradient(rgba(56, 189, 248, 0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(56, 189, 248, 0.03) 1px, transparent 1px);
        background-size: 40px 40px;
        pointer-events: none;
        z-index: 0;
        animation: panBg 20s linear infinite;
    }

    @keyframes panBg {
        0% { background-position: 0 0; }
        100% { background-position: 40px 40px; }
    }

    /* Elevate Block Container above the background canvas */
    [data-testid="stAppViewBlockContainer"] {
        position: relative;
        z-index: 1;
        background: transparent !important;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(10, 15, 30, 0.95) 0%, rgba(3, 7, 18, 0.98) 100%) !important;
        backdrop-filter: blur(25px) !important;
        -webkit-backdrop-filter: blur(25px) !important;
        border-right: 1px solid rgba(56, 189, 248, 0.2) !important;
        box-shadow: inset -5px 0 30px rgba(56, 189, 248, 0.05), 10px 0 40px rgba(0, 0, 0, 0.6) !important;
    }
    
    /* Optional tech pattern overlay for the sidebar */
    [data-testid="stSidebar"]::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        background: 
            linear-gradient(90deg, rgba(56,189,248,0.03) 1px, transparent 1px) 0 0 / 20px 20px,
            linear-gradient(rgba(56,189,248,0.03) 1px, transparent 1px) 0 0 / 20px 20px;
        pointer-events: none;
        z-index: 0;
    }

    [data-testid="stSidebar"] > div:first-child {
        z-index: 1;
    }
    
    /* Sidebar Navigation Links */
    [data-testid="stSidebarNav"] {
        padding-top: 2.5rem !important;
    }
    [data-testid="stSidebarNav"] > ul {
        padding-top: 1.5rem !important;
    }
    [data-testid="stSidebarNav"] span {
        font-family: 'Outfit', sans-serif !important;
        font-weight: 600 !important;
        font-size: 1.05rem !important;
        color: #64748b !important;
        letter-spacing: 0.05em !important;
        text-transform: uppercase !important;
        padding-left: 0.5rem !important;
        transition: all 0.3s ease !important;
    }
    
    /* Hover effect for all links */
    [data-testid="stSidebarNav"] a:hover {
        background-color: rgba(56, 189, 248, 0.08) !important;
        border-radius: 8px !important;
        margin: 0 10px !important;
        border-left: 2px solid rgba(56, 189, 248, 0.4) !important;
    }
    [data-testid="stSidebarNav"] a:hover span {
        color: #38bdf8 !important;
        transform: translateX(6px) !important;
    }
    
    /* Active Link styling */
    [data-testid="stSidebarNav"] a[aria-current="page"] {
        background: linear-gradient(90deg, rgba(56, 189, 248, 0.15) 0%, transparent 100%) !important;
        border-left: 4px solid #38bdf8 !important;
        border-radius: 0 8px 8px 0 !important;
        margin-left: 0 !important;
        box-shadow: inset 20px 0 30px -15px rgba(56, 189, 248, 0.2);
    }
    [data-testid="stSidebarNav"] a[aria-current="page"] span {
        color: #f8fafc !important;
        text-shadow: 0 0 15px rgba(56, 189, 248, 0.8) !important;
        font-weight: 800 !important;
    }
    
    /* Adding a tiny pulsing indicator next to active page */
    [data-testid="stSidebarNav"] a[aria-current="page"]::after {
        content: '';
        position: absolute;
        right: 20px;
        top: 50%;
        transform: translateY(-50%);
        width: 8px;
        height: 8px;
        background-color: #38bdf8;
        border-radius: 50%;
        box-shadow: 0 0 10px #38bdf8, 0 0 20px #38bdf8;
        animation: pulse 1.5s infinite alternate;
    }
    @keyframes pulse {
        0% { opacity: 0.4; transform: translateY(-50%) scale(0.8); }
        100% { opacity: 1; transform: translateY(-50%) scale(1.2); }
    }
    
    /* Headings */
    h1, h2, h3, h4, h5, h6 { 
        font-family: 'Outfit', sans-serif !important; 
        color: #ffffff !important; 
        letter-spacing: -0.02em !important;
    }
    
    /* Remove headers/footers */
    [data-testid="stDecoration"], header { display: none !important; }
    footer { visibility: hidden; }
    
    /* Glassmorphism Classes */
    .glass-card {
        background: rgba(30, 41, 59, 0.4);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 24px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
    }
    
    /* Buttons */
    div[data-testid="stButton"] > button {
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        padding: 0.5rem 1.5rem !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 14px 0 rgba(99, 102, 241, 0.39) !important;
    }
    div[data-testid="stButton"] > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.6) !important;
    }
    
    /* Inputs */
    div[data-testid="stTextInput"] input,
    div[data-testid="stTextArea"] textarea,
    div[data-testid="stSelectbox"] select {
        background: rgba(15, 23, 42, 0.6) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: #f1f5f9 !important;
        border-radius: 12px !important;
        padding: 0.75rem 1rem !important;
        font-family: 'Outfit', sans-serif !important;
        transition: border-color 0.3s ease !important;
    }
    div[data-testid="stTextInput"] input:focus,
    div[data-testid="stTextArea"] textarea:focus {
        border-color: #8b5cf6 !important;
        box-shadow: 0 0 0 1px #8b5cf6 !important;
    }
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar { width: 8px; height: 8px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: rgba(255, 255, 255, 0.1); border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: rgba(255, 255, 255, 0.2); }
    </style>
    """, unsafe_allow_html=True)
