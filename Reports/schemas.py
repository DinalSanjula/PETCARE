from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime
from enum import Enum
from models import ReportStatus

class ReportStatusEnum(str, Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    RESCUED = "RESCUED"
    TREATED = "TREATED"
    TRANSFERRED = "TRANSFERRED"
    CLOSED = "CLOSED"
    REJECTED = "REJECTED"

class ReportImageBase(BaseModel):
    image_url: str

class ReportImageOut(ReportImageBase):
    id: int
    report_id: int
    model_config = ConfigDict(from_attributes=True)

class ReportNoteBase(BaseModel):
    note: str

class ReportNoteCreate(ReportNoteBase):
    pass

class ReportNoteOut(ReportNoteBase):
    id: int
    report_id: int
    created_by: Optional[str] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ReportBase(BaseModel):
    animal_type: str
    condition: str
    description: str
    address: str
    contact_phone: Optional[str] = None

class ReportCreate(ReportBase):
    pass

class ReportUpdate(BaseModel):
    animal_type: Optional[str] = None
    condition: Optional[str] = None
    description: Optional[str] = None
    address: Optional[str] = None
    contact_phone: Optional[str] = None

class ReportStatusUpdate(BaseModel):
    status: ReportStatus

class ReportOut(ReportBase):
    id: int
    status: ReportStatus
    created_at: datetime
    reporter_user_id: Optional[int] = None
    assigned_clinic_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)
