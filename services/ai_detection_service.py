
"""
AI-powered pothole detection service.

Strategy
--------
* If PyTorch / torchvision are available  → use a fine-tuned ResNet-18
  (weights are random here; replace with your trained weights).
* If not available → fall back to an OpenCV-based heuristic analyser.

Either path returns the same dict so the rest of the app is unaffected.
"""

import os
import sys
import random
from typing import Dict, Any, Optional

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config.settings import SEVERITY_THRESHOLDS

# ── Optional heavy imports ──────────────────────────────────────────────────
try:
    import torch
    import torch.nn as nn
    from torchvision import transforms, models
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


# ──────────────────────────────────────────────────────────────────────────────
# Helper: severity from score
# ──────────────────────────────────────────────────────────────────────────────

def score_to_severity(score: float) -> str:
    if score < SEVERITY_THRESHOLDS["low"][1]:
        return "Low"
    elif score < SEVERITY_THRESHOLDS["medium"][1]:
        return "Medium"
    return "High"


# ──────────────────────────────────────────────────────────────────────────────
# PyTorch Model (ResNet-18 backbone)
# ──────────────────────────────────────────────────────────────────────────────

_model: Optional[Any] = None
_transform: Optional[Any] = None

def _load_torch_model():
    global _model, _transform
    if _model is not None:
        return

    model = models.resnet18(weights=None)
    model.fc = nn.Sequential(
        nn.Linear(model.fc.in_features, 128),
        nn.ReLU(),
        nn.Dropout(0.3),
        nn.Linear(128, 2),  # [no_pothole, pothole]
        nn.Softmax(dim=1),
    )
    model_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "models", "pothole_weights.pth"
    )
    if os.path.exists(model_path):
        model.load_state_dict(torch.load(model_path, map_location="cpu"))
    model.eval()
    _model = model

    _transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406],
                             [0.229, 0.224, 0.225]),
    ])


def _analyse_with_torch(image_path: str) -> Dict[str, Any]:
    if not PIL_AVAILABLE:
        raise RuntimeError("Pillow not installed")

    _load_torch_model()
    img = Image.open(image_path).convert("RGB")
    tensor = _transform(img).unsqueeze(0)

    with torch.no_grad():
        probs = _model(tensor)[0]  # [p_no_pothole, p_pothole]

    pothole_prob = float(probs[1].item())
    pothole_detected = pothole_prob > 0.35
    severity_score = pothole_prob if pothole_detected else pothole_prob * 0.5
    severity_level = score_to_severity(severity_score) if pothole_detected else "Low"

    return {
        "pothole_detected": pothole_detected,
        "severity_score":   round(severity_score, 4),
        "severity_level":   severity_level,
        "method":           "PyTorch ResNet-18",
    }


# ──────────────────────────────────────────────────────────────────────────────
# OpenCV heuristic analyser
# ──────────────────────────────────────────────────────────────────────────────

def _analyse_with_opencv(image_path: str) -> Dict[str, Any]:
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError(f"Could not read image: {image_path}")

    # Edge density as a proxy for surface roughness
    blurred = cv2.GaussianBlur(img, (5, 5), 0)
    edges   = cv2.Canny(blurred, 50, 150)
    edge_ratio = float(np.count_nonzero(edges)) / edges.size

    # Variance as a proxy for texture
    variance = float(img.var())
    var_norm = min(variance / 3000.0, 1.0)

    # Dark-region ratio (potholes are dark)
    dark_ratio = float(np.sum(img < 60)) / img.size

    # Combine heuristics
    score = min(
        0.35 * edge_ratio / 0.15 +
        0.35 * var_norm +
        0.30 * dark_ratio / 0.25,
        1.0
    )
    # Add slight stochastic noise to make demo results varied
    score = float(np.clip(score + random.uniform(-0.05, 0.05), 0.0, 1.0))

    pothole_detected = score > 0.30
    severity_level   = score_to_severity(score) if pothole_detected else "Low"

    return {
        "pothole_detected": pothole_detected,
        "severity_score":   round(score, 4),
        "severity_level":   severity_level,
        "method":           "OpenCV Heuristic",
    }


# ──────────────────────────────────────────────────────────────────────────────
# Smart fallback analyser (no CV2 or Torch)
# ──────────────────────────────────────────────────────────────────────────────

def _analyse_smart_fallback(image_path: str) -> Dict[str, Any]:
    """Use PIL pixel statistics when neither Torch nor cv2 are available."""
    if not PIL_AVAILABLE:
        # Pure random demo mode
        score = round(random.uniform(0.15, 0.95), 4)
        return {
            "pothole_detected": score > 0.30,
            "severity_score":   score,
            "severity_level":   score_to_severity(score),
            "method":           "Demo (random)",
        }

    img   = Image.open(image_path).convert("L")
    arr   = np.array(img, dtype=np.float32)
    dark_ratio = float(np.sum(arr < 60)) / arr.size
    var_norm   = min(float(arr.var()) / 3000.0, 1.0)
    score      = float(np.clip(0.5 * dark_ratio / 0.25 + 0.5 * var_norm + random.uniform(-0.05, 0.05), 0.0, 1.0))

    pothole_detected = score > 0.28
    return {
        "pothole_detected": pothole_detected,
        "severity_score":   round(score, 4),
        "severity_level":   score_to_severity(score) if pothole_detected else "Low",
        "method":           "PIL Heuristic",
    }


# ──────────────────────────────────────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────────────────────────────────────

def analyse_image(image_path: str) -> Dict[str, Any]:
    """
    Analyse an image for pothole presence and severity.

    Returns
    -------
    dict with keys:
        pothole_detected : bool
        severity_score   : float  (0–1)
        severity_level   : str    (Low / Medium / High)
        method           : str    (which backend was used)
    """
    if not os.path.exists(image_path):
        return {
            "pothole_detected": False,
            "severity_score":   0.0,
            "severity_level":   "Unknown",
            "method":           "Error - file not found",
        }

    try:
        if TORCH_AVAILABLE and PIL_AVAILABLE:
            return _analyse_with_torch(image_path)
        elif CV2_AVAILABLE:
            return _analyse_with_opencv(image_path)
        else:
            return _analyse_smart_fallback(image_path)
    except Exception as exc:
        # Graceful degradation
        return _analyse_smart_fallback(image_path)
