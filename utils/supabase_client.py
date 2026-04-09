import os
import streamlit as st
from supabase import create_client, Client

def get_supabase_client() -> Client:
    """Initialize and return the Supabase client safely reading from Streamlit Secrets or ENV variables."""
    # Try fetching from Streamlit secrets first, then environment variables
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
    except Exception:
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
    
    if not url or not key:
        raise ValueError("Supabase credentials not found in secrets or env.")
    
    return create_client(url, key)

# Global singleton client
supabase: Client = get_supabase_client()

import uuid

def int_to_uuid(officer_id) -> str:
    """Safely cast a local integer ID into a strict Postgres UUID."""
    if not officer_id:
        return None
    try:
        return str(uuid.UUID(int=int(officer_id)))
    except (ValueError, TypeError):
        return str(officer_id)

def uuid_to_int(officer_uuid: str):
    """Reverts a deterministically generated UUID back to an integer."""
    if not officer_uuid:
        return None
    try:
        return uuid.UUID(officer_uuid).int
    except (ValueError, TypeError):
        return officer_uuid
