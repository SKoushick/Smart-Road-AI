import os
import uuid
import streamlit as st
import cloudinary
import cloudinary.uploader

def init_cloudinary():
    """Initialises the Cloudinary configuration securely."""
    try:
        cloud_name = st.secrets["CLOUDINARY_CLOUD_NAME"]
        api_key = st.secrets["CLOUDINARY_API_KEY"]
        api_secret = st.secrets["CLOUDINARY_API_SECRET"]
    except Exception:
        cloud_name = os.environ.get("CLOUDINARY_CLOUD_NAME")
        api_key = os.environ.get("CLOUDINARY_API_KEY")
        api_secret = os.environ.get("CLOUDINARY_API_SECRET")

    if cloud_name and api_key and api_secret:
        cloudinary.config(
            cloud_name=cloud_name,
            api_key=api_key,
            api_secret=api_secret,
            secure=True
        )
    else:
        raise ValueError("Cloudinary credentials not found in secrets or env.")

def upload_image_to_cloudinary(file_bytes: bytes) -> str:
    """
    Uploads a raw byte array image directly to Cloudinary and returns the secure URL.
    Ensures images are stored strictly in the 'smart-road-monitoring' folder.
    """
    if not cloudinary.config().cloud_name:
        init_cloudinary()
        
    unique_filename = f"complaint_{uuid.uuid4().hex[:10]}"
    
    response = cloudinary.uploader.upload(
        file_bytes,
        folder="smart-road-monitoring",
        public_id=unique_filename
    )
    return response.get("secure_url")
