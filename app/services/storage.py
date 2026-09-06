from pathlib import Path
import uuid

from app.config import settings

BASE = Path(settings.DATA_DIR)
BASE.mkdir(parents=True, exist_ok=True)


def save_upload(filename: str, content: bytes) -> str:
    suffix = Path(filename).suffix.lower() or ".jpg"
    path = BASE / f"{uuid.uuid4().hex}{suffix}"
    path.write_bytes(content)
    return str(path)


def public_file_path(path: str) -> str:
    """Local dev URL served by the /files static mount in app/main.py.
    In production, swap this for a Supabase Storage or S3 public URL."""
    p = Path(path)
    return f"/files/{p.name}"
