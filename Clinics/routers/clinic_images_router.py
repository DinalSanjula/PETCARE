from typing import List, Optional
from fastapi import (
    APIRouter, UploadFile, File,
    HTTPException, status, Depends
)
from sqlalchemy.ext.asyncio import AsyncSession
from PIL import Image
import io

from db import get_db
from Users.auth.security import get_current_active_user
from Users.models.user_model import User, UserRole
from Clinics.utils.helpers import require_roles
from Clinics.crud.clinic_crud import get_clinic_by_id
from Clinics.crud.images_crud import (
    create_clinic_image,
    update_clinic_image,
    delete_image,
    get_image_by_id,
    list_images_for_clinic,
)
from Clinics.storage.minio_storage import (
    generate_stored_filename,
    upload_file,
    delete_file as minio_delete_file,
)
from Clinics.schemas.clinic_image import ClinicImageResponse

router = APIRouter(tags=["Images"])

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_SIZE = 5 * 1024 * 1024


@router.post(
    "/clinics/{clinic_id}",
    response_model=ClinicImageResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles(UserRole.CLINIC, UserRole.ADMIN))],
)
async def upload_clinic_image(
    clinic_id: int,
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    clinic = await get_clinic_by_id(clinic_id=clinic_id, session=session)

    if clinic.owner_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not allowed")

    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    data = await file.read()
    if len(data) > MAX_SIZE:
        raise HTTPException(status_code=400, detail="File too large (max 5MB)")

    try:
        Image.open(io.BytesIO(data)).verify()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid image")

    stored_name = generate_stored_filename(file.filename)
    object_key = f"clinics/clinic-{clinic_id}/{stored_name}"

    public_url = await upload_file(
        filename=object_key,
        data=data,
        content_type=file.content_type,
    )

    image = await create_clinic_image(
        session=session,
        clinic_id=clinic_id,
        filename=object_key,
        url=public_url,
        content_type=file.content_type,
        original_filename=file.filename,
    )

    return image


@router.get("/clinics/{clinic_id}", response_model=List[ClinicImageResponse])
async def images_for_clinic(
    clinic_id: int,
    session: AsyncSession = Depends(get_db),
):
    return await list_images_for_clinic(session=session, clinic_id=clinic_id)


@router.get("/{image_id}", response_model=ClinicImageResponse)
async def get_image(
    image_id: int,
    session: AsyncSession = Depends(get_db),
):
    return await get_image_by_id(session=session, image_id=image_id)


@router.patch(
    "/{image_id}",
    response_model=ClinicImageResponse,
    dependencies=[Depends(require_roles(UserRole.CLINIC, UserRole.ADMIN))],
)
async def patch_image(
    image_id: int,
    file: Optional[UploadFile] = File(None),
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    img = await get_image_by_id(session, image_id)

    if img.clinic.owner_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not allowed")

    if not file:
        return img

    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    data = await file.read()
    if len(data) > MAX_SIZE:
        raise HTTPException(status_code=400, detail="File too large")

    try:
        Image.open(io.BytesIO(data)).verify()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid image")

    stored_name = generate_stored_filename(file.filename)
    object_key = f"clinics/clinic-{img.clinic_id}/{stored_name}"

    new_url = await upload_file(
        filename=object_key,
        data=data,
        content_type=file.content_type,
    )

    # Delete old file with proper rollback
    try:
        removed = await minio_delete_file(img.filename)
        if not removed:
            raise Exception("Delete returned False")
    except Exception:
        # Rollback: delete newly uploaded file
        try:
            await minio_delete_file(object_key)
        except Exception:
            pass
        raise HTTPException(status_code=500, detail="Failed to delete old file")

    return await update_clinic_image(
        session=session,
        image_id=image_id,
        filename=object_key,
        url=new_url,
        content_type=file.content_type,
        original_filename=file.filename,
    )


@router.delete(
    "/{image_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_roles(UserRole.CLINIC, UserRole.ADMIN))],
)
async def delete_image_endpoint(
    image_id: int,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    img = await get_image_by_id(session, image_id)

    if img.clinic.owner_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not allowed")

    await delete_image(
        session=session,
        image_id=image_id,
        delete_from_storage=True,
    )