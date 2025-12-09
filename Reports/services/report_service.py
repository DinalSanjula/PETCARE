from sqlalchemy.orm import Session
from models import Report, ReportStatus
from schemas import ReportCreate, ReportUpdate

def create_report(db: Session, report: ReportCreate, image_url: str = None):
    db_report = Report(
        description=report.description,
        location_lat=report.location_lat,
        location_lng=report.location_lng,
        image_url=image_url,
        status=ReportStatus.NEW
    )
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return db_report

def get_reports(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Report).offset(skip).limit(limit).all()

def get_report(db: Session, report_id: int):
    return db.query(Report).filter(Report.id == report_id).first()

def update_report_status(db: Session, report_id: int, status_update: ReportUpdate):
    db_report = get_report(db, report_id)
    if db_report:
        db_report.status = status_update.status
        db.commit()
        db.refresh(db_report)
    return db_report
