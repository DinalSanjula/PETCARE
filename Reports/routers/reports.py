from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
from schemas import ReportOut, ReportCreate, ReportUpdate, ReportStatusEnum
from services import file_service, report_service

router = APIRouter(
    prefix="/reports",
    tags=["reports"]
)

@router.post("/", response_model=ReportOut, status_code=status.HTTP_201_CREATED)
async def create_new_report(
    description: str = Form(...),
    location_lat: Optional[str] = Form(None),
    location_lng: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):

    image_url = None
    if file:
        image_url = await file_service.save_upload_file(file)


    report_data = ReportCreate(
        description=description,
        location_lat=location_lat,
        location_lng=location_lng
    )
    
    return report_service.create_report(db=db, report=report_data, image_url=image_url)

@router.get("/", response_model=List[ReportOut])
def read_reports(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return report_service.get_reports(db, skip=skip, limit=limit)

@router.get("/{report_id}", response_model=ReportOut)
def read_report(report_id: int, db: Session = Depends(get_db)):
    db_report = report_service.get_report(db, report_id=report_id)
    if db_report is None:
        raise HTTPException(status_code=404, detail="Report not found")
    return db_report

@router.patch("/{report_id}/status", response_model=ReportOut)
def update_status(report_id: int, status_update: ReportUpdate, db: Session = Depends(get_db)):
    db_report = report_service.update_report_status(db, report_id, status_update)
    if db_report is None:
        raise HTTPException(status_code=404, detail="Report not found")
    return db_report
