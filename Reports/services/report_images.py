from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from Reports.models.models import Report, ReportImage
from Clinics.utils.helpers import get_or_404
from Clinics.storage.minio_storage import delete_file, extract_object_key


# =========================
# CREATE
# =========================
async def create_report_image(
    session: AsyncSession,
    report_id: int,
    image_url: str,
) -> ReportImage:

    await get_or_404(session, Report, report_id, name="Report")

    image = ReportImage(
        report_id=report_id,
        image_url=image_url,
    )

    session.add(image)
    try:
        await session.commit()
        await session.refresh(image)
    except IntegrityError as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e.orig),
        )

    return image


# =========================
# READ ONE
# =========================
async def get_report_image_by_id(
    session: AsyncSession,
    image_id: int,
) -> ReportImage:

    result = await session.execute(
        select(ReportImage)
        .where(ReportImage.id == image_id)
        .options(selectinload(ReportImage.report))
    )

    image = result.scalar_one_or_none()
    if image is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report image not found",
        )

    return image


# =========================
# READ LIST
# =========================
async def list_images_for_report(
    session: AsyncSession,
    report_id: int,
) -> List[ReportImage]:

    q = (
        select(ReportImage)
        .where(ReportImage.report_id == report_id)
        .order_by(ReportImage.id.asc())
        .options(selectinload(ReportImage.report))
    )

    result = await session.execute(q)
    return list(result.scalars().all())


# =========================
# UPDATE (URL ONLY)
# =========================
async def update_report_image(
    session: AsyncSession,
    image_id: int,
    image_url: Optional[str] = None,
) -> ReportImage:

    image = await get_report_image_by_id(session, image_id)

    if image_url is not None:
        image.image_url = image_url

        try:
            await session.commit()
            await session.refresh(image)
        except IntegrityError as e:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            )

    return image


# =========================
# DELETE (FIXED)
# =========================
async def delete_report_image(
    session: AsyncSession,
    image_id: int,
    delete_from_storage: bool = True,
) -> None:

    image = await get_report_image_by_id(session, image_id)

    if delete_from_storage:
        try:
            # 🔥 Extract object key from public URL
            object_key = extract_object_key(image.image_url)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Invalid image URL format",
            )

        ok = await delete_file(object_key)
        if not ok:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete file from storage",
            )

    try:
        await session.delete(image)
        await session.commit()
    except Exception:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete database record",
        )