# storage/minio_storage.py
import io

from minio import Minio
from minio.error import S3Error
from pathlib import Path
import uuid
import os
import asyncio
from typing import Optional

from dotenv import load_dotenv
load_dotenv()

MINIO_ENDPOINT = os.environ.get("MINIO_ENDPOINT")
MINIO_ACCESS_KEY = os.environ.get("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = os.environ.get("MINIO_SECRET_KEY")
MINIO_SECURE = os.environ.get("MINIO_SECURE").lower() in ("1", "true", "yes")
BUCKET = os.environ.get("MINIO_BUCKET")
PUBLIC_BASE = os.environ.get("MINIO_PUBLIC_BASE", f"http://{MINIO_ENDPOINT}/{BUCKET}")  # used for public URL

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


async def _put_object(filename: str, data: bytes, content_type: str) -> None:

    def _put():
        client = _get_client()
        stream = io.BytesIO(data)
        client.put_object(BUCKET, filename, stream, length=len(data), content_type=content_type)
    await asyncio.to_thread(_put)


async def upload_file(filename: str, data: bytes, content_type: str) -> str:

    try:
        def _ensure_bucket():
            client = _get_client()
            if not client.bucket_exists(BUCKET):
                client.make_bucket(BUCKET)
        await asyncio.to_thread(_ensure_bucket)

        await _put_object(filename, data, content_type)
        return f"{PUBLIC_BASE}/{filename}"
    except S3Error as e:
        raise RuntimeError(f"minio upload failed: {e}")


async def delete_file(filename: str) -> bool:

    try:
        def _remove():
            client = _get_client()
            client.remove_object(BUCKET, filename)
        await asyncio.to_thread(_remove)
        return True
    except S3Error:
        return False