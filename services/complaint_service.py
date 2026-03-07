
"""
Complaint service — orchestrates the full complaint-submission pipeline.
"""

import os
import sys
from datetime import datetime
from typing import Any, Dict, Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from services.image_processing_service import process_and_store_image
from services.ai_detection_service      import analyse_image
from services.geocoding_service         import geocode_location
from database.complaint_repository      import insert_complaint, fetch_all_complaints


def submit_complaint(
    name: str,
    email: str,
    phone: str,
    location_name: str,
    description: str,
    image_bytes: Optional[bytes],
    image_filename: str,
) -> Dict[str, Any]:
    """
    Full pipeline:
      1. Save & pre-process image
      2. Run AI detection
      3. Geocode location
      4. Persist to DB
      5. Return result summary
    """

    # ── 1. Image ────────────────────────────────────────────────────────────
    local_path = None
    s3_url     = None
    ai_result  = {
        "pothole_detected": False,
        "severity_score":   0.0,
        "severity_level":   "Unknown",
        "method":           "No image",
    }

    if image_bytes:
        local_path, s3_url = process_and_store_image(image_bytes, image_filename)
        ai_result = analyse_image(local_path)

    # ── 2. Geocoding ─────────────────────────────────────────────────────────
    lat, lon = geocode_location(location_name)

    # ── 3. Build record ──────────────────────────────────────────────────────
    record: Dict[str, Any] = {
        "name":             name,
        "email":            email,
        "phone":            phone,
        "location_name":    location_name,
        "latitude":         lat,
        "longitude":        lon,
        "description":      description,
        "image_path":       local_path or "",
        "image_url":        s3_url or (local_path or ""),
        "severity_level":   ai_result["severity_level"],
        "severity_score":   ai_result["severity_score"],
        "pothole_detected": 1 if ai_result["pothole_detected"] else 0,
        "status":           "Pending",
        "date":             datetime.now().isoformat(sep=" ", timespec="seconds"),
    }

    complaint_id = insert_complaint(record)
    record["id"] = complaint_id
    record["ai_result"] = ai_result

    return record
