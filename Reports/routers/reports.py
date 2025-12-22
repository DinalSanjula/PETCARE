from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from database import get_db
from schemas import (
    ReportOut, ReportCreate, ReportUpdate, ReportImageOut, 
    ReportNoteOut, ReportNoteCreate, ReportStatusUpdate
)
from services import file_service, report_service

router = APIRouter(
    prefix="/reports",
    tags=["reports"]
)

@router.post("/", response_model=ReportOut, status_code=status.HTTP_201_CREATED)
async def create_new_report(
    animal_type: str = Form(...),
    condition: str = Form(...),
    description: str = Form(...),
    address: str = Form(...),
    contact_phone: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db)
):
    report_create = ReportCreate(
        animal_type=animal_type,
        condition=condition,
        description=description,
        address=address,
        contact_phone=contact_phone
    )
    db_report = await report_service.create_report(db=db, report=report_create)
    
    if image:
        image_url = await file_service.save_upload_file(image)
        await report_service.add_report_image(db, db_report.id, image_url)
        
    return db_report

@router.get("/", response_model=List[ReportOut])
async def read_reports(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    return await report_service.get_reports(db, skip=skip, limit=limit)

@router.get("/{report_id}", response_model=ReportOut)
async def read_report(report_id: int, db: AsyncSession = Depends(get_db)):
    db_report = await report_service.get_report(db, report_id=report_id)
    if db_report is None:
        raise HTTPException(status_code=404, detail="Report not found")
    return db_report

@router.patch("/{report_id}", response_model=ReportOut)
async def update_report_details(report_id: int, report_update: ReportUpdate, db: AsyncSession = Depends(get_db)):
    db_report = await report_service.update_report(db, report_id, report_update)
    if db_report is None:
        raise HTTPException(status_code=404, detail="Report not found")
    return db_report

@router.patch("/{report_id}/status", response_model=ReportOut)
async def update_status_endpoint(report_id: int, status_update: ReportStatusUpdate, db: AsyncSession = Depends(get_db)):
    db_report = await report_service.update_report_status(db, report_id, status_update.status)
    if db_report is None:
        raise HTTPException(status_code=404, detail="Report not found")
    return db_report

@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_report(report_id: int, db: AsyncSession = Depends(get_db)):
    db_report = await report_service.delete_report(db, report_id)
    if db_report is None:
        raise HTTPException(status_code=404, detail="Report not found")
    return None

@router.post("/{report_id}/images", response_model=ReportImageOut, status_code=status.HTTP_201_CREATED)
async def upload_report_image(report_id: int, file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    db_report = await report_service.get_report(db, report_id)
    if not db_report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    image_url = await file_service.save_upload_file(file)
    return await report_service.add_report_image(db, report_id, image_url)

@router.post("/{report_id}/notes", response_model=ReportNoteOut, status_code=status.HTTP_201_CREATED)
async def create_report_note(report_id: int, note: ReportNoteCreate, db: AsyncSession = Depends(get_db)):
    db_report = await report_service.get_report(db, report_id)
    if not db_report:
        raise HTTPException(status_code=404, detail="Report not found")
        
    return await report_service.add_report_note(db, report_id, note.note, created_by="admin")

@router.get("/{report_id}/notes", response_model=List[ReportNoteOut])
async def read_report_notes(report_id: int, db: AsyncSession = Depends(get_db)):
    if not await report_service.get_report(db, report_id):
        raise HTTPException(status_code=404, detail="Report not found")
    return await report_service.get_report_notes(db, report_id)

@router.get("/stats/overview")
async def get_stats(db: AsyncSession = Depends(get_db)):
    reports = await report_service.get_reports(db, limit=1000)
    stats = {}
    for r in reports:
        stats[r.status] = stats.get(r.status, 0) + 1
    return stats
