import enum
from sqlalchemy import Column, Integer, String, Text, Enum as SaEnum, DateTime, func
from database import Base

class ReportStatus(str, enum.Enum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"

class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(Text, nullable=False)
    location_lat = Column(String(50), nullable=True) # Keeping as string for simplicity or float
    location_lng = Column(String(50), nullable=True)
    image_url = Column(String(255), nullable=True)
    status = Column(SaEnum(ReportStatus), default=ReportStatus.NEW)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
