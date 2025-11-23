from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List, cast
from Clinics.models import Clinic, ClinicImage
from Clinics.utils.helpers import get_or_404
from fastapi import HTTPException, status
from sqlalchemy import select, ColumnElement
from Clinics.storage.minio_storage import delete_file

async def create_clinic_image(
        session:AsyncSession,
        clinic_id:int,
        filename:int,
        url:str ,
        content_type:str,
        original_filename: Optional[str] = None
) -> ClinicImage:

    await get_or_404(session, Clinic, clinic_id, name="Clinic")

    image = ClinicImage(
        clinic_id = clinic_id,
        filename = filename,
        original_filename = original_filename,
        url = url,
        content_type = content_type
    )

    session.add(image)
    try:
        await session.commit()
        await session.refresh(image)
    except IntegrityError as e:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e.orig))

    return image

async def get_image_by_id(session:AsyncSession, image_id:int)-> ClinicImage:
    cond = cast(ColumnElement[bool], ClinicImage.id == image_id)
    q = select(ClinicImage).where(cond)
    result = await session.execute(q)
    img = result.scalar_one_or_none()
    if img is None:
        HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")
    return img

async def list_images_for_clinic(session:AsyncSession, clinic_id:int)-> List[ClinicImage]:
    cond = cast(ColumnElement[bool], ClinicImage.clinic_id == clinic_id)
    q = select(ClinicImage).where(cond).order_by(ClinicImage.id.asc())
    result = await session.execute(q)
    return list(result.scalars().all())

async def update_clinic_image(
        session:AsyncSession,
        image_id:int,
        filename:Optional[int] = None,
        url:Optional[str] = None,
        content_type:Optional[str] = None,
        original_filename: Optional[str] = None
) -> ClinicImage:

    image = await get_image_by_id(session, image_id)
    changed = False

    if filename is not None:
        image.filename = filename
        changed = True

    if url is not None:
        image.url = url
        changed = True

    if content_type is not None:
        image.content_type = content_type
        changed = True

    if original_filename is not None:
        image.original_filename = original_filename
        changed = True

    if changed:
        session.add(image)
        try:
            await session.commit()
            await session.refresh(image)
        except IntegrityError as e:
            await session.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return image

async def delete_image(session:AsyncSession, image_id:int, delete_from_storage:bool = True) -> None:
    image = await get_image_by_id(session, image_id)

    if delete_from_storage:
        ok = await delete_file(image.filename)
        if not ok:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete file from storage")

    try:
        await session.delete(image)
        await session.commit()
    except Exception:
        await session.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete database record")