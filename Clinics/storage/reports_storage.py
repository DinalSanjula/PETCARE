
from fastapi import UploadFile, HTTPException, status
from typing import Optional

from Clinics.storage.minio_storage import (
    upload_file,
    generate_stored_filename,
)

MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB


async def upload_report_image(
    *,
    report_id: int,
    file: UploadFile,
) -> str:

    if not file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file provided",
        )

    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image",
        )

    data = await file.read()

    if len(data) > MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Image size exceeds 5MB",
        )

    stored_name = generate_stored_filename(file.filename)

    object_key = f"reports/report-{report_id}/{stored_name}"

    try:
        return await upload_file(
            filename=object_key,
            data=data,
            content_type=file.content_type,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )