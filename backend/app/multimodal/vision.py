"""
Multimodal image handling and validation for Athena.
Supports student uploads of diagrams, equations, screenshots, and exercises.
"""
import base64
import logging
from typing import Dict, Any, Optional
from app.config import settings

logger = logging.getLogger(__name__)

def validate_image_data(data_str: str) -> Dict[str, Any]:
    """
    Validates image data string (data URI or raw base64).
    Enforces format and size limits.
    """
    if not data_str:
        return {"valid": False, "error": "No image data provided."}

    # Check for data URI prefix
    header = ""
    payload = data_str
    mime_type = "image/png"
    
    if data_str.startswith("data:"):
        parts = data_str.split(",", 1)
        if len(parts) == 2:
            header, payload = parts
            mime_part = header.split(";")[0].replace("data:", "").strip()
            if mime_part:
                mime_type = mime_part

    if mime_type not in settings.ALLOWED_IMAGE_TYPES:
        return {
            "valid": False,
            "error": f"Unsupported image MIME type: {mime_type}. Allowed: {', '.join(settings.ALLOWED_IMAGE_TYPES)}"
        }

    try:
        raw_bytes = base64.b64decode(payload)
        size_mb = len(raw_bytes) / (1024 * 1024)
        if size_mb > settings.MAX_UPLOAD_SIZE_MB:
            return {
                "valid": False,
                "error": f"Image exceeds maximum size of {settings.MAX_UPLOAD_SIZE_MB}MB (received {size_mb:.1f}MB)."
            }
        return {
            "valid": True,
            "mime_type": mime_type,
            "size_mb": round(size_mb, 2),
            "payload_length": len(payload)
        }
    except Exception as e:
        return {"valid": False, "error": f"Malformed image base64 data: {e}"}
