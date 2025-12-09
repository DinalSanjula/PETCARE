from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum
from models import ReportStatus


class ReportStatusEnum(str, Enum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"

class ReportBase(BaseModel):
    description: str
    location_lat: Optional[str] = None
    location_lng: Optional[str] = None

class ReportCreate(ReportBase):
    pass

class ReportUpdate(BaseModel):
    status: ReportStatusEnum

class ReportOut(ReportBase):
    id: int
    image_url: Optional[str] = None
    status: ReportStatusEnum
    created_at: datetime

    class Config:
        from_attributes = True
