
"""
Authentication utilities for the Government Panel.
"""

import hashlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config.settings import GOVT_USERNAME, GOVT_PASSWORD, GOVT_PASSKEY

import streamlit as st


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def check_credentials(username: str, password: str) -> bool:
    return username == GOVT_USERNAME and password == GOVT_PASSWORD


def check_passkey(passkey: str) -> bool:
    return passkey.strip() == GOVT_PASSKEY


def login_form() -> bool:
    """
    Render a login form and return True if the user is authenticated.
    Uses st.session_state['govt_authenticated'] as the auth flag.
    """
    if st.session_state.get("govt_authenticated"):
        return True

    st.markdown("""
    <div style='text-align:center; padding: 40px 0 20px 0;'>
        <h2 style='color:#F97316;'>🔐 Government Authority Login</h2>
        <p style='color:#94a3b8;'>Enter your credentials to access the monitoring panel.</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("govt_login_form", clear_on_submit=False):
            st.markdown("### Login")
            username = st.text_input("Username", placeholder="admin")
            password = st.text_input("Password", type="password", placeholder="••••••••")
            passkey  = st.text_input("System Passkey", type="password", placeholder="SMARTROAD****")
            submitted = st.form_submit_button("🔓 Authenticate", use_container_width=True)

        if submitted:
            if check_credentials(username, password) and check_passkey(passkey):
                st.session_state["govt_authenticated"] = True
                st.session_state["govt_user"] = username
                st.success("✅ Authentication successful! Redirecting…")
                st.rerun()
            else:
                st.error("❌ Invalid credentials or passkey. Please try again.")

    return False


def logout() -> None:
    st.session_state["govt_authenticated"] = False
    st.session_state.pop("govt_user", None)
    st.rerun()
