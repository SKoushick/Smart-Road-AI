"""
Complaint service — orchestrates the full complaint-submission pipeline.
"""

import os
import sys
from datetime import datetime
from typing import Any, Dict, Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from services.image_processing_service import save_uploaded_file, preprocess_image
from services.ai_detection_service      import analyse_image
from services.geocoding_service         import geocode_location
from utils.db                           import save_complaint
from utils.cloudinary_utils             import upload_image_to_cloudinary


def submit_complaint(
    name: str,
    email: str,
    phone: str,
    location_name: str,
    description: str,
    image_bytes: Optional[bytes],
    image_filename: str,
    user_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    New pipeline:
      1. Save & pre-process image locally for AI (temporary)
      2. Run AI detection on local file
      3. Geocode location
      4. Upload original bytes to Cloudinary
      5. Persist to Supabase DB
      6. Return result summary
    """

    local_path = None
    cloudinary_url = None
    ai_result  = {
        "pothole_detected": False,
        "severity_score":   0.0,
        "severity_level":   "Unknown",
        "method":           "No image",
    }

    if image_bytes:
        # Save locally for AI analysis
        local_path = save_uploaded_file(image_bytes, image_filename)
        preprocess_image(local_path)
        
        # 1. AI Detection
        ai_result = analyse_image(local_path)
        
        # 2. Cloudinary Upload (Upload the AI-annotated modified image, NOT the raw bytes)
        try:
            with open(local_path, "rb") as f:
                annotated_bytes = f.read()
            cloudinary_url = upload_image_to_cloudinary(annotated_bytes)
        except Exception as e:
            print(f"Cloudinary upload failed: {e}")
            cloudinary_url = ""

    # 3. Geocoding
    lat, lon = geocode_location(location_name)

    # 4. Build record for Supabase
    record: Dict[str, Any] = {
        "name":             name,
        "email":            email,
        "phone":            phone,
        "location_name":    location_name,
        "latitude":         lat,
        "longitude":        lon,
        "description":      description,
        "image_url":        cloudinary_url or "",
        "severity_level":   ai_result["severity_level"],
        "severity_score":   ai_result["severity_score"],
        "pothole_detected": 1 if ai_result["pothole_detected"] else 0,
        "status":           "Pending",
    }
    
    if user_id is not None:
        record["user_id"] = user_id

    # 5. Persist to Supabase
    try:
        response_data = save_complaint(record)
        # Supabase `.insert().execute()` returns a list of inserted row dicts containing DB-assigned defaults (like id)
        returned_record = response_data[0] if isinstance(response_data, list) and len(response_data) > 0 else record
    except Exception as e:
        print(f"Failed to save complaint to Supabase: {e}")
        # Fallback to returning what we have if Supabase isn't configured yet
        returned_record = record.copy()
        returned_record["id"] = 1 # Dummy ID

    # Map created_at dynamically back to date so UI charts won't crash
    returned_record["date"] = returned_record.get("created_at", datetime.now().isoformat(sep=" ", timespec="seconds"))
    returned_record["ai_result"] = ai_result
    
    # 6. Strict serverless requirement: Purge temporary local image file
    if local_path and os.path.exists(local_path):
        try:
            os.remove(local_path)
        except Exception:
            pass

    return returned_record
