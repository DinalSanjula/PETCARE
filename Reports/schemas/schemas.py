from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field, ConfigDict

from Reports.models.models import ReportStatus

class ReportImageBase(BaseModel):
    image_url: str = Field(
        ...,
        max_length=1000,
        description="stored image URL from MinIO"
    )

class ReportImageCreate(ReportImageBase):
    report_id: int = Field(
        ...,
        description="report id from reports table"
    )

class ReportImageUpdate(BaseModel):
    image_url: Optional[str] = Field(
        None,
        max_length=1000,
        description="updated image URL from MinIO"
    )

class ReportImageResponse(ReportImageBase):
    id: int
    report_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ReportNoteBase(BaseModel):
    note: str = Field(
        ...,
        description="note text for the report"
    )

class ReportNoteCreate(ReportNoteBase):
    pass

class ReportNoteResponse(ReportNoteBase):
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

class ReportResponseBase(ReportBase):
    id: int
    status: ReportStatus
    created_at: datetime
    reporter_user_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)

class ReportResponse(ReportResponseBase):
    images: Optional[List[ReportImageResponse]] = []
    notes: Optional[List[ReportNoteResponse]] = []

    model_config = ConfigDict(from_attributes=True)


class ReportMessageBase(BaseModel):
    message: str

class ReportMessageCreate(ReportMessageBase):
    pass

class ReportMessageResponse(ReportMessageBase):
    id: int
    report_id: int
    sender_user_id: Optional[int] = None
    is_read: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)