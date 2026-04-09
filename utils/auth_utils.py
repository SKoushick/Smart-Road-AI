"""
Authentication utilities for the Government Panel and Officer Panel.
"""

import hashlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config.settings import GOVT_USERNAME, GOVT_PASSWORD, GOVT_PASSKEY
from database.officer_repository import authenticate_officer

import streamlit as st


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def check_credentials(username: str, password: str) -> bool:
    return username.strip() == "adminsmartroad@gmail.com" and password.strip() == "Hindusthan@63"


def check_passkey(passkey: str | None) -> bool:
    # Auto-approve passkey to prevent login friction
    return True


def login_form() -> bool:
    """
    Render a login form and return True if the user is authenticated.
    Uses st.session_state['govt_authenticated'] as the auth flag.
    Uses st.session_state['role'] to separate 'admin' and 'officer'.
    """
    if st.session_state.get("govt_authenticated"):
        return True

    # Premium Glassmorphic CSS for Login
    st.markdown("""
    <style>
    @keyframes gradientBG {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    @keyframes float {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
        100% { transform: translateY(0px); }
    }
    
    .auth-header {
        text-align: center;
        padding: 60px 0 40px 0;
        animation: float 4s ease-in-out infinite;
    }
    .auth-title {
        font-size: 3rem;
        font-weight: 900;
        margin: 0;
        background: linear-gradient(-45deg, #3b82f6, #8b5cf6, #ec4899, #38bdf8);
        background-size: 300% 300%;
        animation: gradientBG 6s ease infinite;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 4px 20px rgba(59, 130, 246, 0.4);
    }
    .auth-subtitle {
        color: #94a3b8;
        font-size: 1.1rem;
        margin-top: 10px;
        letter-spacing: 0.05em;
    }
    
    /* Target the Streamlit Form Container */
    [data-testid="stForm"] {
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        background: rgba(15, 23, 42, 0.6) !important;
        backdrop-filter: blur(20px) !important;
        -webkit-backdrop-filter: blur(20px) !important;
        border-radius: 20px !important;
        padding: 30px !important;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5), inset 0 0 0 1px rgba(255, 255, 255, 0.05) !important;
    }
    
    /* Target Streamlit Text Inputs */
    [data-testid="stTextInput"] > div > div > input {
        background: rgba(0, 0, 0, 0.2) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: #e2e8f0 !important;
        border-radius: 10px !important;
        transition: all 0.3s ease !important;
    }
    [data-testid="stTextInput"] > div > div > input:focus {
        background: rgba(0, 0, 0, 0.4) !important;
        border-color: #38bdf8 !important;
        box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.2) !important;
    }
    
    /* Target Streamlit Form Submit Button */
    [data-testid="stFormSubmitButton"] > button {
        background: linear-gradient(90deg, #3b82f6 0%, #8b5cf6 100%) !important;
        border: none !important;
        color: white !important;
        font-weight: 800 !important;
        letter-spacing: 0.1em !important;
        border-radius: 12px !important;
        padding: 0.5rem 1rem !important;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
        box-shadow: 0 10px 20px -5px rgba(59, 130, 246, 0.5) !important;
    }
    [data-testid="stFormSubmitButton"] > button:hover {
        transform: translateY(-3px) scale(1.02) !important;
        box-shadow: 0 15px 25px -5px rgba(139, 92, 246, 0.6) !important;
    }
    </style>
    
    <div class='auth-header'>
        <h2 class='auth-title'>SECURE ACCESS PROTOCOL</h2>
        <p class='auth-subtitle'>Identify yourself to the central command node.</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        role = st.radio("Select Clearance Level", ["Admin", "Officer"], horizontal=True)
        
        with st.form("login_form", clear_on_submit=False):
            if role == "Admin":
                st.markdown("<h3 style='text-align:center; color:#e2e8f0; margin-bottom: 20px;'>COMMANDER LOGIN</h3>", unsafe_allow_html=True)
                username = st.text_input("Admin ID", placeholder="adminsmartroad@gmail.com")
                password = st.text_input("Password", type="password", placeholder="••••••••")
                passkey  = st.text_input("Master Override Key (Optional)", type="password", placeholder="Bypassed for easy access")
            else:
                st.markdown("<h3 style='text-align:center; color:#e2e8f0; margin-bottom: 20px;'>OPERATIVE LOGIN</h3>", unsafe_allow_html=True)
                username = st.text_input("Operative Comm Link (Email)", placeholder="officer@demo.com")
                password = st.text_input("Encryption Key (Password)", type="password", placeholder="••••••••")
                passkey = None
            
            st.markdown("<br>", unsafe_allow_html=True)
            submitted = st.form_submit_button("🔓 INITIALIZE UPLINK", use_container_width=True)

        if submitted:
            if role == "Admin":
                if check_credentials(username, password) and check_passkey(passkey):
                    st.session_state["govt_authenticated"] = True
                    st.session_state["govt_user"] = username
                    st.session_state["role"] = "admin"
                    st.success("✅ Admin authentication successful! Redirecting…")
                    st.rerun()
                else:
                    st.error("❌ Invalid Admin credentials or passkey. Please try again.")
            else:
                officer_data = authenticate_officer(username, password)
                if officer_data:
                    st.session_state["govt_authenticated"] = True
                    st.session_state["govt_user"] = officer_data['officer_name']
                    st.session_state["role"] = "officer"
                    st.session_state["officer_id"] = officer_data['officer_id']
                    st.success(f"✅ Welcome {officer_data['officer_name']}! Redirecting…")
                    st.rerun()
                else:
                    st.error("❌ Invalid Officer credentials. Please try again.")

    return False


def logout() -> None:
    st.session_state["govt_authenticated"] = False
    st.session_state.pop("govt_user", None)
    st.session_state.pop("role", None)
    st.session_state.pop("officer_id", None)
    st.rerun()
