from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field, HttpUrl, field_validator, ConfigDict

from Clinics.schemas.area import AreaResponse
from Clinics.schemas.clinic_image import ClinicImageResponse
from Clinics.schemas.coordinates import Coordinates
from Clinics.schemas.timezone import TimezoneAwareResponse


class ClinicBase(Coordinates, BaseModel):

    name : str = Field(..., min_length=1, max_length=100, description="Name of the Clinic")
    description : Optional[str] = Field(None, min_length=1, max_length=500, description="A description about the clinic")
    phone : Optional[str] = Field(None, min_length=10, max_length=15, description="Phone number")
    address: Optional[str] = Field(None, min_length=1, max_length=120, description="Address of the clinic")
    profile_pic_url : Optional[HttpUrl] = Field(None, min_length=1, max_length=255, description="Profile photo")
    area_id : Optional[int] = Field(None)

    @field_validator("phone")
    def validate_phone(cls, v):
        if v is None:
            return v
        cleared = "".join(ch for ch in v if ch.isdigit())

        if cleared.startswith("+94") and len(cleared) == 11:
            return cleared

        if cleared.startswith("94") and len(cleared) == 11:
            return "+" + cleared

        if cleared.startswith("0") and len(cleared) == 10:
            return "+94" + cleared[1:]

        raise ValueError("Invalid phone number format or length")



class ClinicCreate(ClinicBase):
    pass

class ClinicUpdate(Coordinates, BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Name of the Clinic")
    description: Optional[str] = Field(None, min_length=1, max_length=500, description="A description about the clinic")
    phone: Optional[str] = Field(None, min_length=10, max_length=15, description="Phone number")
    address: Optional[str] = Field(None, min_length=1, max_length=120, description="Address of the clinic")
    profile_pic_url: Optional[HttpUrl] = Field(None, min_length=1, max_length=255, description="Profile photo")
    area_id: Optional[int] = Field(None)

    @field_validator("phone")
    def validate_phone(cls, v):
        if v is None:
            return v
        cleared = "".join(ch for ch in v if ch.isdigit())

        if cleared.startswith("+94") and len(cleared) == 11:
            return cleared

        if cleared.startswith("94") and len(cleared) == 11:
            return "+" + cleared

        if cleared.startswith("0") and len(cleared) == 10:
            return "+94" + cleared[1:]

        raise ValueError("Invalid phone number format or length")


class ClinicResponse(TimezoneAwareResponse,ClinicBase):
    model_config = ConfigDict(from_attributes=True)

    id : int
    owner_id : int
    formatted_address : Optional[str] = None
    geocoded_at : Optional[datetime] = None
    geocode_source : Optional[str] = None
    created_at : datetime
    updated_at : datetime
    is_active : bool
    area : Optional[AreaResponse] = None
    images : Optional[List[ClinicImageResponse]] = None


class ClinicAdminResponse(TimezoneAwareResponse, BaseModel):
    id : int
    name : str
    owner_id : int
    is_active : bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


