from datetime import datetime
from typing import Optional
from Clinics.schemas.timezone import TimezoneAwareResponse


from pydantic import BaseModel, Field,HttpUrl, ConfigDict

class ClinicImageBase(BaseModel):
    filename : str = Field(..., max_length=255, description="stored filename")
    original_filename : Optional[str] = Field(None, description="user saved name")
    url : HttpUrl = Field(..., max_length=1000)
    content_type : str = Field(..., max_length=255)

class ClinicImageCreate(ClinicImageBase):
    clinic_id : int = Field(..., description="clinic id from clinic table")

class ClinicImageUpdate(BaseModel):
    filename: Optional[str] = Field(None, max_length=255, description="stored filename")
    original_filename : Optional[str] = Field(None, description="user saved name")
    url: Optional[HttpUrl] = Field(None, max_length=1000)
    content_type: Optional[str] = Field(None, max_length=255)

class ClinicImageResponse(TimezoneAwareResponse, ClinicImageBase):
    model_config = ConfigDict(from_attributes=True)

    id : int
    clinic_id : int
    uploaded_at : datetime
