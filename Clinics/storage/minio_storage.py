# storage/minio_storage.py
import io
import uuid
import os
import asyncio
from pathlib import Path
from typing import Optional

from minio import Minio
from minio.error import S3Error
from dotenv import load_dotenv

load_dotenv()

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")
MINIO_BUCKET = os.getenv("MINIO_BUCKET")

MINIO_SECURE = os.getenv("MINIO_SECURE", "false").lower() in ("1", "true", "yes")

# 🔥 IMPORTANT: must be browser-accessible
MINIO_PUBLIC_BASE = os.getenv("MINIO_PUBLIC_BASE")

if not MINIO_PUBLIC_BASE:
    raise RuntimeError("MINIO_PUBLIC_BASE is not set")

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
    ext = Path(original_filename).suffix or ""
    return f"{uuid.uuid4().hex}{ext}"


async def _ensure_bucket() -> None:
    def _ensure():
        client = _get_client()
        if not client.bucket_exists(MINIO_BUCKET):
            client.make_bucket(MINIO_BUCKET)

    await asyncio.to_thread(_ensure)


async def _put_object(filename: str, data: bytes, content_type: str) -> None:
    def _put():
        client = _get_client()
        stream = io.BytesIO(data)
        client.put_object(
            MINIO_BUCKET,
            filename,
            stream,
            length=len(data),
            content_type=content_type,
        )

    await asyncio.to_thread(_put)


async def upload_file(filename: str, data: bytes, content_type: str) -> str:
    try:
        await _ensure_bucket()
        await _put_object(filename, data, content_type)

        # 🔥 PUBLIC URL RETURNED
        return f"{MINIO_PUBLIC_BASE}/{filename}"

    except S3Error as e:
        raise RuntimeError(f"MinIO upload failed: {e}")


async def delete_file(filename: str) -> bool:
    def _remove():
        client = _get_client()
        client.remove_object(MINIO_BUCKET, filename)

    try:
        await asyncio.to_thread(_remove)
        return True
    except S3Error:
        return False

def extract_object_key(public_url: str) -> str:
    """
    Converts a public MinIO URL back to its object key.
    """
    if not public_url.startswith(MINIO_PUBLIC_BASE):
        raise ValueError("URL does not belong to configured MinIO public base")

    return public_url.replace(f"{MINIO_PUBLIC_BASE}/", "", 1)