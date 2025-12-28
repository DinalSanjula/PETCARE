
from fastapi import (
    APIRouter, Depends, UploadFile, File, Form,
    HTTPException, status, Query
)
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from db import get_db
from Users.auth.security import get_current_active_user
from Clinics.utils.helpers import require_roles
from Users.models import User, UserRole

from Reports.schemas.schemas import (
    ReportResponse,
    ReportResponseBase,
    ReportCreate,
    ReportUpdate,
    ReportImageResponse,
    ReportNoteResponse,
    ReportNoteCreate,
    ReportStatusUpdate, ReportListResponse,
)

from Reports.services.report_service import (
    create_report,
    get_report_by_id,
    list_reports,
    update_report,
    update_report_status,
    delete_report,
)

from Reports.services.report_images import (
    create_report_image,
    list_images_for_report,
)

from Reports.services.report_service import (
    create_report_note,
    list_notes_for_report,
)

from Clinics.storage.reports_storage import (
    upload_report_image as upload_report_image_to_minio
)

router = APIRouter(tags=["reports"])

@router.post(
    "/",
    response_model=ReportResponseBase,
    status_code=status.HTTP_201_CREATED,
)
async def create_new_report(
    animal_type: str = Form(...),
    condition: str = Form(...),
    description: str = Form(...),
    address: str = Form(...),
    contact_phone: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    report_create = ReportCreate(
        animal_type=animal_type,
        condition=condition,
        description=description,
        address=address,
        contact_phone=contact_phone,
    )

    report = await create_report(db, report_create)

    # set reporter
    report.reporter_user_id = current_user.id
    await db.commit()
    await db.refresh(report)

    if image:
        image_url = await upload_report_image_to_minio(
            report_id=report.id,
            file=image,
        )
        await create_report_image(
            session=db,
            report_id=report.id,
            image_url=image_url,
        )

    return report

@router.get("/", response_model=List[ReportListResponse])
async def read_reports(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    return await list_reports(db, skip=skip, limit=limit)


@router.get("/{report_id}", response_model=ReportResponseBase)
async def read_report(
    report_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    report = await get_report_by_id(db, report_id)

    if (
        current_user.role != UserRole.ADMIN
        and report.reporter_user_id != current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to view this report",
        )

    return report

@router.patch("/{report_id}", response_model=ReportResponseBase)
async def update_report_details(
    report_id: int,
    report_update: ReportUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    report = await get_report_by_id(db, report_id)

    if (
        current_user.role != UserRole.ADMIN
        and report.reporter_user_id != current_user.id
    ):
        raise HTTPException(status_code=403, detail="Not allowed")

    return await update_report(db, report_id, report_update)


@router.patch(
    "/{report_id}/status",
    response_model=ReportResponseBase,
    dependencies=[Depends(require_roles(UserRole.ADMIN))],
)
async def update_report_status_endpoint(
    report_id: int,
    status_update: ReportStatusUpdate,
    db: AsyncSession = Depends(get_db),
):
    return await update_report_status(db, report_id, status_update.status)


@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_report_endpoint(
    report_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    report = await get_report_by_id(db, report_id)

    if (
        current_user.role != UserRole.ADMIN
        and report.reporter_user_id != current_user.id
    ):
        raise HTTPException(status_code=403, detail="Not allowed")

    await delete_report(db, report_id)
    return None


@router.post(
    "/{report_id}/images",
    response_model=ReportImageResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_report_image_endpoint(
    report_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    report = await get_report_by_id(db, report_id)

    if (
        current_user.role != UserRole.ADMIN
        and report.reporter_user_id != current_user.id
    ):
        raise HTTPException(status_code=403, detail="Not allowed")

    image_url = await upload_report_image_to_minio(
        report_id=report_id,
        file=file,
    )

    return await create_report_image(
        session=db,
        report_id=report_id,
        image_url=image_url,
    )

@router.get(
    "/{report_id}/images",
    response_model=List[ReportImageResponse],
)
async def list_report_images(
    report_id: int,
    db: AsyncSession = Depends(get_db),
):
    report = await get_report_by_id(db, report_id)
    return await list_images_for_report(db, report_id)



@router.post(
    "/{report_id}/notes",
    response_model=ReportNoteResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles(UserRole.ADMIN))],
)
async def create_report_note_endpoint(
    report_id: int,
    note: ReportNoteCreate,
    db: AsyncSession = Depends(get_db),
):
    return await create_report_note(
        db,
        report_id=report_id,
        note=note.note,
        created_by="admin",
    )


@router.get(
    "/{report_id}/notes",
    response_model=List[ReportNoteResponse],
    dependencies=[Depends(require_roles(UserRole.ADMIN))],
)
async def list_report_notes(
    report_id: int,
    db: AsyncSession = Depends(get_db),
):
    return await list_notes_for_report(db, report_id)


@router.get(
    "/stats/overview",
    dependencies=[Depends(require_roles(UserRole.ADMIN))],
)
async def get_stats(
    db: AsyncSession = Depends(get_db),
):
    reports = await list_reports(db, limit=1000)
    stats = {}

    for r in reports:
        stats[r.status] = stats.get(r.status, 0) + 1

    return stats