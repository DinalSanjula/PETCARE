import enum
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, Enum as SaEnum, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from database import Base

class ReportStatus(str, enum.Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    RESCUED = "RESCUED"
    TREATED = "TREATED"
    TRANSFERRED = "TRANSFERRED"
    CLOSED = "CLOSED"
    REJECTED = "REJECTED"

class Report(Base):
    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    animal_type: Mapped[str] = mapped_column(String(50))
    condition: Mapped[str] = mapped_column(String(50))
    description: Mapped[str] = mapped_column(Text)
    address: Mapped[str] = mapped_column(String(255))
    contact_phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    status: Mapped[ReportStatus] = mapped_column(SaEnum(ReportStatus), default=ReportStatus.OPEN)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    reporter_user_id: Mapped[Optional[int]] = mapped_column(nullable=True)
    assigned_clinic_id: Mapped[Optional[int]] = mapped_column(nullable=True)

class ReportImage(Base):
    __tablename__ = "report_images"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    report_id: Mapped[int] = mapped_column(index=True)
    image_url: Mapped[str] = mapped_column(String(255))

class ReportNote(Base):
    __tablename__ = "report_notes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    report_id: Mapped[int] = mapped_column(index=True)
    note: Mapped[str] = mapped_column(Text)
    created_by: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
