from typing import Optional, List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from sqlalchemy import select, func
from Reports.models.models import Report, ReportImage

from Reports.models.models import Report, ReportStatus, ReportNote
from Reports.schemas.schemas import ReportCreate, ReportUpdate
from Clinics.utils.helpers import get_or_404

async def create_report(
    session: AsyncSession,
    report: ReportCreate,
) -> Report:

    db_report = Report(
        animal_type=report.animal_type,
        condition=report.condition,
        description=report.description,
        address=report.address,
        contact_phone=report.contact_phone,
        status=ReportStatus.OPEN,
    )

    session.add(db_report)

    try:
        await session.commit()
        await session.refresh(db_report)
    except IntegrityError as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e.orig),
        )

    return db_report

async def get_report_by_id(
    session: AsyncSession,
    report_id: int,
) -> Report:

    return await get_or_404(session, Report, report_id, name="Report")


async def list_reports(
    session: AsyncSession,
    skip: int = 0,
    limit: int = 100,
):
    stmt = (select(Report,func.min(ReportImage.image_url).label("cover_image_url"))
        .outerjoin(ReportImage, ReportImage.report_id == Report.id)
        .group_by(Report.id)
        .offset(skip)
        .limit(limit)
    )

    result = await session.execute(stmt)

    reports = []
    for report, cover_image_url in result.all():
        report.cover_image_url = cover_image_url
        reports.append(report)

    return reports

async def update_report(
    session: AsyncSession,
    report_id: int,
    report_update: ReportUpdate,
) -> Report:

    report = await get_report_by_id(session, report_id)

    update_data = report_update.model_dump(exclude_unset=True)

    if not update_data:
        return report

    for key, value in update_data.items():
        setattr(report, key, value)

    try:
        await session.commit()
        await session.refresh(report)
    except IntegrityError as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e.orig),
        )

    return report

async def update_report_status(
    session: AsyncSession,
    report_id: int,
    status: ReportStatus,
) -> Report:

    report = await get_report_by_id(session, report_id)
    report.status = status

    try:
        await session.commit()
        await session.refresh(report)
    except IntegrityError as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e.orig),
        )

    return report

async def delete_report(
    session: AsyncSession,
    report_id: int,
) -> None:

    report = await get_report_by_id(session, report_id)

    try:
        await session.delete(report)
        await session.commit()
    except Exception:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete report",
        )


async def create_report_note(
    session: AsyncSession,
    report_id: int,
    note: str,
) -> ReportNote:


    await get_or_404(session, Report, report_id, name="Report")

    report_note = ReportNote(
        report_id=report_id,
        note=note
    )

    session.add(report_note)

    try:
        await session.commit()
        await session.refresh(report_note)
    except IntegrityError as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e.orig),
        )

    return report_note

async def list_notes_for_report(
    session: AsyncSession,
    report_id: int,
) -> List[ReportNote]:


    await get_or_404(session, Report, report_id, name="Report")

    result = await session.execute(
        select(ReportNote)
        .where(ReportNote.report_id == report_id)
        .order_by(ReportNote.id.asc())
    )

    return list(result.scalars().all())

