from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models import Report, ReportStatus
from schemas import ReportCreate, ReportUpdate

async def create_report(db: AsyncSession, report: ReportCreate):
    db_report = Report(
        animal_type=report.animal_type,
        condition=report.condition,
        description=report.description,
        address=report.address,
        contact_phone=report.contact_phone,
        status=ReportStatus.OPEN
    )
    db.add(db_report)
    await db.commit()
    await db.refresh(db_report)
    return db_report

async def get_reports(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(Report).offset(skip).limit(limit))
    return result.scalars().all()

async def get_report(db: AsyncSession, report_id: int):
    result = await db.execute(select(Report).where(Report.id == report_id))
    return result.scalar_one_or_none()

async def update_report(db: AsyncSession, report_id: int, report_update: ReportUpdate):
    db_report = await get_report(db, report_id)
    if db_report:
        update_data = report_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_report, key, value)
        await db.commit()
        await db.refresh(db_report)
    return db_report

async def update_report_status(db: AsyncSession, report_id: int, status: ReportStatus):
    db_report = await get_report(db, report_id)
    if db_report:
        db_report.status = status
        await db.commit()
        await db.refresh(db_report)
    return db_report

async def delete_report(db: AsyncSession, report_id: int):
    db_report = await get_report(db, report_id)
    if db_report:
        await db.delete(db_report)
        await db.commit()
    return db_report

async def add_report_image(db: AsyncSession, report_id: int, image_url: str):
    from models import ReportImage
    db_image = ReportImage(report_id=report_id, image_url=image_url)
    db.add(db_image)
    await db.commit()
    return db_image

async def add_report_note(db: AsyncSession, report_id: int, note: str, created_by: str = None):
    from models import ReportNote
    db_note = ReportNote(report_id=report_id, note=note, created_by=created_by)
    db.add(db_note)
    await db.commit()
    await db.refresh(db_note)
    return db_note

async def get_report_notes(db: AsyncSession, report_id: int):
    from models import ReportNote
    result = await db.execute(select(ReportNote).where(ReportNote.report_id == report_id))
    return result.scalars().all()
