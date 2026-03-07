
"""
Image processing service.

Handles:
  - Saving uploaded file bytes to the local temp directory
  - Optional OpenCV pre-processing before AI analysis
  - Optional upload to AWS S3
"""

import os
import sys
import uuid
from datetime import datetime
from typing import Optional, Tuple

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config.settings import (
    UPLOAD_DIR, S3_BUCKET_NAME,
    AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION,
)

# ── Optional libraries ─────────────────────────────────────────────────────
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

try:
    import boto3
    from botocore.exceptions import BotoCoreError, ClientError
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False

try:
    from PIL import Image as PILImage
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


# ──────────────────────────────────────────────────────────────────────────────
# Save uploaded file
# ──────────────────────────────────────────────────────────────────────────────

def save_uploaded_file(file_bytes: bytes, original_name: str) -> str:
    """
    Save raw uploaded bytes to the uploads/temp_images directory.

    Returns the absolute path to the saved file.
    """
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    ext      = os.path.splitext(original_name)[-1].lower() or ".jpg"
    uid      = uuid.uuid4().hex[:10]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename  = f"complaint_{timestamp}_{uid}{ext}"
    filepath  = os.path.join(UPLOAD_DIR, filename)

    with open(filepath, "wb") as f:
        f.write(file_bytes)

    return filepath


# ──────────────────────────────────────────────────────────────────────────────
# Pre-processing
# ──────────────────────────────────────────────────────────────────────────────

def preprocess_image(image_path: str, target_size: Tuple[int, int] = (640, 480)) -> str:
    """
    Resize and normalise the image for AI analysis.
    Returns the path of the processed image (may be the same file).
    """
    if CV2_AVAILABLE:
        img = cv2.imread(image_path)
        if img is not None:
            img = cv2.resize(img, target_size)
            cv2.imwrite(image_path, img)
    elif PIL_AVAILABLE:
        try:
            img = PILImage.open(image_path).convert("RGB")
            img = img.resize(target_size, PILImage.LANCZOS)
            img.save(image_path)
        except Exception:
            pass
    return image_path


# ──────────────────────────────────────────────────────────────────────────────
# AWS S3 upload
# ──────────────────────────────────────────────────────────────────────────────

def upload_to_s3(image_path: str) -> Optional[str]:
    """
    Upload the image to S3 and return the public URL.
    Returns None if S3 credentials are not configured or upload fails.
    """
    if not BOTO3_AVAILABLE:
        return None
    if not (AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY):
        return None

    try:
        s3 = boto3.client(
            "s3",
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION,
        )
        key = f"complaints/{os.path.basename(image_path)}"
        s3.upload_file(
            image_path,
            S3_BUCKET_NAME,
            key,
            ExtraArgs={"ContentType": "image/jpeg"},
        )
        url = f"https://{S3_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{key}"
        return url
    except Exception:
        return None


# ──────────────────────────────────────────────────────────────────────────────
# Public convenience function used by complaint_service
# ──────────────────────────────────────────────────────────────────────────────

def process_and_store_image(file_bytes: bytes, original_name: str) -> Tuple[str, Optional[str]]:
    """
    Full pipeline: save → pre-process → [upload to S3].

    Returns
    -------
    (local_path, s3_url)   — s3_url is None when S3 is not configured.
    """
    local_path = save_uploaded_file(file_bytes, original_name)
    preprocess_image(local_path)
    s3_url = upload_to_s3(local_path)
    return local_path, s3_url
