import os
import uuid
from typing import Tuple
from fastapi import HTTPException, UploadFile, status
from app.core.config import settings

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/jpg"}
ALLOWED_VIDEO_TYPES = {"video/mp4", "video/quicktime", "video/webm", "video/x-msvideo"}
ALLOWED_AUDIO_TYPES = {"audio/mpeg", "audio/wav", "audio/mp4", "audio/m4a", "audio/webm", "audio/ogg"}

IMAGE_MAX_SIZE = 15 * 1024 * 1024  # 15 MB
VIDEO_MAX_SIZE = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024  # 50 MB
AUDIO_MAX_SIZE = 25 * 1024 * 1024  # 25 MB


def sanitize_filename(filename: str) -> str:
    # Strip any directory path components to prevent path traversal
    base = os.path.basename(filename)
    # Remove potentially dangerous characters
    clean = "".join(c for c in base if c.isalnum() or c in "._-")
    return clean or "upload"


def validate_image_upload(file: UploadFile) -> str:
    content_type = (file.content_type or "").lower()
    if content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported image type: '{content_type}'. Allowed types: JPG, PNG, WEBP."
        )
    return content_type


def validate_video_upload(file: UploadFile) -> str:
    content_type = (file.content_type or "").lower()
    if content_type not in ALLOWED_VIDEO_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported video format: '{content_type}'. Allowed formats: MP4, MOV, WEBM."
        )
    return content_type


def validate_audio_upload(file: UploadFile) -> str:
    content_type = (file.content_type or "").lower()
    if content_type not in ALLOWED_AUDIO_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported audio format: '{content_type}'. Allowed formats: MP3, WAV, M4A, WEBM, OGG."
        )
    return content_type


async def save_upload_safely(file: UploadFile, max_bytes: int, prefix: str = "file") -> Tuple[str, bytes, str]:
    """
    Safely reads and saves an upload file with size enforcement, unique name generation,
    and path traversal prevention.
    Returns (saved_filepath, file_bytes, relative_url).
    """
    content = await file.read()
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Uploaded file size ({len(content) / (1024*1024):.1f} MB) exceeds maximum allowed limit ({max_bytes / (1024*1024):.1f} MB)."
        )

    # Derive safe extension
    clean_original = sanitize_filename(file.filename or "upload.bin")
    ext = os.path.splitext(clean_original)[1].lower()
    if not ext:
        ext = ".bin"

    unique_filename = f"{prefix}_{uuid.uuid4().hex[:12]}{ext}"
    dest_path = os.path.join(settings.UPLOAD_DIR, unique_filename)

    with open(dest_path, "wb") as f_out:
        f_out.write(content)

    relative_url = f"/uploads/{unique_filename}"
    return dest_path, content, relative_url
