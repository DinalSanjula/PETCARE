
from db import Base
from sqlalchemy import (
    Column, Integer, String, Text,
    Enum, DateTime, ForeignKey, func, Nullable, Boolean
)
from sqlalchemy.orm import relationship
import enum

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

    id = Column(Integer, primary_key=True, index=True)
    animal_type = Column(String(50), nullable=False)
    condition = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)
    address = Column(String(255), nullable=False)
    contact_phone = Column(String(20), nullable=True)
    status = Column(Enum(ReportStatus, name="report_status_enum"),default=ReportStatus.OPEN,Nullable=False)
    reporter_user_id = Column(Integer,ForeignKey("users.id", ondelete="SET NULL"),nullable=True)
    created_at = Column(DateTime(timezone=True),server_default=func.now(),nullable=False)


    images = relationship("ReportImage",back_populates="report",cascade="all, delete-orphan",passive_deletes=True)
    notes = relationship("ReportNote",back_populates="report",cascade="all, delete-orphan",passive_deletes=True)


class ReportImage(Base):
    __tablename__ = "report_images"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer,ForeignKey("reports.id", ondelete="CASCADE"),nullable=False,index=True)
    image_url = Column(String(255), nullable=False)

    report = relationship("Report", back_populates="images")

class ReportNote(Base):
    __tablename__ = "report_notes"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer,ForeignKey("reports.id", ondelete="CASCADE"),nullable=False,index=True)
    note = Column(Text, nullable=False)
    created_by = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True),server_default=func.now(),nullable=False)

    report = relationship("Report", back_populates="notes")


class ReportMessage(Base):
    __tablename__ = "report_messages"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer,ForeignKey("reports.id", ondelete="CASCADE"),nullable=False,index=True)
    sender_user_id = Column( Integer,ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, server_default="false", nullable=False)
    created_at = Column(DateTime(timezone=True),server_default=func.now(),nullable=False)

    report = relationship("Report", back_populates="messages")