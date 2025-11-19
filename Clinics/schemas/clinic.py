from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl, field_validator

from Clinics.schemas.area import AreaResponse
from Clinics.schemas.clinic_image import ClinicImageResponse


class ClinicBase(BaseModel):
    name : str = Field(..., min_length=1, max_length=100, description="Name of the Clinic")
    description : Optional[str] = Field(None, min_length=1, max_length=500, description="A description about the clinic")
    phone : Optional[str] = Field(None, min_length=10, max_length=15, description="Phone number")
    address: Optional[str] = Field(None, min_length=1, max_length=120, description="Address of the clinic")
    profile_pic_url : Optional[HttpUrl] = Field(None, min_length=1, max_length=150, description="Profile photo")
    latitude : Optional[float] = Field(None)
    longitude : Optional[float] = Field(None)
    area_id : Optional[int] = Field(None)

    @field_validator("latitude")
    def latitude_range(cls, l):
        if l is None:
            return l
        if not -90 <= l <= 90:
            raise ValueError("latitude range must be between -90 and 90")
        return l

    @field_validator("longitude")
    def longitude_range(cls, l):
        if l is None:
            return l
        if not -180 <= l <= 180:
            raise ValueError("longitude range must be between -180 and 180")
        return l

class ClinicCreate(ClinicBase):
    owner_id: int = Field(...,description="owner id that came from owner/user table")

class ClinicUpdate(ClinicBase):
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Name of the Clinic")
    description: Optional[str] = Field(None, min_length=1, max_length=500, description="A description about the clinic")
    phone: Optional[str] = Field(None, min_length=10, max_length=15, description="Phone number")
    address: Optional[str] = Field(None, min_length=1, max_length=120, description="Address of the clinic")
    profile_pic_url: Optional[HttpUrl] = Field(None, min_length=1, max_length=150, description="Profile photo")
    latitude: Optional[float] = Field(None)
    longitude: Optional[float] = Field(None)
    area_id: Optional[int] = Field(None)

class ClinicResponse(ClinicBase):
    id : int
    formatted_address : Optional[str] = None
    created_at : datetime
    updated_at : datetime
    is_active : bool
    # area : Optional[AreaResponse] = None
    # images : Optional[ClinicImageResponse] = None

    class Config:
        orm_mode = True