# storage/minio_storage.py
from minio import Minio
from minio.error import S3Error
from pathlib import Path
import uuid
import os
import asyncio
from typing import Optional

from dotenv import load_dotenv
load_dotenv()

# Configure from env (recommended)
MINIO_ENDPOINT = os.environ.get("MINIO_ENDPOINT", "localhost:9000")
MINIO_ACCESS_KEY = os.environ.get("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.environ.get("MINIO_SECRET_KEY", "minioadmin")
MINIO_SECURE = os.environ.get("MINIO_SECURE", "false").lower() in ("1", "true", "yes")
BUCKET = os.environ.get("MINIO_BUCKET", "clinic-images")
PUBLIC_BASE = os.environ.get("MINIO_PUBLIC_BASE", f"http://{MINIO_ENDPOINT}/{BUCKET}")  # used for public URL

# Minio client is synchronous; call it via asyncio.to_thread
_client: Optional[Minio] = None


def _get_client() -> Minio:
    global _client
    if _client is None:
        _client = Minio(
            MINIO_ENDPOINT,
            access_key=MINIO_ACCESS_KEY,
            secret_key=MINIO_SECRET_KEY,
            secure=MINIO_SECURE,
        )
    return _client


def generate_stored_filename(original_filename: str) -> str:
    # Keep extension if present, use uuid for uniqueness
    ext = Path(original_filename).suffix or ""
    return f"{uuid.uuid4().hex}{ext}"


async def _put_object(filename: str, data: bytes, content_type: str) -> None:
    client = _get_client()
    # MinIO's put_object expects a readable file-like or bytes obj; use to_thread
    def _put():
        client.put_object(BUCKET, filename, data, length=len(data), content_type=content_type)
    await asyncio.to_thread(_put)


async def upload_file(filename: str, data: bytes, content_type: str) -> str:
    """
    Upload bytes to MinIO and return the public URL for the object.
    """
    try:
        # ensure bucket exists (idempotent)
        def _ensure_bucket():
            client = _get_client()
            if not client.bucket_exists(BUCKET):
                client.make_bucket(BUCKET)
        await asyncio.to_thread(_ensure_bucket)

        await _put_object(filename, data, content_type)
        # return public URL (assumes bucket is public, or you will serve via proxy)
        return f"{PUBLIC_BASE}/{filename}"
    except S3Error as e:
        raise RuntimeError(f"minio upload failed: {e}")


async def delete_file(filename: str) -> bool:
    """
    Delete object from MinIO. Return True on success, False on failure.
    """
    try:
        def _remove():
            client = _get_client()
            client.remove_object(BUCKET, filename)
        await asyncio.to_thread(_remove)
        return True
    except S3Error:
        return False