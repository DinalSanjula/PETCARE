from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, status, Form, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from Clinics.utils.auth import get_current_user
from db import get_db
from Clinics.schemas.clinic_image import ClinicImageCreate, ClinicImageResponse, ClinicImageUpdate
from Clinics.crud.images_crud import create_clinic_image, update_clinic_image, delete_image, get_image_by_id, list_images_for_clinic
from Clinics.storage.minio_storage import generate_stored_filename, upload_file,delete_file as minio_delete_file
from PIL import Image
import io

router = APIRouter()

@router.post("/clinics/{clinic_id}/", response_model=ClinicImageResponse, status_code=status.HTTP_201_CREATED, summary="Upload image for clinic")
async def upload_clinic_image(clinic_id:int, file:UploadFile = File(...),
                              session : AsyncSession = Depends(get_db)):

    ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unsupported file type : {file.content_type}")

    MAX_SIZE = 5 * 1024 * 1024
    data = await file.read()

    if len(data) > MAX_SIZE:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"File too large : Max allowed size is {MAX_SIZE/1024/1024}")

    try:
        Image.open(io.BytesIO(data)).verify()
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or corrupted image")

    stored_filename = generate_stored_filename(file.filename)
    content_type = file.content_type

    public_url = await upload_file(filename=stored_filename, content_type=content_type, data=data)

    created = await create_clinic_image(
        session=session,
        clinic_id=clinic_id,
        filename=stored_filename,
        url=public_url,
        content_type=content_type,
        original_filename=file.filename
    )

    return created

@router.get("/clinics/{clinic_id}/", response_model=List[ClinicImageResponse])
async def images_for_clinic(clinic_id:int, session: AsyncSession = Depends(get_db)):
    images = await list_images_for_clinic(session=session, clinic_id=clinic_id)
    return images

@router.get("/{image_id}/", response_model=ClinicImageResponse)
async def get_image(image_id:int, session:AsyncSession = Depends(get_db)):
    img = await get_image_by_id(session=session, image_id=image_id)
    if img is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found!")
    return img

@router.patch("/{image_id}", response_model=ClinicImageResponse)
async def patch_image(
    image_id: int,
    file: Optional[UploadFile] = File(None),
    original_filename: Optional[str] = Form(None),
    content_type: Optional[str] = Form(None),
    url: Optional[str] = Form(None),
    session: AsyncSession = Depends(get_db),
):
    img = await get_image_by_id(session, image_id)
    if img is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found!")

    updates = {}

    if file is not None:
        ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}
        MAX_SIZE = 5 * 1024 * 1024

        if file.content_type not in ALLOWED_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file type: {file.content_type}",
            )

        data = await file.read()
        if len(data) > MAX_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File too large: Max allowed size is {MAX_SIZE / (1024 * 1024)} MB",
            )


        buf = io.BytesIO(data)
        try:
            pil_img = Image.open(buf)
            pil_img.verify()
        except Exception:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or corrupted image")

        try:
            buf.seek(0)
            pil_img = Image.open(buf)
            fmt = getattr(pil_img, "format", None)
        except Exception:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unable to read image format")

        fmt_map = {"JPEG": "image/jpeg", "JPG": "image/jpeg", "PNG": "image/png", "WEBP": "image/webp"}
        detected_mime = fmt_map.get(fmt, file.content_type or "application/octet-stream")

        if detected_mime not in ALLOWED_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file type detected: {detected_mime}",
            )

        if content_type is not None and content_type != detected_mime:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Provided content_type does not match actual file content ({detected_mime})",
            )

        if url is not None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot set url when uploading a file")

        chosen_original = original_filename or file.filename

        new_stored_filename = generate_stored_filename(file.filename)
        try:
            new_url = await upload_file(filename=new_stored_filename, data=data, content_type=detected_mime)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Upload failed: {e}")

        #delete the old file
        try:
            removed = await minio_delete_file(img.filename)
        except Exception:
            try:
                await minio_delete_file(new_stored_filename)
            except Exception:
                pass
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete old file from storage")

        if not removed:
            try:
                await minio_delete_file(new_stored_filename)
            except Exception:
                pass
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete old file from storage")

        updates["filename"] = new_stored_filename
        updates["url"] = new_url
        updates["content_type"] = detected_mime
        updates["original_filename"] = chosen_original

    else:
        if content_type is not None:
            if content_type not in {"image/jpeg", "image/png", "image/webp"}:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Unsupported content_type: {content_type}",
                )
            updates["content_type"] = content_type

        if url is not None:
            updates["url"] = url

        if original_filename is not None:
            updates["original_filename"] = original_filename

    if not updates:
        return img

    updated = await update_clinic_image(
        session=session,
        image_id=image_id,
        filename=updates.get("filename"),
        url=updates.get("url"),
        content_type=updates.get("content_type"),
        original_filename=updates.get("original_filename"),
    )

    return updated




@router.delete("/{image_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_image_endpoint(image_id:int,
                       session:AsyncSession = Depends(get_db),
                       current_user = Depends(get_current_user)):

    img = await get_image_by_id(session, image_id)
    if img is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found!")

    if img.clinic.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to delete")

    try:
        await delete_image(session=session,
                           image_id=image_id,
                           delete_from_storage=True)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    return None

